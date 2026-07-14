"""
Device 设备管理接口
GET      /api/devices              列表（支持按 status/type/keyword/area 过滤 + 分页）
GET      /api/devices/<id>         详情
POST     /api/devices              新增
PUT      /api/devices/<id>         更新
DELETE   /api/devices/<id>         删除
PATCH    /api/devices/<id>/status  修改状态
GET      /api/devices/summary      各类型/状态统计
"""
from flask import request
from extensions import db
from apps.api import devices_bp
from apps.models import Device, Alert, Metric
from apps.common.response import success, error
from apps.common.pagination import get_pagination, paginate
from apps.common.audit import log_action


@devices_bp.get('')
def list_devices():
    q = Device.query
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        like = f'%{keyword}%'
        q = q.filter(db.or_(Device.name.like(like), Device.ip.like(like), Device.area.like(like)))
    status = request.args.get('status')
    if status:
        q = q.filter(Device.status == status)
    type_ = request.args.get('type')
    if type_:
        q = q.filter(Device.type == type_)
    area = request.args.get('area')
    if area:
        q = q.filter(Device.area.like(f'%{area}%'))
    q = q.order_by(Device.id.desc())
    page, per_page = get_pagination()
    return success(paginate(q, page, per_page))


@devices_bp.get('/<int:device_id>')
def get_device(device_id: int):
    d = Device.query.get(device_id)
    if not d:
        return error('设备不存在', http_status=404)
    data = d.to_dict()
    # 附带设备最新指标
    latest = Metric.query.filter_by(device_id=d.id).order_by(Metric.collected_at.desc()).first()
    data['latest_metric'] = latest.to_dict() if latest else None
    # 附带最近告警数
    data['active_alerts'] = Alert.query.filter_by(device_id=d.id, status='active').count()
    return success(data)


@devices_bp.post('')
@log_action('新增设备', module='设备管理')
def create_device():
    payload = request.get_json(silent=True) or {}
    required = ['name', 'ip', 'type']
    for k in required:
        if not payload.get(k):
            return error(f'字段 {k} 为必填项')
    d = Device(
        name=payload['name'].strip(),
        ip=payload['ip'].strip(),
        type=payload['type'].strip(),
        area=payload.get('area', '') or '',
        status=payload.get('status', 'online') or 'online',
        description=payload.get('description', '') or '',
        interfaces=int(payload.get('interfaces', 0) or 0),
        in_use_interfaces=int(payload.get('in_use_interfaces', 0) or 0),
        temperature=payload.get('temperature', '') or '',
        uptime=payload.get('uptime', '') or '',
    )
    db.session.add(d)
    db.session.commit()
    return success(d.to_dict(), message='创建设备成功')


@devices_bp.put('/<int:device_id>')
@log_action('更新设备', module='设备管理')
def update_device(device_id: int):
    d = Device.query.get(device_id)
    if not d:
        return error('设备不存在', http_status=404)
    payload = request.get_json(silent=True) or {}
    fields = ['name', 'ip', 'type', 'area', 'status', 'description', 'temperature', 'uptime']
    for f in fields:
        if f in payload and payload[f] is not None:
            setattr(d, f, payload[f])
    for f in ['interfaces', 'in_use_interfaces']:
        if f in payload and payload[f] is not None:
            setattr(d, f, int(payload[f]))
    db.session.commit()
    return success(d.to_dict(), message='更新设备成功')


@devices_bp.patch('/<int:device_id>/status')
@log_action('更新设备状态', module='设备管理')
def update_status(device_id: int):
    d = Device.query.get(device_id)
    if not d:
        return error('设备不存在', http_status=404)
    payload = request.get_json(silent=True) or {}
    status = payload.get('status')
    if status not in ('online', 'offline', 'warning', 'maintenance'):
        return error('status 参数不合法')
    d.status = status
    db.session.commit()
    return success({'id': d.id, 'status': d.status})


@devices_bp.delete('/<int:device_id>')
@log_action('删除设备', module='设备管理')
def delete_device(device_id: int):
    d = Device.query.get(device_id)
    if not d:
        return error('设备不存在', http_status=404)
    db.session.delete(d)
    db.session.commit()
    return success(message='删除设备成功')


@devices_bp.get('/summary/counts')
def summary_counts():
    total = Device.query.count()
    status_counts = dict(
        db.session.query(Device.status, db.func.count(Device.id))
        .group_by(Device.status).all()
    )
    type_counts = dict(
        db.session.query(Device.type, db.func.count(Device.id))
        .group_by(Device.type).all()
    )
    area_counts = dict(
        db.session.query(Device.area, db.func.count(Device.id))
        .filter(Device.area != '')
        .group_by(Device.area).all()
    )
    return success({
        'total': total,
        'by_status': status_counts,
        'by_type': type_counts,
        'by_area': area_counts,
    })


@devices_bp.get('/areas')
def list_areas():
    areas = db.session.query(Device.area).filter(Device.area != '').distinct().all()
    return success([a[0] for a in areas])
