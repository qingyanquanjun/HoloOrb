-- ================================================================
-- HoloOrb 数据库 Schema（用户提供版，MySQL 5.7+/8.0+）
-- 用法（本机 MySQL）:
--   mysql -uroot -p < sql/schema.sql
-- 或先登录 mysql 后执行：source /path/to/this/file.sql
-- ================================================================

create database if not exists holoorb default character set utf8mb4 collate utf8mb4_unicode_ci;
use holoorb;

-- ------------------------
-- 网络设备表
-- ------------------------
drop table if exists metrics;
drop table if exists alerts;
drop table if exists devices;
create table devices
(
    id                int auto_increment comment '设备ID' primary key,
    name              varchar(100)                                                                   not null comment '设备名称',
    ip                varchar(45)                                                                    not null comment 'IP地址',
    type              varchar(50)                                                                    not null comment '设备类型(交换机/路由器/防火墙等)',
    area              varchar(100)                                         default ''                null comment '所属区域',
    status            enum ('online', 'offline', 'warning', 'maintenance') default 'online'          null comment '运行状态',
    description       text                                                                           null comment '设备描述',
    `interfaces`        int                                                  default 0                 null comment '接口总数',
    in_use_interfaces int                                                  default 0                 null comment '使用中接口数',
    temperature       varchar(10)                                          default ''                null comment '设备温度',
    uptime            varchar(50)                                          default ''                null comment '运行时长',
    created_at        datetime                                             default CURRENT_TIMESTAMP null comment '添加时间',
    index idx_status (status),
    index idx_type (type)
) comment '网络设备表' row_format = DYNAMIC;

-- ------------------------
-- 告警记录表
-- ------------------------
drop table if exists alerts;
create table alerts
(
    id         int auto_increment comment '告警ID' primary key,
    device_id  int                                                                     not null comment '关联设备ID',
    type       varchar(50)                                                             not null comment '告警类型(CPU过高/流量异常等)',
    level      enum ('danger', 'warning', 'primary', 'info') default 'warning'         not null comment '告警级别',
    status     enum ('active', 'acknowledged', 'resolved')   default 'active'          not null comment '处理状态',
    message    text                                                                    null comment '告警详情',
    handler    varchar(50)                                   default ''                null comment '处理人',
    created_at datetime                                      default CURRENT_TIMESTAMP null comment '告警时间',
    constraint fk_alerts_device foreign key (device_id) references devices (id) on delete cascade,
    index idx_created (created_at),
    index idx_device_level (device_id, level),
    index idx_status (status)
) comment '告警记录表' row_format = DYNAMIC;

-- ------------------------
-- 监控指标表
-- ------------------------
drop table if exists metrics;
create table metrics
(
    id               int auto_increment comment '指标ID' primary key,
    device_id        int                                not null comment '所属设备ID',
    cpu              float    default 0                 null comment 'CPU使用率(%)',
    memory           float    default 0                 null comment '内存使用率(%)',
    traffic_in       float    default 0                 null comment '入流量(Mbps)',
    traffic_out      float    default 0                 null comment '出流量(Mbps)',
    interface_status text                               null comment '接口状态(JSON)',
    collected_at     datetime default CURRENT_TIMESTAMP null comment '采集时间',
    constraint fk_metrics_device foreign key (device_id) references devices (id) on delete cascade,
    index idx_device_collected (device_id, collected_at)
) comment '监控指标表' row_format = DYNAMIC;

-- ------------------------
-- 分析报告表
-- ------------------------
drop table if exists reports;
create table reports
(
    id           int auto_increment comment '报告ID' primary key,
    type         enum ('日报', '周报', '月报')         not null comment '报告类型',
    title        varchar(200)                          not null comment '报告标题',
    content      text                                  null comment '报告内容',
    status       varchar(20) default 'generated'       null comment '生成状态',
    generated_at datetime    default CURRENT_TIMESTAMP null comment '生成时间',
    index idx_type_time (type, generated_at)
) comment '分析报告表' row_format = DYNAMIC;

-- ------------------------
-- 用户表
-- ------------------------
drop table if exists logs;
drop table if exists users;
create table users
(
    id            int auto_increment comment '用户ID' primary key,
    username      varchar(50)                                                         not null comment '用户名',
    password_hash varchar(200)                                                        not null comment '密码哈希(bcrypt)',
    role          enum ('管理员', '运维工程师', '普通用户') default '普通用户'        not null comment '角色',
    email         varchar(100)                              default ''                null comment '邮箱',
    status        enum ('active', 'disabled')               default 'active'          null comment '状态',
    created_at    datetime                                  default CURRENT_TIMESTAMP null comment '创建时间',
    constraint username unique (username),
    index idx_username (username)
) comment '用户表' row_format = DYNAMIC;

-- ------------------------
-- 操作日志表
-- ------------------------
drop table if exists logs;
create table logs
(
    id         int auto_increment comment '日志ID' primary key,
    user_id    int                                null comment '操作用户ID',
    action     varchar(100)                       not null comment '操作类型',
    detail     text                               null comment '操作详情',
    created_at datetime default CURRENT_TIMESTAMP null comment '操作时间',
    constraint fk_logs_user foreign key (user_id) references users (id) on delete set null,
    index idx_user_time (user_id, created_at)
) comment '操作日志表' row_format = DYNAMIC;
