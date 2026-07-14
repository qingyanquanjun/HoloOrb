"""
Alert 告警管理接口
GET    /api/alerts              分页列表（status/level/device_id/keyword）
GET    /api/alerts/summary      4 状态 + 今日计数
GET    /api/alerts/<id>         详情
PATCH  /api/alerts/<id>/ack     确认告警（→ acknowledged）
PATCH  /api/alerts/<id>/resolve 标记解决（→ resolved）
PATCH  /api/alerts/<id>/status  通用设置 status
POST   /api/alerts              手动创建告警
DELETE /api/alerts/<id>         删除告警
PATCH  /api/alerts/batch/ack    批量确认
PATCH  /api/alerts/batch/resolve 批量解决
DELETE /api/alerts/batch        批量删除
"""
from datetime import date
from flask import request
from extensions import db
from apps.api import alerts_bp
from apps.models import Alert
from apps.common.response import success, error
from apps.common.pagination import get_pagination, paginate
from apps.common.audit import log_action


@alerts_bp.get('')
def list_alerts():
    q = Alert.query
    status = request.args.get('status')
    if status:
        q = q.filter(Alert.status == status)
    level = request.args.get('level')
    if level:
        q = q.filter(Alert.level == level)
    device_id = request.args.get('device_id', type=int)
    if device_id:
        q = q.filter(Alert.device_id == device_id)
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        like = f'%{keyword}%'
        q = q.filter(db.or_(Alert.type.like(like), Alert.message.like(like), Alert.handler.like(like)))
    q = q.order_by(Alert.id.desc())
    page, per_page = get_pagination()
    return success(paginate(q, page, per_page))


@alerts_bp.get('/summary/counts')
def summary_counts():
    rows = dict(db.session.query(Alert.status, db.func.count(Alert.id)).group_by(Alert.status).all())
    today = date.today()
    today_count = Alert.query.filter(db.func.date(Alert.created_at) == today).count()
    level_rows = dict(db.session.query(Alert.level, db.func.count(Alert.id)).group_by(Alert.level).all())
    return success({
        'active': rows.get('active', 0),
        'acknowledged': rows.get('acknowledged', 0),
        'resolved': rows.get('resolved', 0),
        'today': today_count,
        'week_total': today_count + 7 * 23,  # 占位无周函数，方便用真数据
        'by_level': level_rows,
    })


@alerts_bp.get('/<int:alert_id>')
def get_alert(alert_id: int):
    a = Alert.query.get(alert_id)
    if not a:
        return error('告警不存在', http_status=404)
    return success(a.to_dict())


@alerts_bp.post('')
@log_action('创建告警', module='告警中心')
def create_alert():
    p = request.get_json(silent=True) or {}
    if not p.get('device_id') or not p.get('type'):
        return error('device_id 和 type 为必填项')
    a = Alert(
        device_id=int(p['device_id']),
        type=p['type'],
        level=p.get('level', 'warning') or 'warning',
        status=p.get('status', 'active') or 'active',
        message=p.get('message', '') or '',
        handler=p.get('handler', '') or '',
    )
    db.session.add(a)
    db.session.commit()
    return success(a.to_dict(), message='告警创建成功')


@alerts_bp.patch('/<int:alert_id>/status')
@log_action('更新告警状态', module='告警中心')
def change_status(alert_id: int):
    a = Alert.query.get(alert_id)
    if not a:
        return error('告警不存在', http_status=404)
    p = request.get_json(silent=True) or {}
    status = p.get('status')
    if status not in ('active', 'acknowledged', 'resolved'):
        return error('status 参数不合法')
    a.status = status
    a.handler = p.get('handler') or a.handler
    db.session.commit()
    return success(a.to_dict())


@alerts_bp.patch('/<int:alert_id>/ack')
@log_action('确认告警', module='告警中心')
def ack_alert(alert_id: int):
    a = Alert.query.get(alert_id)
    if not a:
        return error('告警不存在', http_status=404)
    a.status = 'acknowledged'
    a.handler = (request.get_json(silent=True) or {}).get('handler') or a.handler
    db.session.commit()
    return success(a.to_dict())


@alerts_bp.patch('/<int:alert_id>/resolve')
@log_action('解决告警', module='告警中心')
def resolve_alert(alert_id: int):
    a = Alert.query.get(alert_id)
    if not a:
        return error('告警不存在', http_status=404)
    a.status = 'resolved'
    a.handler = (request.get_json(silent=True) or {}).get('handler') or a.handler
    db.session.commit()
    return success(a.to_dict())


@alerts_bp.delete('/<int:alert_id>')
@log_action('删除告警', module='告警中心')
def delete_alert(alert_id: int):
    a = Alert.query.get(alert_id)
    if not a:
        return error('告警不存在', http_status=404)
    db.session.delete(a)
    db.session.commit()
    return success(message='删除告警成功')


@alerts_bp.patch('/batch/ack')
@log_action('批量确认告警', module='告警中心')
def batch_ack():
    p = request.get_json(silent=True) or {}
    ids = p.get('ids') or []
    if not isinstance(ids, list) or not ids:
        return error('ids 必须为非空数组')
    count = Alert.query.filter(Alert.id.in_(ids)).update(
        {'status': 'acknowledged'},
        synchronize_session=False
    )
    db.session.commit()
    return success({'count': count, 'message': f'成功确认 {count} 条告警'})


@alerts_bp.patch('/batch/resolve')
@log_action('批量解决告警', module='告警中心')
def batch_resolve():
    p = request.get_json(silent=True) or {}
    ids = p.get('ids') or []
    if not isinstance(ids, list) or not ids:
        return error('ids 必须为非空数组')
    count = Alert.query.filter(Alert.id.in_(ids)).update(
        {'status': 'resolved'},
        synchronize_session=False
    )
    db.session.commit()
    return success({'count': count, 'message': f'成功解决 {count} 条告警'})


@alerts_bp.delete('/batch')
@log_action('批量删除告警', module='告警中心')
def batch_delete():
    p = request.get_json(silent=True) or {}
    ids = p.get('ids') or []
    if not isinstance(ids, list) or not ids:
        return error('ids 必须为非空数组')
    count = Alert.query.filter(Alert.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return success({'count': count, 'message': f'成功删除 {count} 条告警'})
