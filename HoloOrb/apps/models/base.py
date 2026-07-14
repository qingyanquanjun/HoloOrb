"""
基础模型类
"""
from datetime import datetime
from extensions import db


class Base(db.Model):
    """基础抽象模型"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
