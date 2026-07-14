/**
 * 全站通用假数据（mock data）
 */
import dayjs from 'dayjs'

export const mockUsers = [
  { username: 'admin', password: 'admin123', name: '系统管理员', role: '超级管理员', email: 'admin@holoorb.local' },
  { username: 'ops_user', password: '123456', name: '李运维', role: '运维工程师', email: 'ops@holoorb.local' },
  { username: 'sys_zhangsan', password: '123456', name: '张工程', role: '工程师', email: 'zhangsan@holoorb.local' },
  { username: 'viewer_wang', password: '123456', name: '王审计', role: '只读用户', email: 'wang@holoorb.local' }
]

export function mockLogin(data) {
  const user = mockUsers.find(u => u.username === data.username && u.password === data.password)
  if (user) {
    return {
      code: 0,
      message: '登录成功',
      data: {
        token: 'mock-token-' + user.username + '-' + Date.now(),
        user: {
          username: user.username,
          name: user.name,
          role: user.role,
          email: user.email
        }
      }
    }
  }
  return {
    code: 401,
    message: '用户名或密码错误'
  }
}

/* ---------------- 仪表盘 ---------------- */
export const dashboardStats = {
  onlineDevices: 128,
  totalDevices: 156,
  todayAlarms: 17,
  avgCpuLoad: 38.6,
  networkHealth: 96.4
}

// CPU/内存 24小时趋势
const hours = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`)
function trendArr(avg, swing) {
  return hours.map(() => +(avg + (Math.random() - 0.5) * swing).toFixed(1))
}
export const cpuMemorySeries = {
  hours,
  cpu: trendArr(42, 30),
  memory: trendArr(58, 20)
}

// 网络流量趋势（入/出 Mbps）
export const networkTrafficSeries = {
  hours,
  inbound: trendArr(240, 180).map((v) => +v.toFixed(0)),
  outbound: trendArr(120, 100).map((v) => +v.toFixed(0))
}

// 近期告警
export const recentAlarms = [
  { id: 1, level: '严重', device: 'Server-07', content: 'CPU 使用率持续 10 分钟 > 90%', time: '10 分钟前', status: 'active' },
  { id: 2, level: '警告', device: 'Switch-03', content: '端口 GE-0/2 丢包率 2.1%', time: '25 分钟前', status: 'active' },
  { id: 3, level: '提示', device: 'AP-GF-12', content: '在线客户端超过阈值（>32）', time: '1 小时前', status: 'acknowledged' },
  { id: 4, level: '严重', device: 'Storage-02', content: '磁盘剩余 < 5% (/data)', time: '2 小时前', status: 'acknowledged' },
  { id: 5, level: '警告', device: 'Firewall-01', content: '检测到异常外联请求', time: '3 小时前', status: 'resolved' },
  { id: 6, level: '提示', device: 'UPS-01', content: '市电切换，运行于备用电源', time: '昨天', status: 'resolved' }
]

/* ---------------- 设备管理 ---------------- */
export const deviceTypes = ['服务器', '交换机', '路由器', '无线AP', '防火墙', '存储', 'UPS']
export const deviceStatuses = ['在线', '离线', '告警', '维护中']
const deptPool = ['数据中心A', '数据中心B', '办公区', '研发中心', '机房3F']
const modelPool = ['Dell R740', 'HPE DL380', 'Huawei CE6850', 'Cisco C9300', 'H3C S5560', 'Ruijie RG-AP820', 'FortiGate 200E']

function randItem(arr) { return arr[Math.floor(Math.random() * arr.length)] }
function randId() { return 'DEV-' + Math.floor(10000 + Math.random() * 90000) }

export const deviceList = Array.from({ length: 42 }, (_, i) => {
  const type = randItem(deviceTypes)
  const status = Math.random() < 0.82 ? '在线' : randItem(['离线', '告警', '维护中'])
  return {
    id: i + 1,
    deviceId: randId(),
    name: `${type}-${(i + 1).toString().padStart(2, '0')}`,
    type,
    model: randItem(modelPool),
    ip: `10.${10 + Math.floor(Math.random() * 50)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 254) + 1}`,
    dept: randItem(deptPool),
    status,
    cpu: +(Math.random() * 80 + 10).toFixed(1),
    memory: +(Math.random() * 70 + 20).toFixed(1),
    createdAt: dayjs().subtract(Math.floor(Math.random() * 365), 'day').format('YYYY-MM-DD HH:mm')
  }
})

/* ---------------- 数据分析 ---------------- */
export const analysisSummary = {
  totalRecords: 2486732,
  dataSources: 156,
  avgCpuAll: 41.3,
  peakCpuAll: 97.8,
  avgMemoryAll: 57.2,
  anomalyCount: 132,
  anomalyRate: 0.53
}

// CPU 均值 vs 峰值 按设备类型
export const cpuCompare = {
  types: deviceTypes.slice(0, 6),
  avg: [35, 44, 38, 29, 52, 46],
  peak: [91, 98, 88, 76, 99, 93]
}

// 异常检测 30 天趋势
const days30 = Array.from({ length: 30 }, (_, i) => dayjs().subtract(29 - i, 'day').format('MM-DD'))
export const anomalyTrend = {
  days: days30,
  anomalies: days30.map(() => Math.floor(Math.random() * 15) + 1)
}

/* ---------------- 告警中心 ---------------- */
export const alarmOverview = {
  active: 9,
  acknowledged: 18,
  resolved: 143,
  weekTotal: 170
}

export const alarmRecords = Array.from({ length: 26 }, (_, i) => {
  const levels = ['严重', '警告', '提示', '信息']
  const statuses = ['active', 'acknowledged', 'resolved']
  const level = levels[Math.floor(Math.random() * levels.length)]
  const status = i < 9 ? 'active' : i < 27 ? statuses[1 + Math.floor(Math.random() * 2)] : 'resolved'
  return {
    id: 'ALM' + (20000 + i),
    level,
    title: `${randItem(deviceTypes)}异常事件 #${i + 1}`,
    device: randItem(deviceList).name,
    content: ['CPU使用率超过阈值', '内存使用率过高', '磁盘I/O异常', '网络连接数激增', '服务响应超时', '登录失败次数过多'][i % 6],
    status,
    createdAt: dayjs().subtract(i * 3, 'hour').format('YYYY-MM-DD HH:mm'),
    operator: i % 3 === 0 ? '-' : ['admin', 'ops_user', 'sys_zhangsan'][i % 3]
  }
})

