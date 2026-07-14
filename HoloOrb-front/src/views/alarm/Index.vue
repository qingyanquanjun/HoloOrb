<template>
  <div class="alarm">
    <div class="alarm-summary-bar">
      <div class="alarm-summary-item" v-for="(c, i) in cards" :key="i">
        <el-icon :size="20" :style="{ color: c.color }"><component :is="c.icon" /></el-icon>
        <div class="alarm-summary-content">
          <span class="alarm-summary-label">{{ c.label }}</span>
          <span class="alarm-summary-value" :style="{ color: c.color }">{{ c.value }}</span>
        </div>
      </div>
    </div>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head">
        <div class="panel-title"><el-icon><Warning /></el-icon> 告警记录</div>
        <div class="ph-actions">
          <el-select v-model="filterLevel" placeholder="全部级别" clearable size="default" style="width: 130px">
            <el-option label="严重" value="danger" />
            <el-option label="警告" value="warning" />
            <el-option label="提示" value="primary" />
            <el-option label="信息" value="info" />
          </el-select>
          <el-button size="default" plain @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>
        </div>
      </div>

      <el-tabs v-model="filterStatus" class="alarm-tabs">
        <el-tab-pane label="全部" name="all">
          <div class="sub-hint">共 {{ pagination.total }} 条</div>
        </el-tab-pane>
        <el-tab-pane label="活跃告警" name="active">
          <el-tag type="danger" size="small" effect="dark">{{ overview.active }}</el-tag> 条待处理
        </el-tab-pane>
        <el-tab-pane label="已确认" name="acknowledged">
          <el-tag type="warning" size="small" effect="dark">{{ overview.acknowledged }}</el-tag> 条处理中
        </el-tab-pane>
        <el-tab-pane label="已解决" name="resolved">
          <el-tag type="success" size="small" effect="dark">{{ overview.resolved }}</el-tag> 条已恢复
        </el-tab-pane>
        <el-tab-pane label="本周总计" name="week">
          <el-tag type="info" size="small" effect="dark">{{ overview.week_total }}</el-tag> 条
        </el-tab-pane>
      </el-tabs>

      <el-table :data="alarmList" stripe size="default" v-loading="loading">
        <el-table-column width="70" label="级别">
          <template #default="{ row }">
            <el-tag :type="levelType(row.level)" effect="dark" size="small">{{ levelText(row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="告警编号" width="80" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="device_name" label="关联设备" width="140" />
        <el-table-column prop="message" label="详情" min-width="240" show-overflow-tooltip />
        <el-table-column width="100" label="状态">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handler" label="处理人" width="110" />
        <el-table-column prop="created_at" label="发生时间" width="170" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'active'" link type="primary" size="small" @click="act(row,'ack')">确认</el-button>
            <el-button v-if="row.status !== 'resolved'" link type="success" size="small" @click="act(row,'res')">标记解决</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10,20,50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @size-change="loadAlerts"
        @current-change="loadAlerts"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listAlerts, getAlertSummary, ackAlert, resolveAlert, deleteAlert } from '@/api/alerts'
import { useUserStore } from '@/stores/user'

const loading = ref(false)
const overview = reactive({ active: 0, acknowledged: 0, resolved: 0, today: 0, week_total: 0 })
const userStore = useUserStore()

const cards = computed(() => [
  { key: 'active', label: '活跃告警', value: overview.active, icon: 'BellFilled', color: '#F56C6C' },
  { key: 'ack', label: '已确认', value: overview.acknowledged, icon: 'CircleCheck', color: '#E6A23C' },
  { key: 'res', label: '已解决', value: overview.resolved, icon: 'Finished', color: '#67C23A' },
  { key: 'week', label: '本周总计', value: overview.week_total, icon: 'DataLine', color: '#409EFF' }
])

const filterLevel = ref('')
const filterStatus = ref('all')
const pagination = reactive({ page: 1, per_page: 10, total: 0 })
const alarmList = ref([])

function levelType(l) {
  return { danger: 'danger', warning: 'warning', primary: 'info', info: '' }[l] || 'info'
}

function levelText(l) {
  return { danger: '严重', warning: '警告', primary: '提示', info: '信息' }[l] || l
}

function statusType(s) {
  return { active: 'danger', acknowledged: 'warning', resolved: 'success' }[s] || ''
}

function statusText(s) {
  return { active: '活跃', acknowledged: '已确认', resolved: '已解决' }[s] || s
}

async function loadAlerts() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      level: filterLevel.value,
      status: filterStatus.value === 'all' || filterStatus.value === 'week' ? '' : filterStatus.value
    }
    const data = await listAlerts(params)
    alarmList.value = data.items || data.data || []
    pagination.total = data.total || 0
  } catch (e) {
    console.error('Failed to load alerts', e)
  } finally {
    loading.value = false
  }
}

async function loadSummary() {
  try {
    const data = await getAlertSummary()
    Object.assign(overview, data)
  } catch (e) {
    console.error('Failed to load alert summary', e)
  }
}

async function act(row, type) {
  try {
    const handler = userStore.userInfo?.username || userStore.userInfo?.name || '用户'
    if (type === 'ack') {
      await ackAlert(row.id, { handler })
      row.status = 'acknowledged'
      row.handler = handler
      overview.active--
      overview.acknowledged++
      ElMessage.success('已确认告警')
    } else if (type === 'res') {
      await resolveAlert(row.id, { handler })
      if (row.status === 'active') {
        overview.active--
      } else {
        overview.acknowledged--
      }
      overview.resolved++
      row.status = 'resolved'
      row.handler = handler
      ElMessage.success('已标记为已解决')
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定删除告警「${row.type}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteAlert(row.id)
        ElMessage.success('删除成功')
        loadAlerts()
        loadSummary()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

function handleExport() {
  const exportData = alarmList.value.map(item => ({
    '告警编号': item.id,
    '级别': levelText(item.level),
    '类型': item.type,
    '关联设备': item.device_name || '-',
    '详情': item.message || '-',
    '状态': statusText(item.status),
    '处理人': item.handler || '-',
    '发生时间': item.created_at || '-'
  }))
  
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '告警记录')
  XLSX.writeFile(wb, `告警记录_${new Date().toISOString().slice(0, 10)}.xlsx`)
}

watch([filterStatus, filterLevel], () => {
  pagination.page = 1
  loadAlerts()
})

onMounted(() => {
  loadSummary()
  loadAlerts()
})
</script>

<style scoped>
.alarm { width: 100%; }
.alarm-summary-bar {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: #fff;
  padding: 16px 24px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.alarm-summary-item {
  display: flex;
  align-items: center;
  gap: 10px;
}
.alarm-summary-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.alarm-summary-label { font-size: 13px; color: #909399; }
.alarm-summary-value { font-size: 24px; font-weight: 700; }

.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
.ph-actions { display: flex; align-items: center; gap: 10px; }
.alarm-tabs :deep(.el-tabs__header) { margin: 8px 0 14px; }
.alarm-tabs :deep(.el-tabs__item) { font-size: 14px; }
.sub-hint { color: #909399; font-size: 13px; }
</style>