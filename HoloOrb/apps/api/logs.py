"""
OpLog 操作日志接口
GET /api/logs          分页列表（user_id/action/start/end 过滤）
GET /api/logs/<id>     日志详情
"""
from flask import request
from extensions import db
from apps.api import logs_bp
from apps.models import OpLog
from apps.common.response import success, error
from apps.common.pagination import get_pagination, paginate


def _parse_dt(s):
    if not s:
        return None
    try:
        from datetime import datetime
        return datetime.fromisoformat(str(s).replace('Z', ''))
    except Exception:
        return None


@logs_bp.get('')
def list_logs():
    q = OpLog.query
    user_id = request.args.get('user_id', type=int)
    if user_id:
        q = q.filter(OpLog.user_id == user_id)
    username = request.args.get('username', '').strip()
    if username:
        from apps.models import User
        sub = db.session.query(User.id).filter(User.username.like(f'%{username}%')).subquery()
        q = q.filter(OpLog.user_id.in_(sub))
    action = request.args.get('action', '').strip()
    if action:
        q = q.filter(OpLog.action.like(f'%{action}%'))
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        q = q.filter(OpLog.detail.like(f'%{keyword}%'))
    start, end = _parse_dt(request.args.get('start')), _parse_dt(request.args.get('end'))
    if start:
        q = q.filter(OpLog.created_at >= start)
    if end:
        q = q.filter(OpLog.created_at <= end)
    q = q.order_by(OpLog.id.desc())
    page, per_page = get_pagination()
    return success(paginate(q, page, per_page))


@logs_bp.get('/<int:log_id>')
def get_log(log_id: int):
    log = OpLog.query.get(log_id)
    if not log:
        return error('日志不存在', http_status=404)
    return success(log.to_dict())
