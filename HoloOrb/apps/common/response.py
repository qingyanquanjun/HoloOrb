"""
统一响应格式工具
"""
from flask import jsonify
from typing import Any, Optional

def success(data: Any = None, message: str = 'success', code: int = 0):
    """成功响应"""
    response = {
        'code': code,
        'message': message,
        'data': data
    }
    return jsonify(response)


def error(message: str = 'error', code: int = -1, data: Optional[Any] = None, http_status: int = 400):
    """错误响应"""
    response = {
        'code': code,
        'message': message,
        'data': data
    }
    return jsonify(response), http_status
