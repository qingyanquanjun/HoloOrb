"""
HoloOrb 后端配置文件
支持 MySQL / SQLite 双模式，通过 DATABASE_URL 切换
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _fix_sqlite_url(url: str) -> str:
    """兼容相对路径的 SQLite URL，并启用外键约束"""
    if url.startswith('sqlite:///') and not url.startswith('sqlite:////'):
        # 把 sqlite:///./xxx.db → sqlite:///<绝对路径>/xxx.db
        rel = url[len('sqlite:///'):]
        if rel.startswith('.'):
            return f"sqlite:///{os.path.join(BASE_DIR, rel[2:] if rel.startswith('./') else rel[1:])}"
    return url


class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'holoorb-dev-secret-key')
    JSON_AS_ASCII = False

    # SQLAlchemy 配置
    _raw_url = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "holoorb.db")}')
    SQLALCHEMY_DATABASE_URI = _fix_sqlite_url(_raw_url)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }

    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'holoorb-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # CORS 配置
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']

    # 默认管理员
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@holoorb.local')

    # DeepSeek API 配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_BASE_URL = os.getenv('DEEPSEEK_API_BASE_URL', 'https://api.deepseek.com')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-v4-flash')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
