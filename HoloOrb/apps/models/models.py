"""
SQLAlchemy ORM 模型 - 按用户提供的 Schema 严格定义
注意：各表时间字段不完全一致（metrics用collected_at，reports用generated_at），
所以不继承公共 Base，避免产生多余的 updated_at 列。
"""
from datetime import datetime
from extensions import db
from sqlalchemy import Index, ForeignKey
from flask_bcrypt import generate_password_hash, check_password_hash


# ------------------------------------------------------------------
# Device 网络设备表
# ------------------------------------------------------------------
class Device(db.Model):
    __tablename__ = 'devices'
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_type', 'type'),
        {'comment': '网络设备表', 'mysql_row_format': 'DYNAMIC'},
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='设备ID')
    name = db.Column(db.String(100), nullable=False, comment='设备名称')
    ip = db.Column(db.String(45), nullable=False, comment='IP地址')
    type = db.Column(db.String(50), nullable=False, comment='设备类型(交换机/路由器/防火墙等)')
    area = db.Column(db.String(100), nullable=True, default='', comment='所属区域')
    status = db.Column(
        db.Enum('online', 'offline', 'warning', 'maintenance', name='device_status'),
        nullable=True, default='online', comment='运行状态',
    )
    description = db.Column(db.Text, nullable=True, comment='设备描述')
    interfaces = db.Column(db.Integer, nullable=True, default=0, comment='接口总数')
    in_use_interfaces = db.Column(db.Integer, nullable=True, default=0, comment='使用中接口数')
    temperature = db.Column(db.String(10), nullable=True, default='', comment='设备温度')
    uptime = db.Column(db.String(50), nullable=True, default='', comment='运行时长')
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now, comment='添加时间')

    # 关系
    alerts = db.relationship('Alert', backref='device', cascade='all, delete-orphan', passive_deletes=True)
    metrics = db.relationship('Metric', backref='device', cascade='all, delete-orphan', passive_deletes=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
            'type': self.type,
            'area': self.area or '',
            'status': self.status,
            'description': self.description or '',
            'interfaces': self.interfaces or 0,
            'in_use_interfaces': self.in_use_interfaces or 0,
            'temperature': self.temperature or '',
            'uptime': self.uptime or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


# ------------------------------------------------------------------
# Alert 告警记录表
# ------------------------------------------------------------------
class Alert(db.Model):
    __tablename__ = 'alerts'
    __table_args__ = (
        Index('idx_created', 'created_at'),
        Index('idx_device_level', 'device_id', 'level'),
        Index('idx_status', 'status'),
        {'comment': '告警记录表', 'mysql_row_format': 'DYNAMIC'},
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='告警ID')
    device_id = db.Column(
        db.Integer,
        ForeignKey('devices.id', ondelete='CASCADE'),
        nullable=False,
        comment='关联设备ID',
    )
    type = db.Column(db.String(50), nullable=False, comment='告警类型(CPU过高/流量异常等)')
    level = db.Column(
        db.Enum('danger', 'warning', 'primary', 'info', name='alert_level'),
        nullable=False, default='warning', comment='告警级别',
    )
    status = db.Column(
        db.Enum('active', 'acknowledged', 'resolved', name='alert_status'),
        nullable=False, default='active', comment='处理状态',
    )
    message = db.Column(db.Text, nullable=True, comment='告警详情')
    handler = db.Column(db.String(50), nullable=True, default='', comment='处理人')
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now, comment='告警时间')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'type': self.type,
            'level': self.level,
            'status': self.status,
            'message': self.message or '',
            'handler': self.handler or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


