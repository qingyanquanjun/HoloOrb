<template>
  <div class="analysis">
    <div class="summary-bar">
      <div class="summary-item" v-for="s in summaryCards" :key="s.key">
        <span class="summary-label">{{ s.title }}</span>
        <span class="summary-value" :style="{ color: s.color }">{{ s.value }}{{ s.unit || '' }}</span>
      </div>
    </div>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :lg="14">
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">设备类型分布</span>
            <el-radio-group size="small" v-model="chartType">
              <el-radio-button value="bar">柱状图</el-radio-button>
              <el-radio-button value="pie">饼图</el-radio-button>
            </el-radio-group>
          </div>
          <BaseChart :option="deviceTypeOption" height="320px" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="10">
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">设备状态统计</span>
          </div>
          <BaseChart :option="statusOption" height="320px" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="24">
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">设备指标概览</span>
            <el-select size="small" placeholder="排序方式" style="width: 160px" v-model="sortKey">
              <el-option label="CPU 占用" value="cpu" />
              <el-option label="内存占用" value="memory" />
            </el-select>
          </div>
          <el-table :data="topList" stripe size="default" v-loading="loading">
            <el-table-column type="index" label="排名" width="70" />
            <el-table-column prop="name" label="设备名称" width="160" />
            <el-table-column prop="type" label="类型" width="110" />
            <el-table-column prop="ip" label="IP" width="150" />
            <el-table-column label="CPU 占用" width="200">
              <template #default="{ row }">
                <el-progress :percentage="row.cpu" :color="c(row.cpu)" :stroke-width="14" />
              </template>
            </el-table-column>
            <el-table-column label="内存占用" width="200">
              <template #default="{ row }">
                <el-progress :percentage="row.memory" :color="c(row.memory)" :stroke-width="14" />
              </template>
            </el-table-column>
            <el-table-column prop="area" label="区域" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import BaseChart from '@/components/BaseChart.vue'
import { getLatestMetrics } from '@/api/metrics'
import { getDeviceSummary } from '@/api/devices'

const sortKey = ref('cpu')
const chartType = ref('bar')
const loading = ref(false)

const latestMetrics = ref([])
const summary = ref({ total: 0, by_status: {}, by_type: {} })

const summaryCards = computed(() => [
  { key: 'total', title: '设备总数', value: summary.value.total, unit: ' 台', foot: '已接入监控', color: '#409EFF' },
  { key: 'online', title: '在线设备', value: summary.value.by_status.online || 0, unit: ' 台', foot: '正常运行', color: '#67C23A' },
  { key: 'warning', title: '告警设备', value: summary.value.by_status.warning || 0, unit: ' 台', foot: '需要关注', color: '#F56C6C' },
  { key: 'offline', title: '离线设备', value: summary.value.by_status.offline || 0, unit: ' 台', foot: '通讯异常', color: '#909399' }
])

const deviceTypeOption = computed(() => {
  const typeData = Object.entries(summary.value.by_type || {}).map(([name, value]) => ({ name, value: Number(value) }))
  if (chartType.value === 'pie') {
    return {
      tooltip: { trigger: 'item', formatter: '{b}: {c} 台 ({d}%)' },
      legend: { bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 11 } },
      color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#9B59B6', '#16A085'],
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        labelLine: { show: false },
        data: typeData
      }]
    }
  }
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: typeData.map(i => i.name) },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: typeData.map(i => i.value),
      itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }
    }]
  }
})

const statusOption = computed(() => {
  const statusMap = { online: '在线', offline: '离线', warning: '告警', maintenance: '维护中' }
  const data = Object.entries(summary.value.by_status || {}).map(([key, value]) => ({
    name: statusMap[key] || key,
    value: Number(value)
  }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 台 ({d}%)' },
    legend: { bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 11 } },
    color: ['#67C23A', '#909399', '#F56C6C', '#E6A23C'],
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      labelLine: { show: false },
      data
    }]
  }
})

const topList = computed(() =>
  [...latestMetrics.value]
    .sort((a, b) => b[sortKey.value] - a[sortKey.value])
    .slice(0, 10)
)

function c(v) {
  if (v >= 85) return '#F56C6C'
  if (v >= 65) return '#E6A23C'
  return '#67C23A'
}

async function loadMetrics() {
  loading.value = true
  try {
    const data = await getLatestMetrics()
    latestMetrics.value = data.items || data || []
  } catch (e) {
    console.error('Failed to load metrics', e)
  } finally {
    loading.value = false
  }
}

async function loadSummary() {
  try {
    const data = await getDeviceSummary()
    summary.value = data
  } catch (e) {
    console.error('Failed to load summary', e)
  }
}

onMounted(() => {
  loadMetrics()
  loadSummary()
})
</script>

<style scoped>
.analysis { width: 100%; }
.summary-bar {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: #fff;
  padding: 16px 24px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}
.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.summary-label { font-size: 13px; color: #909399; }
.summary-value { font-size: 24px; font-weight: 700; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  height: 100%;
  box-sizing: border-box;
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; }
</style>