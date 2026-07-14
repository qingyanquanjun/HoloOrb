"""
API 路由包 - 注册所有蓝图到 /api 前缀下
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

dashboard_bp = Blueprint('dashboard', __name__)
devices_bp = Blueprint('devices', __name__)
alerts_bp = Blueprint('alerts', __name__)
metrics_bp = Blueprint('metrics', __name__)
reports_bp = Blueprint('reports', __name__)
auth_bp = Blueprint('auth', __name__)
users_bp = Blueprint('users', __name__)
logs_bp = Blueprint('logs', __name__)
insight_bp = Blueprint('insight', __name__)

from apps.api import health, example  # noqa: E402,F401
from apps.api import dashboard, devices, alerts, metrics, reports, auth, logs, insight  # noqa: E402

api_bp.register_blueprint(dashboard_bp, url_prefix='/dashboard')
api_bp.register_blueprint(devices_bp, url_prefix='/devices')
api_bp.register_blueprint(alerts_bp, url_prefix='/alerts')
api_bp.register_blueprint(metrics_bp, url_prefix='/metrics')
api_bp.register_blueprint(reports_bp, url_prefix='/reports')
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(users_bp, url_prefix='/users')
api_bp.register_blueprint(logs_bp, url_prefix='/logs')
api_bp.register_blueprint(insight_bp, url_prefix='/insight')