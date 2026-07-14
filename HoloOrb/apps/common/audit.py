"""
操作日志辅助装饰器
"""
from functools import wraps
from extensions import db
from apps.models import OpLog
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def log_action(action: str, module: str = None, detail_extractor=None):
    """
    记录操作日志的装饰器：
    - action: 操作描述，如 "新增设备"
    - module: 模块名，如 "设备管理"
    - detail_extractor: 可选 function(response_data, *args, **kwargs) -> str，默认写入响应 JSON 摘要
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            resp = fn(*args, **kwargs)
            user_id = None
            try:
                verify_jwt_in_request(locations=['headers', 'cookies', 'json', 'query_string'], optional=True)
                uid = get_jwt_identity()
                if isinstance(uid, (int, str)) and str(uid).isdigit():
                    user_id = int(uid)
                elif isinstance(uid, dict):
                    user_id = uid.get('id')
            except Exception:
                pass
            try:
                detail = ''
                if isinstance(resp, tuple):
                    data = resp[0]
                else:
                    data = resp
                if detail_extractor:
                    detail = detail_extractor(data, *args, **kwargs) or ''
                elif hasattr(data, 'get_json'):
                    d = data.get_json(silent=True)
                    detail = f'{module or ""} {action} => {str(d)[:500]}'
                else:
                    detail = f'{module or ""} {action}'
                log = OpLog(user_id=user_id, action=action, detail=detail[:4000])
                db.session.add(log)
                db.session.commit()
            except Exception:
                db.session.rollback()
            return resp
        return wrapper
    return decorator