/* ---------------- 报表中心 ---------------- */
const weekDays = Array.from({ length: 7 }, (_, i) => dayjs().subtract(6 - i, 'day').format('MM-DD (ddd)').replace('ddd', ['周日','周一','周二','周三','周四','周五','周六'][dayjs().subtract(6 - i, 'day').day()]))
export const weekTrend = {
  days: weekDays,
  alarms: [22, 18, 31, 24, 29, 27, 19],
  online: [124, 126, 125, 128, 127, 130, 128],
  anomalies: [12, 18, 22, 15, 19, 21, 14]
}

export const reportList = Array.from({ length: 14 }, (_, i) => ({
  id: 'RPT' + (1000 + i),
  name: ['系统资源周报', '网络流量月报', '告警统计日报', '设备健康季度报告', '异常检测分析'][i % 5] + `-${2026}${(Math.floor(i / 5) + 1).toString().padStart(2, '0')}${(i + 1).toString().padStart(2, '0')}`,
  type: ['日报', '周报', '月报', '季报', '专项报告'][i % 5],
  creator: ['admin', 'ops_user', 'ai_agent'][i % 3],
  size: (Math.random() * 8 + 0.5).toFixed(2) + ' MB',
  createdAt: dayjs().subtract(i, 'day').format('YYYY-MM-DD HH:mm'),
  status: i % 7 === 0 ? '生成中' : '已完成'
}))

/* ---------------- 智能洞察 ---------------- */
export const aiPresetReports = [
  {
    id: 'R-AI-001',
    title: '本周服务器 CPU 瓶颈分析',
    summary: 'Server-07、Server-12、Storage-02 在 14:00-17:00 持续高负载，建议对 Server-07 上的 MySQL 实例做慢查询排查。',
    createdAt: '2026-07-08 18:20',
    tags: ['CPU', '性能分析', '数据库'],
    riskLevel: '高'
  },
  {
    id: 'R-AI-002',
    title: '网络丢包关联根因',
    summary: 'Switch-03 端口 GE-0/2 丢包与同期广播风暴强相关，建议开启广播抑制并排查下联 AP-GF-12 是否存在异常终端。',
    createdAt: '2026-07-07 09:14',
    tags: ['网络', '丢包', '根因分析'],
    riskLevel: '中'
  },
  {
    id: 'R-AI-003',
    title: '未来 7 天容量预测',
    summary: 'Storage-01、Storage-02 磁盘增长率分别为 4.2%/周、6.1%/周，预计 22 天、15 天后达到阈值，建议提前扩容或清理归档。',
    createdAt: '2026-07-06 23:05',
    tags: ['容量预测', '存储'],
    riskLevel: '中'
  }
]

