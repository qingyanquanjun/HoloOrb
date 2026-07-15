<template>
  <div class="rules">
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><AlarmClock /></el-icon> 告警规则列表</span>
        <el-button type="primary" size="small" disabled><el-icon><Plus /></el-icon> 新建规则</el-button>
      </div>
      <el-table :data="list" stripe>
        <el-table-column type="index" width="60" label="#" />
        <el-table-column prop="name" label="规则名称" min-width="220" />
        <el-table-column width="90" label="级别">
          <template #default="{ row }">
            <el-tag :type="levelTag(row.level)" effect="dark" size="small">{{ levelText(row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="适用范围" width="150" />
        <el-table-column label="通知方式" min-width="220">
          <template #default="{ row }">
            <el-tag size="small" v-for="n in row.notify" :key="n" style="margin-right: 6px">{{ n }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="启用" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="(v)=>onToggle(row,v)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="matchLogs(row)">匹配日志</el-button>
            <el-button link type="primary" size="small" @click="editRule(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head"><span class="panel-title">📝 规则模板</span></div>
      <el-descriptions :column="2" border size="default">
        <el-descriptions-item label="CPU 阈值模板">
          <code>cpu.usage > {X}% for {N}min</code>
          <el-button link type="primary" size="small" style="margin-left: 8px">使用此模板</el-button>
        </el-descriptions-item>
        <el-descriptions-item label="磁盘阈值模板">
          <code>disk.free_pct < {X}%</code>
          <el-button link type="primary" size="small" style="margin-left: 8px">使用此模板</el-button>
        </el-descriptions-item>
        <el-descriptions-item label="设备离线模板">
          <code>device.online = false for {N}min</code>
          <el-button link type="primary" size="small" style="margin-left: 8px">使用此模板</el-button>
        </el-descriptions-item>
        <el-descriptions-item label="网络丢包模板">
          <code>iface.loss_pct > {X}%</code>
          <el-button link type="primary" size="small" style="margin-left: 8px">使用此模板</el-button>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <el-dialog v-model="editDialogVisible" title="编辑告警规则" width="500px" destroy-on-close>
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="规则名称" required>
          <el-input v-model="editForm.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="告警级别" required>
          <el-select v-model="editForm.level" placeholder="请选择告警级别">
            <el-option label="严重" value="danger" />
            <el-option label="警告" value="warning" />
            <el-option label="提示" value="info" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用范围" required>
          <el-input v-model="editForm.target" placeholder="如：所有服务器" />
        </el-form-item>
        <el-form-item label="通知方式">
          <el-checkbox-group v-model="editForm.notify">
            <el-checkbox label="邮件" />
            <el-checkbox label="短信" />
            <el-checkbox label="钉钉" />
          </el-checkbox-group>
        </el-form-item>
        <el-form-item>
          <el-switch v-model="editForm.enabled" />
          <span style="margin-left: 8px">启用规则</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="matchDialogVisible" title="规则匹配结果" width="650px" destroy-on-close>
      <div class="match-content">
        <div class="match-header">
          <span class="match-rule">规则：{{ currentRuleName }}</span>
          <span class="match-count">扫描 {{ currentMatchScanned }} 条，匹配到 {{ currentMatchCount }} 条</span>
        </div>
        <div class="match-list">
          <div v-for="(item, idx) in matchResults" :key="idx" class="match-item">
            <span class="match-time">{{ item.time }}</span>
            <span class="match-device">{{ item.device }}</span>
            <span class="match-message">{{ item.message }}</span>
            <el-tag :type="levelTag(item.level)" size="small" effect="dark">{{ levelText(item.level) }}</el-tag>
          </div>
          <div v-if="matchResults.length === 0" class="match-empty">暂无匹配日志</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="matchDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRules, matchRule, updateRule, deleteRule as apiDeleteRule } from '@/api/tasks'

const list = ref([])

const editDialogVisible = ref(false)
const matchDialogVisible = ref(false)
const currentEditId = ref(null)
const currentRuleName = ref('')
const currentMatchCount = ref(0)
const currentMatchScanned = ref(0)
const matchResults = ref([])

const editForm = reactive({
  name: '',
  level: '',
  target: '',
  notify: [],
  enabled: false
})

function levelTag(l) {
  return { danger: 'danger', warning: 'warning', info: 'info' }[l] || 'info'
}

function levelText(l) {
  return { danger: '严重', warning: '警告', info: '提示' }[l] || l
}

async function loadRules() {
  try {
    const res = await getRules()
    list.value = res.items
  } catch {
    list.value = []
  }
}

function onToggle(row, v) {
  ElMessage.success(`规则「${row.name}」已${v ? '启用' : '禁用'}`)
}

async function matchLogs(row) {
  currentRuleName.value = row.name
  try {
    const res = await matchRule(row.id)
    matchResults.value = res.matches
    currentMatchCount.value = res.matched
    currentMatchScanned.value = res.scanned
    ElMessage.info(res.message)
  } catch {
    matchResults.value = []
    currentMatchCount.value = 0
    currentMatchScanned.value = 0
    ElMessage.warning('匹配失败，请检查后端服务')
  }
  matchDialogVisible.value = true
}

function editRule(row) {
  currentEditId.value = row.id
  editForm.name = row.name
  editForm.level = row.level
  editForm.target = row.target
  editForm.notify = [...row.notify]
  editForm.enabled = row.enabled
  editDialogVisible.value = true
}

async function saveEdit() {
  if (!editForm.name || !editForm.level || !editForm.target) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await updateRule(currentEditId.value, {
      name: editForm.name,
      level: editForm.level,
      target: editForm.target,
      notify: editForm.notify,
      enabled: editForm.enabled
    })
    const idx = list.value.findIndex(item => item.id === currentEditId.value)
    if (idx !== -1) {
      list.value[idx].name = editForm.name
      list.value[idx].level = editForm.level
      list.value[idx].target = editForm.target
      list.value[idx].notify = [...editForm.notify]
      list.value[idx].enabled = editForm.enabled
    }
    ElMessage.success('修改成功')
    editDialogVisible.value = false
  } catch {
    ElMessage.error('修改失败')
  }
}

async function deleteRule(row) {
  try {
    await ElMessageBox.confirm(`确定要删除告警规则「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await apiDeleteRule(row.id)
    list.value = list.value.filter(item => item.id !== row.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.rules { width: 100%; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
code {
  background: #f2f3f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  color: #409EFF;
  font-family: Consolas, Monaco, monospace;
}

.match-content {
  padding: 8px;
}
.match-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}
.match-rule { font-weight: 600; color: #303133; }
.match-count { font-size: 13px; color: #409EFF; }
.match-list {
  max-height: 300px;
  overflow-y: auto;
}
.match-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  margin-bottom: 8px;
  background: #f7f8fa;
  border-radius: 8px;
  font-size: 13px;
}
.match-time {
  color: #909399;
  flex-shrink: 0;
  width: 140px;
}
.match-device {
  color: #409EFF;
  flex-shrink: 0;
  width: 110px;
}
.match-message { flex: 1; color: #303133; }
.match-empty { text-align: center; color: #909399; padding: 20px; }
</style>
