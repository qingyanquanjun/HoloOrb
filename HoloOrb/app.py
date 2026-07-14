import os
from flask import Flask

from config import config
from extensions import db, jwt, cors, bcrypt


def create_app(config_name: str = None) -> Flask:
    """应用工厂函数"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # 确保 instance 目录存在
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, dict):
            return str(user['id'])
        return str(user)
    cors.init_app(app, resources={
        r'/api/*': {
            'origins': app.config.get('CORS_ORIGINS', '*'),
            'supports_credentials': True
        }
    })

    # 注册蓝图
    from apps.api import api_bp
    app.register_blueprint(api_bp)

    # 根路由
    @app.route('/')
    def index():
        return {
            'name': 'HoloOrb Backend API',
            'version': '1.0.0',
            'docs': '/api/health',
            'endpoints': [
                'GET  /api/health   - 健康检查',
                'GET  /api/hello    - 示例 GET 接口',
                'POST /api/echo     - 示例 POST 接口'
            ]
        }

    # 初始化数据库表和默认管理员
    with app.app_context():
        db.create_all()

        # 检查并创建默认管理员
        from apps.models import User
        admin_user = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
        if not admin_user:
            admin_user = User(
                username=app.config['ADMIN_USERNAME'],
                password_hash='',
                role='管理员',
                email=app.config['ADMIN_EMAIL'],
                status='active'
            )
            admin_user.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin_user)
            db.session.commit()
            print(f"Created default admin user: {app.config['ADMIN_USERNAME']}")
        else:
            print(f"Admin user {app.config['ADMIN_USERNAME']} already exists")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
