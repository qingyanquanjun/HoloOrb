"""
Dashboard 仪表盘聚合统计接口（真实落库数据聚合）
GET /api/dashboard/overview     顶部 4 个卡片：在线设备/今日告警/平均CPU/网络健康度
GET /api/dashboard/cpu-memory   CPU/内存 24h 趋势（聚合所有设备，按小时平均）
GET /api/dashboard/traffic      流量 24h 趋势（入/出合计）
GET /api/dashboard/devices-by-type  设备类型饼图
GET /api/dashboard/recent-alarms    最近 N 条告警（默认 20 条）
"""
from datetime import datetime, timedelta, date
from flask import request
from extensions import db
from apps.api import dashboard_bp
from apps.models import Device, Alert, Metric
from apps.common.response import success


def _trend_q(days=1):
    since = datetime.now() - timedelta(days=days)
    engine = str(db.engine.url).lower()
    if 'mysql' in engine:
        return db.func.date_format(Metric.collected_at, '%Y-%m-%d %H:00')
    return db.func.strftime('%Y-%m-%d %H:00', Metric.collected_at), since


@dashboard_bp.get('/overview')
def overview():
    total_devices = Device.query.count()
    online_devices = Device.query.filter(Device.status == 'online').count()
    today = date.today()
    today_alerts = Alert.query.filter(db.func.date(Alert.created_at) == today).count()

    # CPU 均值（所有设备最近一条）
    latest = (
        db.session.query(
            Metric.device_id,
            db.func.max(Metric.collected_at).label('mx'),
        )
        .group_by(Metric.device_id)
        .subquery()
    )
    avg_cpu = (
        db.session.query(
            db.func.round(db.func.avg(Metric.cpu), 2),
            db.func.round(db.func.avg(Metric.memory), 2),
            db.func.round(db.func.avg(Metric.traffic_in), 2),
            db.func.round(db.func.avg(Metric.traffic_out), 2),
        )
        .join(latest, db.and_(Metric.device_id == latest.c.device_id, Metric.collected_at == latest.c.mx))
        .first()
    ) or (0, 0, 0, 0)
    avg_cpu_v, avg_mem_v, avg_in_v, avg_out_v = [float(x or 0) for x in avg_cpu]

    # 网络健康度 = 1 - (warning+offline+maintenance 占比)
    if total_devices:
        bad = Device.query.filter(Device.status.in_(['offline', 'warning', 'maintenance'])).count()
        health = round(max(0.0, 100.0 * (1 - bad / total_devices)), 2)
    else:
        health = 100.0

    return success({
        'online_devices': online_devices,
        'total_devices': total_devices,
        'today_alerts': today_alerts,
        'avg_cpu': avg_cpu_v,
        'avg_memory': avg_mem_v,
        'avg_traffic_in': avg_in_v,
        'avg_traffic_out': avg_out_v,
        'network_health': health,
    })


@dashboard_bp.get('/cpu-memory')
def cpu_memory_trend():
    hours = request.args.get('hours', 24, type=int)
    since = datetime.now() - timedelta(hours=int(hours))
    engine = str(db.engine.url).lower()
    if 'mysql' in engine:
        time_col = db.func.date_format(Metric.collected_at, '%Y-%m-%d %H:00')
    else:
        time_col = db.func.strftime('%Y-%m-%d %H:00', Metric.collected_at)

    rows = (
        db.session.query(
            time_col.label('t'),
            db.func.round(db.func.avg(Metric.cpu), 2).label('cpu'),
            db.func.round(db.func.avg(Metric.memory), 2).label('memory'),
        )
        .filter(Metric.collected_at >= since)
        .group_by('t')
        .order_by('t')
        .all()
    )
    return success({
        'hours': hours,
        'timeline': [r.t for r in rows],
        'cpu': [float(r.cpu or 0) for r in rows],
        'memory': [float(r.memory or 0) for r in rows],
    })


@dashboard_bp.get('/traffic')
def traffic_trend():
    hours = request.args.get('hours', 24, type=int)
    since = datetime.now() - timedelta(hours=int(hours))
    engine = str(db.engine.url).lower()
    if 'mysql' in engine:
        time_col = db.func.date_format(Metric.collected_at, '%Y-%m-%d %H:00')
    else:
        time_col = db.func.strftime('%Y-%m-%d %H:00', Metric.collected_at)

    rows = (
        db.session.query(
            time_col.label('t'),
            db.func.round(db.func.sum(Metric.traffic_in), 2).label('inbound'),
            db.func.round(db.func.sum(Metric.traffic_out), 2).label('outbound'),
        )
        .filter(Metric.collected_at >= since)
        .group_by('t')
        .order_by('t')
        .all()
    )
    return success({
        'hours': hours,
        'timeline': [r.t for r in rows],
        'inbound': [float(r.inbound or 0) for r in rows],
        'outbound': [float(r.outbound or 0) for r in rows],
    })


@dashboard_bp.get('/devices-by-type')
def devices_by_type():
    rows = (
        db.session.query(Device.type, db.func.count(Device.id).label('c'))
        .group_by(Device.type)
        .all()
    )
    return success([{'type': r.type, 'value': int(r.c or 0)} for r in rows])


@dashboard_bp.get('/recent-alarms')
def recent_alarms():
    limit = min(200, request.args.get('limit', 20, type=int))
    items = Alert.query.order_by(Alert.id.desc()).limit(int(limit)).all()
    return success([a.to_dict() for a in items])
