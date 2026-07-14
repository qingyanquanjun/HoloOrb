"""
分页 & 通用参数解析工具
"""
from flask import request


def get_pagination():
    """从 request.args 中解析 page / page_size，默认第 1 页，每页 10 条"""
    page = max(1, request.args.get('page', 1, type=int))
    per_page = min(200, max(1, request.args.get('page_size', request.args.get('size', 10, type=int), type=int)))
    return page, per_page


def paginate(query, page, per_page, to_dict_fn=None):
    """
    对 SQLAlchemy Query 对象执行分页。
    返回: {
        'items': list[dict],
        'total': int,
        'page': int,
        'page_size': int,
        'pages': int
    }
    """
    p = query.paginate(page=page, per_page=per_page, error_out=False)
    items = []
    for obj in p.items:
        if to_dict_fn is not None:
            items.append(to_dict_fn(obj))
        elif hasattr(obj, 'to_dict'):
            items.append(obj.to_dict())
        else:
            items.append(obj)
    return {
        'items': items,
        'total': p.total,
        'page': p.page,
        'page_size': p.per_page,
        'pages': p.pages,
    }


def arg(name, default=None, cast=None):
    """便捷读取 URL 参数 / JSON body 的合并字段"""
    # 1) URL query
    v = request.args.get(name)
    if v is None and request.is_json:
        # 2) JSON body
        data = request.get_json(silent=True) or {}
        v = data.get(name)
    if v is None or v == '':
        return default
    if cast is not None:
        try:
            return cast(v)
        except (TypeError, ValueError):
            return default
    return v
