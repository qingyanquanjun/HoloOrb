"""
健康检查路由
"""
from flask import jsonify
from datetime import datetime

from apps.api import api_bp


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'code': 0,
        'message': 'ok',
        'data': {
            'status': 'healthy',
            'service': 'HoloOrb API',
            'timestamp': datetime.now().isoformat()
        }
    })
