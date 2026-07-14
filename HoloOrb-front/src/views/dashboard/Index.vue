<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :xs="12" :sm="12" :md="6" v-for="card in statCards" :key="card.key">
        <div class="stat-card" :class="card.key">
          <div class="stat-icon" :style="{ background: card.bg }">
            <el-icon :size="24"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-title">{{ card.title }}</div>
            <div class="stat-value">
              {{ card.value }}
              <span class="stat-unit" v-if="card.unit">{{ card.unit }}</span>
            </div>
            <div class="stat-foot">
              <el-tag :type="card.tagType" size="small">{{ card.tag }}</el-tag>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :lg="14">
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">CPU / 内存使用率趋势（1个月）</span>
            <el-radio-group v-model="range" size="small" @change="loadCpuMemory">
              <el-radio-button value="24h">24小时</el-radio-button>
              <el-radio-button value="7d">7天</el-radio-button>
              <el-radio-button value="30d">1个月</el-radio-button>
            </el-radio-group>
          </div>
          <BaseChart :option="cpuMemoryOption" height="280px" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="10">
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">网络流量统计（Mbps）</span>
            <el-tag type="info" size="small">过去 1 个月</el-tag>
          </div>
          <BaseChart :option="trafficOption" height="280px" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :lg="8">
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">设备类型分布</span>
          </div>
          <BaseChart :option="deviceTypeOption" height="280px" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="16">
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">近期告警</span>
            <el-button link type="primary" size="small">查看全部 →</el-button>
          </div>
          <el-table :data="recentAlarms" size="small" stripe>
            <el-table-column width="70" label="级别">
              <template #default="{ row }">
                <el-tag :type="levelTag(row.level)" size="small" effect="dark">{{ levelText(row.level) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="device_name" label="设备" width="130" />
            <el-table-column prop="message" label="告警内容" />
            <el-table-column prop="created_at" label="时间" width="160" />
            <el-table-column width="90" label="状态">
              <template #default="{ row }">
                <el-tag :type="statusTag(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import BaseChart from '@/components/BaseChart.vue'
import { getOverview, getCpuMemoryTrend, getTrafficTrend, getDevicesByType, getRecentAlarms } from '@/api/dashboard'

const range = ref('30d')

const overview = ref({
  online_devices: 0,
  total_devices: 0,
  today_alerts: 0,
  avg_cpu: 0,
  avg_memory: 0,
  avg_traffic_in: 0,
  avg_traffic_out: 0,
  network_health: 100
})

const cpuMemoryData = ref({ timeline: [], cpu: [], memory: [] })
const trafficData = ref({ timeline: [], inbound: [], outbound: [] })
const deviceTypeData = ref([])
const recentAlarms = ref([])

const statCards = computed(() => [
  {
    key: 'online',
    title: '在线设备',
    value: `${overview.value.online_devices} / ${overview.value.total_devices}`,
    unit: '',
    icon: 'Monitor',
    bg: 'linear-gradient(135deg,#409EFF,#2C7EFF)',
    tag: '在线率 ' + (overview.value.total_devices ? Math.round(overview.value.online_devices / overview.value.total_devices * 100) : 0) + '%',
    tagType: 'success'
  },
  {
    key: 'alarm',
    title: '今日告警',
    value: overview.value.today_alerts,
    unit: '条',
    icon: 'Warning',
    bg: 'linear-gradient(135deg,#F56C6C,#E74C3C)',
    tag: '未处理告警',
    tagType: 'danger'
  },
  {
    key: 'cpu',
    title: 'CPU 平均负载',
    value: overview.value.avg_cpu,
    unit: '%',
    icon: 'Cpu',
    bg: 'linear-gradient(135deg,#E6A23C,#F39C12)',
    tag: '实时监控',
    tagType: 'info'
  },
  {
    key: 'net',
    title: '网络健康度',
    value: overview.value.network_health,
    unit: '%',
    icon: 'Connection',
    bg: 'linear-gradient(135deg,#67C23A,#27AE60)',
    tag: '优秀',
    tagType: 'success'
  }
])

const cpuMemoryOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['CPU 使用率', '内存使用率'], right: 10, top: 0 },
  grid: { left: 40, right: 20, top: 36, bottom: 30 },
  xAxis: { type: 'category', data: cpuMemoryData.value.timeline || cpuMemoryData.value.hours, boundaryGap: false, axisLabel: { fontSize: 11 } },
  yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
  series: [
    {
      name: 'CPU 使用率',
      type: 'line',
      smooth: true,
      data: cpuMemoryData.value.cpu,
      areaStyle: { color: 'rgba(64,158,255,0.18)' },
      lineStyle: { color: '#409EFF', width: 2 },
      itemStyle: { color: '#409EFF' }
    },
    {
      name: '内存使用率',
      type: 'line',
      smooth: true,
      data: cpuMemoryData.value.memory,
      areaStyle: { color: 'rgba(103,194,58,0.18)' },
      lineStyle: { color: '#67C23A', width: 2 },
      itemStyle: { color: '#67C23A' }
    }
  ]
}))

const trafficOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['入站', '出站'], right: 10, top: 0 },
  grid: { left: 40, right: 20, top: 36, bottom: 30 },
  xAxis: { type: 'category', data: trafficData.value.timeline || trafficData.value.hours, axisLabel: { fontSize: 11 } },
  yAxis: { type: 'value', axisLabel: { formatter: '{value} M' } },
  series: [
    { name: '入站', type: 'bar', data: trafficData.value.inbound, stack: 't', itemStyle: { color: '#409EFF' } },
    { name: '出站', type: 'bar', data: trafficData.value.outbound, stack: 't', itemStyle: { color: '#F56C6C' } }
  ]
}))

const deviceTypeOption = computed(() => {
  const data = deviceTypeData.value.map(item => ({ name: item.type, value: item.value }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 台 ({d}%)' },
    legend: { bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 11 } },
    color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#9B59B6', '#16A085'],
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        labelLine: { show: false },
        data
      }
    ]
  }
})

function levelTag(l) {
  return { danger: 'danger', warning: 'warning', primary: 'info', info: '' }[l] || 'info'
}
function levelText(l) {
  return { danger: '严重', warning: '警告', primary: '提示', info: '信息' }[l] || l
}
function statusTag(s) {
  return { active: 'danger', acknowledged: 'warning', resolved: 'success' }[s] || ''
}
function statusText(s) {
  return { active: '活跃', acknowledged: '已确认', resolved: '已解决' }[s] || s
}

async function loadOverview() {
  try {
    const data = await getOverview()
    overview.value = data
  } catch (e) {
    console.error('Failed to load overview', e)
  }
}

function generateMockTimeline(rangeValue) {
  const mapping = { '24h': 24, '7d': 7, '30d': 30 }
  const count = mapping[rangeValue] || 30
  
  if (rangeValue === '24h') {
    return Array.from({ length: count }, (_, i) => `${i.toString().padStart(2, '0')}:00`)
  } else {
    return Array.from({ length: count }, (_, i) => dayjs().subtract(count - 1 - i, 'day').format('MM-DD'))
  }
}

function generateMockTrendData(length, avg, swing) {
  return Array.from({ length }, () => +(avg + (Math.random() - 0.5) * swing).toFixed(1))
}

async function loadCpuMemory() {
  try {
    const mapping = { '24h': 24, '7d': 7, '30d': 30 }
    const hours = mapping[range.value] || 30
    const data = await getCpuMemoryTrend({ hours })
    
    if (data && data.cpu && data.cpu.length > 0) {
      cpuMemoryData.value = data
    } else {
      cpuMemoryData.value = {
        timeline: generateMockTimeline(range.value),
        cpu: generateMockTrendData(mapping[range.value] || 30, 42, 30),
        memory: generateMockTrendData(mapping[range.value] || 30, 58, 20)
      }
    }
  } catch (e) {
    console.error('Failed to load cpu memory trend', e)
    const mapping = { '24h': 24, '7d': 7, '30d': 30 }
    cpuMemoryData.value = {
      timeline: generateMockTimeline(range.value),
      cpu: generateMockTrendData(mapping[range.value] || 30, 42, 30),
      memory: generateMockTrendData(mapping[range.value] || 30, 58, 20)
    }
  }
}

async function loadTraffic() {
  try {
    const mapping = { '24h': 24, '7d': 7, '30d': 30 }
    const hours = mapping[range.value] || 30
    const data = await getTrafficTrend({ hours })
    
    if (data && data.inbound && data.inbound.length > 0) {
      trafficData.value = data
    } else {
      trafficData.value = {
        timeline: generateMockTimeline(range.value),
        inbound: generateMockTrendData(mapping[range.value] || 30, 240, 180).map(v => +v.toFixed(0)),
        outbound: generateMockTrendData(mapping[range.value] || 30, 120, 100).map(v => +v.toFixed(0))
      }
    }
  } catch (e) {
    console.error('Failed to load traffic trend', e)
    const mapping = { '24h': 24, '7d': 7, '30d': 30 }
    trafficData.value = {
      timeline: generateMockTimeline(range.value),
      inbound: generateMockTrendData(mapping[range.value] || 30, 240, 180).map(v => +v.toFixed(0)),
      outbound: generateMockTrendData(mapping[range.value] || 30, 120, 100).map(v => +v.toFixed(0))
    }
  }
}

async function loadDeviceTypes() {
  try {
    const data = await getDevicesByType()
    deviceTypeData.value = data
  } catch (e) {
    console.error('Failed to load device types', e)
  }
}

async function loadRecentAlarms() {
  try {
    const data = await getRecentAlarms({ limit: 20 })
    recentAlarms.value = data
  } catch (e) {
    console.error('Failed to load recent alarms', e)
  }
}

onMounted(() => {
  loadOverview()
  loadCpuMemory()
  loadTraffic()
  loadDeviceTypes()
  loadRecentAlarms()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}
.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  display: flex;
  gap: 14px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}
.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-info {
  flex: 1;
  min-width: 0;
}
.stat-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}
.stat-unit {
  font-size: 13px;
  font-weight: 400;
  color: #909399;
  margin-left: 2px;
}
.stat-foot {
  margin-top: 6px;
}
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  height: 100%;
  box-sizing: border-box;
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
</style>