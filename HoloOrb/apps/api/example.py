"""
示例路由 - 演示 API 结构
"""
from flask import jsonify, request
from apps.api import api_bp


@api_bp.route('/hello', methods=['GET'])
def hello():
    """示例 GET 接口"""
    name = request.args.get('name', 'World')
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'greeting': f'Hello, {name}!',
            'project': 'HoloOrb'
        }
    })


@api_bp.route('/echo', methods=['POST'])
def echo():
    """示例 POST 接口 - 回显请求体"""
    data = request.get_json(silent=True) or {}
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'received': data,
            'keys': list(data.keys())
        }
    })
