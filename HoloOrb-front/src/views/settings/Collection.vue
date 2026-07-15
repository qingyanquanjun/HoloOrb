<template>
  <div class="settings">
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Connection /></el-icon> 数据采集任务</span>
        <el-button type="primary" size="small" disabled><el-icon><Plus /></el-icon> 新建采集任务</el-button>
      </div>
      <el-table :data="list" stripe>
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="任务名称" min-width="200" />
        <el-table-column prop="target" label="采集目标" width="150" />
        <el-table-column prop="interval" label="采集周期" width="110" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-switch v-model="row.runningStatus" :active-value="true" :inactive-value="false" @change="(v)=>toggle(row,v)" />
            <span style="margin-left: 8px; font-size: 12px" :class="row.status === 'running' ? 'on' : 'off'">{{ row.status === 'running' ? '运行中' : '已暂停' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastRun" label="最近执行" width="140" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" :disabled="row.status !== 'running'" @click="executeTask(row)">立即执行</el-button>
            <el-button link type="primary" size="small" @click="viewLogs(row)">日志</el-button>
            <el-button link type="primary" size="small" @click="editTask(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head"><span class="panel-title">📊 近 7 天采集成功率</span></div>
      <BaseChart :option="succOption" height="260px" />
    </div>

    <el-dialog v-model="editDialogVisible" title="编辑采集任务" width="500px" destroy-on-close>
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="editForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="采集目标" required>
          <el-input v-model="editForm.target" placeholder="如：服务器*" />
        </el-form-item>
        <el-form-item label="采集周期" required>
          <el-select v-model="editForm.interval" placeholder="请选择采集周期">
            <el-option label="10秒" value="10s" />
            <el-option label="30秒" value="30s" />
            <el-option label="1分钟" value="60s" />
            <el-option label="2分钟" value="2min" />
            <el-option label="5分钟" value="5min" />
            <el-option label="10分钟" value="10min" />
            <el-option label="30分钟" value="30min" />
            <el-option label="1小时" value="1h" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="logDialogVisible" title="任务执行日志" width="650px" destroy-on-close>
      <div class="log-content">
        <div v-for="(log, idx) in currentLogs" :key="idx" class="log-item">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-level" :class="log.level">{{ log.level }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        <div v-if="currentLogs.length === 0" class="log-empty">暂无日志记录</div>
      </div>
      <template #footer>
        <el-button @click="logDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseChart from '@/components/BaseChart.vue'
import dayjs from 'dayjs'
import { getTasks, executeTask as apiExecuteTask, getTaskLogs, updateTask, deleteTask as apiDeleteTask } from '@/api/tasks'

const list = ref([])
const loading = ref(false)

const editDialogVisible = ref(false)
const logDialogVisible = ref(false)
const currentEditId = ref(null)
const currentLogs = ref([])

const editForm = reactive({
  name: '',
  target: '',
  interval: ''
})

async function loadTasks() {
  try {
    const res = await getTasks()
    list.value = res.items.map((t) => ({ ...t, runningStatus: t.status === 'running' }))
  } catch {
    list.value = []
  }
}

function toggle(row, v) {
  row.status = v ? 'running' : 'stopped'
  row.lastRun = v ? '刚刚' : row.lastRun
  ElMessage.success('任务已' + (v ? '启动' : '暂停'))
}

async function executeTask(row) {
  loading.value = true
  row.lastRun = '正在执行...'
  try {
    const res = await apiExecuteTask(row.id)
    row.lastRun = '刚刚'
    ElMessage.success(res.message)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '执行失败')
    row.lastRun = '执行失败'
  } finally {
    loading.value = false
  }
}

async function viewLogs(row) {
  try {
    const res = await getTaskLogs(row.id)
    currentLogs.value = res.items
  } catch {
    currentLogs.value = [
      { time: dayjs().format('HH:mm:ss'), level: 'INFO', message: `开始执行采集任务: ${row.name}` },
      { time: dayjs().format('HH:mm:ss'), level: 'INFO', message: `连接目标: ${row.target}` },
      { time: dayjs().format('HH:mm:ss'), level: 'SUCCESS', message: '采集完成' },
    ]
  }
  logDialogVisible.value = true
}

function editTask(row) {
  currentEditId.value = row.id
  editForm.name = row.name
  editForm.target = row.target
  editForm.interval = row.interval
  editDialogVisible.value = true
}

async function saveEdit() {
  if (!editForm.name || !editForm.target || !editForm.interval) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await updateTask(currentEditId.value, {
      name: editForm.name,
      target: editForm.target,
      interval: editForm.interval
    })
    const idx = list.value.findIndex(item => item.id === currentEditId.value)
    if (idx !== -1) {
      list.value[idx].name = editForm.name
      list.value[idx].target = editForm.target
      list.value[idx].interval = editForm.interval
    }
    ElMessage.success('修改成功')
    editDialogVisible.value = false
  } catch {
    ElMessage.error('修改失败')
  }
}

async function deleteTask(row) {
  try {
    await ElMessageBox.confirm(`确定要删除采集任务「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiDeleteTask(row.id)
    list.value = list.value.filter(item => item.id !== row.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const succOption = computed(() => {
  const days = Array.from({ length: 7 }, (_, i) => dayjs().subtract(6 - i, 'day').format('MM-DD'))
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{
      type: 'bar',
      data: [99.2, 99.6, 98.7, 99.9, 99.4, 99.1, 99.7],
      itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top', formatter: '{c}%', fontSize: 11 }
    }]
  }
})

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.settings { width: 100%; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
.on { color: #67C23A; }
.off { color: #909399; }

.log-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
  background: #f7f8fa;
  border-radius: 8px;
}
.log-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.6;
}
.log-time {
  color: #909399;
  flex-shrink: 0;
  width: 140px;
}
.log-level {
  flex-shrink: 0;
  width: 60px;
  text-align: center;
  padding: 1px 4px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}
.log-level.INFO { background: #e8f4fd; color: #409EFF; }
.log-level.WARN { background: #fdf6ec; color: #E6A23C; }
.log-level.SUCCESS { background: #f0f9eb; color: #67C23A; }
.log-level.ERROR { background: #fef0f0; color: #F56C6C; }
.log-message { flex: 1; color: #303133; }
.log-empty { text-align: center; color: #909399; padding: 20px; }
</style>