# ------------------------------------------------------------------
# Metric 监控指标表
# ------------------------------------------------------------------
class Metric(db.Model):
    __tablename__ = 'metrics'
    __table_args__ = (
        Index('idx_device_collected', 'device_id', 'collected_at'),
        {'comment': '监控指标表', 'mysql_row_format': 'DYNAMIC'},
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='指标ID')
    device_id = db.Column(
        db.Integer,
        ForeignKey('devices.id', ondelete='CASCADE'),
        nullable=False,
        comment='所属设备ID',
    )
    cpu = db.Column(db.Float, nullable=True, default=0, comment='CPU使用率(%)')
    memory = db.Column(db.Float, nullable=True, default=0, comment='内存使用率(%)')
    traffic_in = db.Column(db.Float, nullable=True, default=0, comment='入流量(Mbps)')
    traffic_out = db.Column(db.Float, nullable=True, default=0, comment='出流量(Mbps)')
    interface_status = db.Column(db.Text, nullable=True, comment='接口状态(JSON)')
    collected_at = db.Column(db.DateTime, nullable=True, default=datetime.now, comment='采集时间')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'cpu': float(self.cpu or 0),
            'memory': float(self.memory or 0),
            'traffic_in': float(self.traffic_in or 0),
            'traffic_out': float(self.traffic_out or 0),
            'interface_status': self.interface_status or '',
            'collected_at': self.collected_at.strftime('%Y-%m-%d %H:%M:%S') if self.collected_at else None,
        }


# ------------------------------------------------------------------
# Report 分析报告表
# ------------------------------------------------------------------
class Report(db.Model):
    __tablename__ = 'reports'
    __table_args__ = (
        Index('idx_type_time', 'type', 'generated_at'),
        {'comment': '分析报告表', 'mysql_row_format': 'DYNAMIC'},
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='报告ID')
    type = db.Column(db.Enum('日报', '周报', '月报', name='report_type'), nullable=False, comment='报告类型')
    title = db.Column(db.String(200), nullable=False, comment='报告标题')
    content = db.Column(db.Text, nullable=True, comment='报告内容')
    status = db.Column(db.String(20), nullable=True, default='generated', comment='生成状态')
    generated_at = db.Column(db.DateTime, nullable=True, default=datetime.now, comment='生成时间')

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'content': self.content or '',
            'status': self.status or 'generated',
            'generated_at': self.generated_at.strftime('%Y-%m-%d %H:%M:%S') if self.generated_at else None,
        }


# ------------------------------------------------------------------
# User 用户表
# ------------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        Index('idx_username', 'username'),
        {'comment': '用户表', 'mysql_row_format': 'DYNAMIC'},
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(50), nullable=False, unique=True, comment='用户名')
    password_hash = db.Column(db.String(200), nullable=False, comment='密码哈希(bcrypt)')
    role = db.Column(
        db.Enum('管理员', '运维工程师', '普通用户', name='user_role'),
        nullable=False, default='普通用户', comment='角色',
    )
    email = db.Column(db.String(100), nullable=True, default='', comment='邮箱')
    status = db.Column(
        db.Enum('active', 'disabled', name='user_status'),
        nullable=True, default='active', comment='状态',
    )
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now, comment='创建时间')

    # 关系
    logs = db.relationship('OpLog', backref='user')

    def set_password(self, raw_password: str):
        """设置 bcrypt 密码哈希"""
        self.password_hash = generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password: str) -> bool:
        try:
            return check_password_hash(self.password_hash, raw_password)
        except Exception:
            return False

    def to_dict(self, include_sensitive=False):
        d = {
            'id': self.id,
            'username': self.username,
            'name': self.username,
            'role': self.role,
            'email': self.email or '',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
        if include_sensitive:
            d['password_hash'] = self.password_hash
        return d


# ------------------------------------------------------------------
# OpLog 操作日志表
# ------------------------------------------------------------------
class OpLog(db.Model):
    __tablename__ = 'logs'
    __table_args__ = (
        Index('idx_user_time', 'user_id', 'created_at'),
        {'comment': '操作日志表', 'mysql_row_format': 'DYNAMIC'},
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='日志ID')
    user_id = db.Column(
        db.Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        comment='操作用户ID',
    )
    action = db.Column(db.String(100), nullable=False, comment='操作类型')
    # 注意：用户提供的 schema 中 detail 为操作详情；额外加一个 module 字段存在后端 JSON 化到 detail 中，
    # 为了严格兼容我们在 detail 中存 {module, detail} 结构，也提供 property 方便使用。
    detail = db.Column(db.Text, nullable=True, comment='操作详情')
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now, comment='操作时间')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action': self.action,
            'detail': self.detail or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
