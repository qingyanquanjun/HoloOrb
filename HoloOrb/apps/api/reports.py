"""
Report 报告中心接口
GET    /api/reports            列表（按 type/status 过滤 + 时间范围）
GET    /api/reports/<id>       详情
POST   /api/reports            创建报告（支持生成中/已完成）
PATCH  /api/reports/<id>       更新内容/状态
DELETE /api/reports/<id>       删除
"""
from datetime import datetime
from flask import request
from extensions import db
from apps.api import reports_bp
from apps.models import Report
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


@reports_bp.get('')
def list_reports():
    q = Report.query
    type_ = request.args.get('type')
    if type_:
        q = q.filter(Report.type == type_)
    status = request.args.get('status')
    if status:
        q = q.filter(Report.status == status)
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        q = q.filter(Report.title.like(f'%{keyword}%'))
    start = _parse_dt(request.args.get('start'))
    end = _parse_dt(request.args.get('end'))
    if start:
        q = q.filter(Report.generated_at >= start)
    if end:
        q = q.filter(Report.generated_at <= end)
    q = q.order_by(Report.id.desc())
    page, per_page = get_pagination()
    return success(paginate(q, page, per_page))


@reports_bp.get('/<int:report_id>')
def get_report(report_id: int):
    r = Report.query.get(report_id)
    if not r:
        return error('报告不存在', http_status=404)
    return success(r.to_dict())


@reports_bp.post('')
@log_action('生成报告', module='报表中心')
def create_report():
    p = request.get_json(silent=True) or {}
    if not p.get('type') or not p.get('title'):
        return error('type 和 title 为必填项')
    if p['type'] not in ('日报', '周报', '月报', '专项报告'):
        return error('type 只允许：日报/周报/月报/专项报告')
    r = Report(
        type=p['type'],
        title=p['title'],
        content=p.get('content', '') or '',
        status=p.get('status', 'generated') or 'generated',
    )
    db.session.add(r)
    db.session.commit()
    return success(r.to_dict(), message='报告创建成功')


@reports_bp.patch('/<int:report_id>')
@log_action('更新报告', module='报表中心')
def update_report(report_id: int):
    r = Report.query.get(report_id)
    if not r:
        return error('报告不存在', http_status=404)
    p = request.get_json(silent=True) or {}
    for k in ('title', 'content', 'status', 'type'):
        if k in p and p[k] is not None:
            setattr(r, k, p[k])
    db.session.commit()
    return success(r.to_dict())


@reports_bp.delete('/<int:report_id>')
@log_action('删除报告', module='报表中心')
def delete_report(report_id: int):
    r = Report.query.get(report_id)
    if not r:
        return error('报告不存在', http_status=404)
    db.session.delete(r)
    db.session.commit()
    return success(message='报告删除成功')
