"""
Metric 监控指标接口
GET  /api/metrics                       分页列表（device_id/start/end 过滤）
GET  /api/metrics/latest                所有设备最新一条指标
GET  /api/metrics/<device_id>/latest    指定设备最新指标
GET  /api/metrics/<device_id>/trend     指定设备 N 小时趋势（默认24h）
POST /api/metrics                       上报一条指标（兼容采集器）
POST /api/metrics/batch                 批量上报
"""
from datetime import datetime, timedelta
from flask import request
from extensions import db
from apps.api import metrics_bp
from apps.models import Metric, Device
from apps.common.response import success, error
from apps.common.pagination import get_pagination, paginate
from apps.common.audit import log_action


def _parse_dt(s, default=None):
    if not s:
        return default
    try:
        return datetime.fromisoformat(str(s).replace('Z', ''))
    except (ValueError, TypeError):
        return default


@metrics_bp.get('')
def list_metrics():
    q = Metric.query
    device_id = request.args.get('device_id', type=int)
    if device_id:
        q = q.filter(Metric.device_id == device_id)
    start = _parse_dt(request.args.get('start'))
    end = _parse_dt(request.args.get('end'))
    if start:
        q = q.filter(Metric.collected_at >= start)
    if end:
        q = q.filter(Metric.collected_at <= end)
    q = q.order_by(Metric.collected_at.desc(), Metric.id.desc())
    page, per_page = get_pagination()
    return success(paginate(q, page, per_page))


@metrics_bp.get('/latest/all')
def latest_all():
    """各设备最新一条指标（子查询取最大collected_at对应设备id）"""
    sub = (
        db.session.query(
            Metric.device_id,
            db.func.max(Metric.collected_at).label('mx'),
        )
        .group_by(Metric.device_id)
        .subquery()
    )
    q = (
        Metric.query
        .join(sub, db.and_(Metric.device_id == sub.c.device_id, Metric.collected_at == sub.c.mx))
        .order_by(Metric.device_id.asc())
    )
    items = [m.to_dict() for m in q.all()]
    return success({'items': items, 'total': len(items)})


@metrics_bp.get('/<int:device_id>/latest')
def latest_one(device_id: int):
    if not Device.query.get(device_id):
        return error('设备不存在', http_status=404)
    m = Metric.query.filter_by(device_id=device_id).order_by(Metric.collected_at.desc()).first()
    return success(m.to_dict() if m else None)


@metrics_bp.get('/<int:device_id>/trend')
def device_trend(device_id: int):
    """
    趋势接口：返回 按小时/分钟聚合的 cpu/memory/traffic_in/traffic_out 序列
    Query:
      - hours: 回退小时数，默认 24
      - bucket: 聚合粒度 'hour' | 'minute'，默认 hour
    """
    if not Device.query.get(device_id):
        return error('设备不存在', http_status=404)
    hours = request.args.get('hours', 24, type=int)
    bucket = request.args.get('bucket', 'hour')
    since = datetime.now() - timedelta(hours=int(hours))

    q = Metric.query.filter(Metric.device_id == device_id, Metric.collected_at >= since)

    # SQLite 与 MySQL 函数统一：通过 func 兼容
    if bucket == 'minute':
        time_col = db.func.date_format(Metric.collected_at, '%Y-%m-%d %H:%i') if 'mysql' in str(db.engine.url).lower() \
            else db.func.strftime('%Y-%m-%d %H:%M', Metric.collected_at)
    else:
        time_col = db.func.date_format(Metric.collected_at, '%Y-%m-%d %H:00') if 'mysql' in str(db.engine.url).lower() \
            else db.func.strftime('%Y-%m-%d %H:00', Metric.collected_at)

    rows = (
        db.session.query(
            time_col.label('t'),
            db.func.round(db.func.avg(Metric.cpu), 2).label('cpu'),
            db.func.round(db.func.avg(Metric.memory), 2).label('memory'),
            db.func.round(db.func.avg(Metric.traffic_in), 2).label('traffic_in'),
            db.func.round(db.func.avg(Metric.traffic_out), 2).label('traffic_out'),
            db.func.count(Metric.id).label('cnt'),
        )
        .filter(Metric.device_id == device_id, Metric.collected_at >= since)
        .group_by('t')
        .order_by('t')
        .all()
    )
    return success({
        'device_id': device_id,
        'bucket': bucket,
        'hours': hours,
        'timeline': [r.t for r in rows],
        'cpu': [float(r.cpu or 0) for r in rows],
        'memory': [float(r.memory or 0) for r in rows],
        'traffic_in': [float(r.traffic_in or 0) for r in rows],
        'traffic_out': [float(r.traffic_out or 0) for r in rows],
        'counts': [int(r.cnt or 0) for r in rows],
    })


@metrics_bp.post('')
@log_action('上报指标', module='监控指标')
def create_metric():
    p = request.get_json(silent=True) or {}
    if not p.get('device_id'):
        return error('device_id 为必填项')
    if not Device.query.get(int(p['device_id'])):
        return error('device_id 对应的设备不存在')
    m = Metric(
        device_id=int(p['device_id']),
        cpu=float(p.get('cpu', 0) or 0),
        memory=float(p.get('memory', 0) or 0),
        traffic_in=float(p.get('traffic_in', 0) or 0),
        traffic_out=float(p.get('traffic_out', 0) or 0),
        interface_status=p.get('interface_status') or '',
        collected_at=_parse_dt(p.get('collected_at'), datetime.now()),
    )
    db.session.add(m)
    db.session.commit()
    return success(m.to_dict(), message='指标上报成功')


@metrics_bp.post('/batch')
def batch_create():
    p = request.get_json(silent=True) or {}
    items = p.get('items') or []
    if not isinstance(items, list) or not items:
        return error('items 必须为非空数组')
    ok = 0
    errs = []
    for idx, it in enumerate(items):
        try:
            if not it.get('device_id'):
                raise ValueError('缺少 device_id')
            if not Device.query.get(int(it['device_id'])):
                raise ValueError('设备不存在')
            m = Metric(
                device_id=int(it['device_id']),
                cpu=float(it.get('cpu', 0) or 0),
                memory=float(it.get('memory', 0) or 0),
                traffic_in=float(it.get('traffic_in', 0) or 0),
                traffic_out=float(it.get('traffic_out', 0) or 0),
                interface_status=it.get('interface_status') or '',
                collected_at=_parse_dt(it.get('collected_at'), datetime.now()),
            )
            db.session.add(m)
            ok += 1
        except Exception as e:  # noqa: BLE001
            errs.append({'index': idx, 'error': str(e)})
    db.session.commit()
    return success({'success': ok, 'failed': len(errs), 'errors': errs})
