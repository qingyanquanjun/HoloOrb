"""
User + Auth 接口

Auth 登录相关：
POST  /api/auth/login           账号密码登录 → 返回 access_token / refresh_token
POST  /api/auth/refresh         刷新 access_token
POST  /api/auth/register        管理员或开放注册

User CRUD：
GET    /api/users                分页列表（username/role/status 过滤）
GET    /api/users/<id>           详情
POST   /api/users                新建（密码明文传入自动加密）
PUT    /api/users/<id>           更新资料
PATCH  /api/users/<id>/password  重置密码
PATCH  /api/users/<id>/status    启/禁用
DELETE /api/users/<id>           删除
"""
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from extensions import db, bcrypt
from apps.api import auth_bp, users_bp
from apps.models import User, OpLog
from apps.common.response import success, error
from apps.common.pagination import get_pagination, paginate
from apps.common.audit import log_action


# ---------------- Auth ----------------
@auth_bp.post('/login')
def login():
    p = request.get_json(silent=True) or {}
    username = (p.get('username') or '').strip()
    password = p.get('password') or ''
    if not username or not password:
        return error('用户名和密码为必填项')
    user = User.query.filter_by(username=username).first()
    if not user:
        return error('用户不存在', code=401, http_status=401)
    if user.status == 'disabled':
        return error('账号已被禁用，请联系管理员', code=403, http_status=403)
    if not user.check_password(password):
        # 兼容 bcrypt 插件 generate_password_hash 生成与 werkzeug 自带生成的差异（这里模型用的就是 flask_bcrypt，所以 ok）
        # 兜底：如果密码 hash 看起来是 pbkdf2_sha256 格式，尝试 werkzeug.check_password_hash
        try:
            from werkzeug.security import check_password_hash as _wk_check
            if not _wk_check(user.password_hash, password):
                return error('密码错误', code=401, http_status=401)
        except Exception:
            return error('密码错误', code=401, http_status=401)

    identity = str(user.id)
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    # 写操作日志
    try:
        db.session.add(OpLog(user_id=user.id, action='登录', detail=f'用户登录：{user.username}'))
        db.session.commit()
    except Exception:
        db.session.rollback()
    return success({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
    }, message='登录成功')


@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return error('用户不存在', http_status=404)
    identity = str(user.id)
    return success({
        'access_token': create_access_token(identity=identity),
    })


@auth_bp.get('/me')
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return error('用户不存在', http_status=404)
    return success(user.to_dict())


@auth_bp.patch('/me/password')
@jwt_required()
def change_my_password():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return error('用户不存在', http_status=404)
    p = request.get_json(silent=True) or {}
    old_password = p.get('old_password') or ''
    new_password = p.get('new_password') or ''
    if not old_password or not new_password:
        return error('旧密码和新密码为必填项')
    if not user.check_password(old_password):
        return error('旧密码不正确', http_status=401)
    if len(new_password) < 6:
        return error('密码长度不能少于 6 位')
    user.set_password(new_password)
    db.session.commit()
    return success(message='密码修改成功')


@auth_bp.post('/register')
@log_action('用户注册', module='系统设置')
def register():
    p = request.get_json(silent=True) or {}
    username = (p.get('username') or '').strip()
    password = p.get('password') or ''
    if not username or not password:
        return error('用户名和密码为必填项')
    if User.query.filter_by(username=username).first():
        return error('用户名已存在')
    role = p.get('role', '普通用户') or '普通用户'
    if role not in ('管理员', '运维工程师', '普通用户'):
        role = '普通用户'
    user = User(
        username=username,
        role=role,
        email=p.get('email', '') or '',
        status=p.get('status', 'active') or 'active',
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return success(user.to_dict(), message='注册成功')


# ---------------- Users CRUD ----------------
@users_bp.get('')
def list_users():
    q = User.query
    kw = request.args.get('username', '').strip()
    if kw:
        q = q.filter(db.or_(User.username.like(f'%{kw}%'), User.email.like(f'%{kw}%')))
    role = request.args.get('role')
    if role:
        q = q.filter(User.role == role)
    status = request.args.get('status')
    if status:
        q = q.filter(User.status == status)
    q = q.order_by(User.id.desc())
    page, per_page = get_pagination()
    return success(paginate(q, page, per_page))


@users_bp.get('/<int:user_id>')
def get_user(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error('用户不存在', http_status=404)
    return success(u.to_dict())


@users_bp.post('')
@log_action('新增用户', module='系统设置')
def create_user():
    p = request.get_json(silent=True) or {}
    username = (p.get('username') or '').strip()
    password = p.get('password') or ''
    if not username or not password:
        return error('用户名和密码为必填项')
    if User.query.filter_by(username=username).first():
        return error('用户名已存在')
    u = User(
        username=username,
        role=p.get('role', '普通用户') or '普通用户',
        email=p.get('email', '') or '',
        status=p.get('status', 'active') or 'active',
    )
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return success(u.to_dict(), message='创建用户成功')


@users_bp.put('/<int:user_id>')
@log_action('更新用户', module='系统设置')
def update_user(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error('用户不存在', http_status=404)
    p = request.get_json(silent=True) or {}
    for k in ('email', 'role', 'status'):
        if k in p and p[k] is not None:
            setattr(u, k, p[k])
    db.session.commit()
    return success(u.to_dict())


@users_bp.patch('/<int:user_id>/password')
@log_action('重置密码', module='系统设置')
def reset_password(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error('用户不存在', http_status=404)
    pwd = (request.get_json(silent=True) or {}).get('password') or ''
    if len(pwd) < 6:
        return error('密码长度不能少于 6 位')
    u.set_password(pwd)
    db.session.commit()
    return success(message='重置密码成功')


@users_bp.patch('/<int:user_id>/status')
@log_action('更新用户状态', module='系统设置')
def toggle_user_status(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error('用户不存在', http_status=404)
    status = (request.get_json(silent=True) or {}).get('status')
    if status not in ('active', 'disabled'):
        return error('status 参数不合法')
    u.status = status
    db.session.commit()
    return success({'id': u.id, 'status': u.status})


@users_bp.delete('/<int:user_id>')
@log_action('删除用户', module='系统设置')
def delete_user(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error('用户不存在', http_status=404)
    db.session.delete(u)
    db.session.commit()
    return success(message='删除用户成功')
