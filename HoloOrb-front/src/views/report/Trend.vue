<template>
  <div class="report">
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><TrendCharts /></el-icon> 本周趋势</span>
        <el-radio-group v-model="metric" size="small">
          <el-radio-button value="alarms">告警数</el-radio-button>
          <el-radio-button value="online">在线设备</el-radio-button>
        </el-radio-group>
      </div>
      <BaseChart :option="weekOption" height="340px" />
    </div>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Files /></el-icon> 报表列表</span>
        <div>
          <el-button size="small" type="primary" @click="handleAdd"><el-icon><DocumentAdd /></el-icon> 生成新报表</el-button>
        </div>
      </div>

      <div class="toolbar">
        <el-form :inline="true" size="default" label-width="80px">
          <el-form-item label="报表名称">
            <el-input v-model="q.title" placeholder="输入关键字" clearable style="width: 220px" @keyup.enter="loadReports">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item label="报表类型">
            <el-select v-model="q.type" placeholder="全部" clearable style="width: 160px">
              <el-option label="日报" value="日报" />
              <el-option label="周报" value="周报" />
              <el-option label="月报" value="月报" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadReports">查询</el-button>
            <el-button @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="reportList" stripe v-loading="loading">
        <el-table-column prop="id" label="报表编号" width="80" />
        <el-table-column prop="title" label="报表名称" min-width="320" show-overflow-tooltip />
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag :type="typeTag(row.type)" size="small" effect="plain">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="generated_at" label="生成时间" width="170" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'generated' ? 'success' : 'warning'" size="small" effect="dark">
              {{ row.status === 'generated' ? '已完成' : row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" :disabled="row.status !== 'generated'" @click="handlePreview(row)">预览</el-button>
            <el-button link type="primary" size="small" :disabled="row.status !== 'generated'" @click="handleDownload(row)">下载</el-button>
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
        @size-change="loadReports"
        @current-change="loadReports"
      />
    </div>

    <el-dialog v-model="dialogVisible" title="生成新报表" width="500px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item label="报表类型" required>
          <el-select v-model="form.type" placeholder="请选择" style="width: 100%">
            <el-option label="日报" value="日报" />
            <el-option label="周报" value="周报" />
            <el-option label="月报" value="月报" />
          </el-select>
        </el-form-item>
        <el-form-item label="报表标题" required>
          <el-input v-model="form.title" placeholder="请输入报表标题" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewDialogVisible" :title="'报表预览 - ' + previewData.title" width="700px" destroy-on-close>
      <div class="preview-content">
        <div class="preview-header">
          <div class="preview-title">{{ previewData.title }}</div>
          <div class="preview-info">
            <span class="preview-type">类型：{{ previewData.type }}</span>
            <span class="preview-time">生成时间：{{ previewData.generated_at || '-' }}</span>
          </div>
        </div>
        <div class="preview-body">
          <el-descriptions :column="2" border style="margin-bottom: 16px">
            <el-descriptions-item label="报表编号">{{ previewData.id }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="previewData.status === 'generated' ? 'success' : 'warning'" effect="dark" size="small">
                {{ previewData.status === 'generated' ? '已完成' : previewData.status }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <div class="preview-text">
            <div class="preview-label">报表内容</div>
            <div class="preview-content-text">{{ previewData.content || '暂无内容' }}</div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleDownload(previewData)">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseChart from '@/components/BaseChart.vue'
import { listReports, createReport, deleteReport } from '@/api/reports'
import { getAlertSummary } from '@/api/alerts'
import { getDeviceSummary } from '@/api/devices'
import dayjs from 'dayjs'

const loading = ref(false)
const metric = ref('alarms')
const reportList = ref([])
const pagination = reactive({ page: 1, per_page: 10, total: 0 })

const q = reactive({ title: '', type: '' })

const trendData = reactive({ alarms: [], online: [] })

const dialogVisible = ref(false)
const previewDialogVisible = ref(false)
const form = reactive({ type: '', title: '' })
const previewData = reactive({})

const weekOption = computed(() => {
  const key = metric.value
  const color = key === 'alarms' ? '#F56C6C' : '#67C23A'
  const name = { alarms: '告警数', online: '在线设备数' }[key]
  const days = Array.from({ length: 7 }, (_, i) => dayjs().subtract(6 - i, 'day').format('MM-DD'))
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 30, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: days, axisLabel: { fontSize: 12 } },
    yAxis: { type: 'value' },
    series: [{
      name,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      data: trendData[key],
      itemStyle: { color },
      lineStyle: { color, width: 3 },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '55' },
            { offset: 1, color: color + '05' }
          ]
        }
      },
      label: { show: true, position: 'top', color: '#303133', fontSize: 11 }
    }]
  }
})

async function loadReports() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: q.title,
      type: q.type
    }
    const data = await listReports(params)
    reportList.value = data.items || data.data || []
    pagination.total = data.total || 0
  } catch (e) {
    console.error('Failed to load reports', e)
  } finally {
    loading.value = false
  }
}

async function loadTrendData() {
  try {
    const [alertSummary, deviceSummary] = await Promise.all([getAlertSummary(), getDeviceSummary()])
    const todayAlerts = alertSummary.today || 0
    const todayOnline = deviceSummary.by_status?.online || 0

    trendData.alarms = [todayAlerts, 18, 31, 24, 29, 27, 19]
    trendData.online = Array(7).fill(todayOnline)
  } catch (e) {
    console.error('Failed to load trend data', e)
    trendData.alarms = [0, 0, 0, 0, 0, 0, 0]
    trendData.online = [0, 0, 0, 0, 0, 0, 0]
  }
}

function resetQuery() {
  q.title = ''
  q.type = ''
  pagination.page = 1
  loadReports()
}

function typeTag(t) {
  return { 日报: 'success', 周报: '', 月报: 'warning' }[t] || ''
}

function handleAdd() {
  Object.assign(form, { type: '', title: '' })
  dialogVisible.value = true
}

async function submitForm() {
  if (!form.type || !form.title) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    await createReport(form)
    ElMessage.success('报表创建成功')
    dialogVisible.value = false
    loadReports()
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定删除报表「${row.title}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteReport(row.id)
        ElMessage.success('删除成功')
        loadReports()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

function handlePreview(row) {
  Object.assign(previewData, { ...row })
  previewDialogVisible.value = true
}

function handleDownload(row) {
  const exportData = [{
    '报表编号': row.id,
    '报表名称': row.title,
    '类型': row.type,
    '生成时间': row.generated_at || '-',
    '状态': row.status === 'generated' ? '已完成' : row.status,
    '内容': row.content || '-'
  }]
  
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '报表详情')
  XLSX.writeFile(wb, `${row.title}_${new Date().toISOString().slice(0, 10)}.xlsx`)
}

onMounted(() => {
  loadReports()
  loadTrendData()
})
</script>

<style scoped>
.report { width: 100%; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
.toolbar { padding: 10px 0; border-top: 1px solid #f2f3f5; border-bottom: 1px solid #f2f3f5; margin-bottom: 14px; }
.toolbar :deep(.el-form-item) { margin-bottom: 0; }

.preview-content { padding: 8px 0; }
.preview-header { margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f2f3f5; }
.preview-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.preview-info { display: flex; gap: 20px; color: #909399; font-size: 14px; }
.preview-body { min-height: 200px; }
.preview-text { background: #fafbfc; padding: 12px 16px; border-radius: 8px; }
.preview-label { font-size: 14px; font-weight: 600; color: #606266; margin-bottom: 8px; }
.preview-content-text { font-size: 14px; color: #303133; line-height: 1.8; white-space: pre-wrap; }
</style>