/* ---------------- 系统设置 ---------------- */
export const collectionTasks = [
  { id: 1, name: '服务器 SNMP 采集', target: '服务器*', interval: '60s', status: '运行中', lastRun: '5 秒前' },
  { id: 2, name: '交换机端口流量', target: '交换机*', interval: '30s', status: '运行中', lastRun: '12 秒前' },
  { id: 3, name: '无线 AP 客户端', target: 'AP*', interval: '2min', status: '运行中', lastRun: '1 分钟前' },
  { id: 4, name: '防火墙日志抓取', target: 'Firewall*', interval: '10s', status: '已暂停', lastRun: '1 天前' },
  { id: 5, name: '存储阵列健康', target: 'Storage*', interval: '5min', status: '运行中', lastRun: '2 分钟前' }
]

export const alarmRules = [
  { id: 1, name: 'CPU>90% 持续5min', level: '严重', target: '所有服务器', enabled: true, notify: ['邮件', '钉钉'] },
  { id: 2, name: '内存>95%', level: '警告', target: '所有设备', enabled: true, notify: ['邮件'] },
  { id: 3, name: '磁盘剩余<10%', level: '严重', target: '存储节点', enabled: true, notify: ['邮件', '短信'] },
  { id: 4, name: '设备离线>3min', level: '严重', target: '所有设备', enabled: true, notify: ['钉钉', '短信'] },
  { id: 5, name: '丢包率>1%', level: '警告', target: '网络设备', enabled: false, notify: ['邮件'] },
  { id: 6, name: '登录失败>5次/10min', level: '提示', target: '所有设备', enabled: true, notify: ['邮件'] }
]

export const backupRecords = [
  { id: 1, name: '配置全量备份-2026-07-09', type: '配置', size: '128 MB', time: '今天 02:00', status: '成功' },
  { id: 2, name: '数据库增量备份', type: '数据', size: '842 MB', time: '今天 03:30', status: '成功' },
  { id: 3, name: '配置全量备份-2026-07-08', type: '配置', size: '127 MB', time: '昨天 02:00', status: '成功' },
  { id: 4, name: '数据库全量备份', type: '数据', size: '56 GB', time: '07-06 周日 04:00', status: '成功' },
  { id: 5, name: '告警历史归档', type: '日志', size: '2.3 GB', time: '07-01 周二 00:00', status: '成功' }
]

export const systemUsers = [
  { id: 1, username: 'admin', name: '系统管理员', role: '超级管理员', email: 'admin@holoorb.local', status: '启用', lastLogin: '今天 18:12' },
  { id: 2, username: 'ops_user', name: '李运维', role: '运维工程师', email: 'ops@holoorb.local', status: '启用', lastLogin: '今天 16:40' },
  { id: 3, username: 'sys_zhangsan', name: '张工程', role: '工程师', email: 'zhangsan@holoorb.local', status: '启用', lastLogin: '昨天 09:15' },
  { id: 4, username: 'viewer_wang', name: '王审计', role: '只读用户', email: 'wang@holoorb.local', status: '启用', lastLogin: '07-07' },
  { id: 5, username: 'test01', name: '测试账号', role: '只读用户', email: 'test01@holoorb.local', status: '禁用', lastLogin: '06-20' }
]

export const operationLogs = Array.from({ length: 20 }, (_, i) => {
  const actions = ['登录', '登出', '新增设备', '删除设备', '修改告警规则', '执行备份', '修改用户', '重启采集任务', '下载报表', '确认告警']
  const mods = ['认证', '设备管理', '告警中心', '系统设置', '报表中心', '数据采集']
  return {
    id: 200 + i,
    user: ['admin', 'ops_user', 'sys_zhangsan'][i % 3],
    module: mods[i % mods.length],
    action: actions[i % actions.length],
    detail: `${actions[i % actions.length]} #${i + 1} - 相关ID: ${10000 + i}`,
    ip: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 254) + 1}`,
    time: dayjs().subtract(i * 17, 'minute').format('YYYY-MM-DD HH:mm:ss'),
    status: i % 9 === 3 ? '失败' : '成功'
  }
})
