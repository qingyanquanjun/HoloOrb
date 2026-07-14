"""
HoloOrb 后端扩展模块
集中初始化 Flask 扩展，避免循环导入
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()
bcrypt = Bcrypt()
