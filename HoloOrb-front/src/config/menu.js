/**
 * 侧边栏菜单配置
 * meta: { title, icon, roles?, hidden? }
 */
export const menuConfig = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    meta: { title: '仪表盘', icon: 'DataBoard' },
    children: [
      {
        path: '/dashboard',
        name: 'DashboardIndex',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: { title: '概览', icon: 'Odometer' }
      }
    ]
  },
  {
    path: '/device',
    name: 'Device',
    meta: { title: '设备管理', icon: 'Monitor' },
    children: [
      {
        path: '/device',
        name: 'DeviceList',
        component: () => import('@/views/device/List.vue'),
        meta: { title: '设备管理', icon: 'List' }
      }
    ]
  },
  {
    path: '/analysis',
    name: 'Analysis',
    meta: { title: '数据分析', icon: 'DataAnalysis' },
    children: [
      {
        path: '/analysis',
        name: 'AnalysisIndex',
        component: () => import('@/views/analysis/Index.vue'),
        meta: { title: '分析中心', icon: 'TrendCharts' }
      }
    ]
  },
  {
    path: '/insight',
    name: 'Insight',
    meta: { title: '智能洞察', icon: 'MagicStick' },
    children: [
      {
        path: '/insight/chat',
        name: 'InsightChat',
        component: () => import('@/views/insight/Chat.vue'),
        meta: { title: 'AI 智能问答', icon: 'ChatDotRound' }
      },
      {
        path: '/insight/report',
        name: 'InsightReport',
        component: () => import('@/views/insight/Report.vue'),
        meta: { title: 'AI 分析报告', icon: 'Document' }
      }
    ]
  },
  {
    path: '/alarm',
    name: 'Alarm',
    meta: { title: '告警中心', icon: 'Bell' },
    children: [
      {
        path: '/alarm',
        name: 'AlarmIndex',
        component: () => import('@/views/alarm/Index.vue'),
        meta: { title: '告警管理', icon: 'Warning' }
      }
    ]
  },
  {
    path: '/report',
    name: 'Report',
    meta: { title: '报表中心', icon: 'PieChart' },
    children: [
      {
        path: '/report',
        name: 'ReportTrend',
        component: () => import('@/views/report/Trend.vue'),
        meta: { title: '报表中心', icon: 'TrendCharts' }
      }
    ]
  },
  {
    path: '/settings',
    name: 'Settings',
    meta: { title: '系统设置', icon: 'Setting' },
    children: [
      {
        path: '/settings/collection',
        name: 'SettingsCollection',
        component: () => import('@/views/settings/Collection.vue'),
        meta: { title: '数据采集', icon: 'Connection' }
      },
      {
        path: '/settings/rules',
        name: 'SettingsRules',
        component: () => import('@/views/settings/Rules.vue'),
        meta: { title: '告警规则', icon: 'AlarmClock' }
      },
      {
        path: '/settings/backup',
        name: 'SettingsBackup',
        component: () => import('@/views/settings/Backup.vue'),
        meta: { title: '数据备份', icon: 'Box' }
      },
      {
        path: '/settings/users',
        name: 'SettingsUsers',
        component: () => import('@/views/settings/Users.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: '/settings/logs',
        name: 'SettingsLogs',
        component: () => import('@/views/settings/Logs.vue'),
        meta: { title: '操作日志', icon: 'Notebook' }
      }
    ]
  }
]

// 扁平化成路由使用的 routes
export function flattenMenuRoutes(menu) {
  const routes = []
  menu.forEach((group) => {
    ;(group.children || []).forEach((child) => {
      routes.push(child)
    })
  })
  return routes
}
