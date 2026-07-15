<template>
  <div class="backup">
    <!-- 快速操作卡 -->
    <el-row :gutter="16">
      <el-col :xs="12" :sm="6" v-for="c in cards" :key="c.label">
        <div class="b-card" @click="quickAction(c.label)">
          <el-icon :size="28" :style="{ color: c.color }"><component :is="c.icon" /></el-icon>
          <div class="b-label">{{ c.label }}</div>
          <div class="b-desc">{{ c.desc }}</div>
        </div>
      </el-col>
    </el-row>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Box /></el-icon> 备份记录</span>
        <div>
          <el-button size="small" plain @click="loadRecords"><el-icon><Refresh /></el-icon> 刷新</el-button>
          <el-button size="small" type="primary" @click="handleBackup"><el-icon><Upload /></el-icon> 立即备份</el-button>
        </div>
      </div>
      <el-table :data="records" stripe>
        <el-table-column type="index" width="60" label="#" />
        <el-table-column prop="name" label="备份名称" min-width="260" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="typeT(row.type)">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120" />
        <el-table-column prop="time" label="执行时间" width="200" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag type="success" effect="dark" size="small">
              <el-icon><CircleCheck /></el-icon> {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleDownload(row.id)">下载</el-button>
            <el-button link type="primary" size="small">校验</el-button>
            <el-button link type="warning" size="small">恢复</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head"><span class="panel-title">⚙️ 自动备份计划</span></div>
      <el-form label-width="140px" style="max-width: 680px">
        <el-form-item label="启用自动备份">
          <el-switch v-model="autoBackup.enabled" />
        </el-form-item>
        <el-form-item label="备份周期">
          <el-radio-group v-model="autoBackup.period">
            <el-radio value="daily">每日</el-radio>
            <el-radio value="weekly">每周</el-radio>
            <el-radio value="monthly">每月</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="执行时间">
          <el-time-picker v-model="autoBackup.time" placeholder="选择时间" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="备份内容">
          <el-checkbox-group v-model="autoBackup.items">
            <el-checkbox value="配置">设备配置</el-checkbox>
            <el-checkbox value="数据">数据库</el-checkbox>
            <el-checkbox value="日志">系统日志</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="保留数量">
          <el-input-number v-model="autoBackup.keep" :min="1" :max="100" />
          <span style="color: #909399; font-size: 12px; margin-left: 8px">份，超出自动清理最早备份</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSchedule">保存计划</el-button>
          <el-button @click="resetSchedule">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listBackups,
  createBackup,
  downloadBackup,
  deleteBackup,
  getSchedule,
  updateSchedule,
} from '@/api/backup'

const cards = [
  { label: '配置备份', icon: 'Setting', color: '#409EFF', desc: '导出全部设备配置' },
  { label: '数据备份', icon: 'Coin', color: '#67C23A', desc: '数据库全量快照' },
  { label: '日志归档', icon: 'Notebook', color: '#E6A23C', desc: '日志打包归档' },
  { label: '立即恢复', icon: 'RefreshRight', color: '#F56C6C', desc: '从备份点还原' }
]

const records = ref([])

const autoBackup = reactive({
  enabled: false,
  period: 'daily',
  time: '02:00',
  items: ['配置'],
  keep: 30
})

const defaultSchedule = {
  enabled: false,
  period: 'daily',
  time: '02:00',
  items: ['配置'],
  keep: 30
}

function typeT(t) {
  return { 配置: '', 数据: 'warning', 日志: 'info' }[t] || ''
}

async function loadRecords() {
  try {
    const data = await listBackups()
    records.value = data || []
  } catch (e) {
    ElMessage.error('加载备份记录失败')
  }
}

async function handleBackup() {
  try {
    await ElMessageBox.confirm('确定要执行备份吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    const data = await createBackup({ type: '配置' })
    ElMessage.success('备份成功')
    records.value.unshift(data)
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('备份失败')
    }
  }
}

function quickAction(label) {
  const typeMap = {
    '配置备份': '配置',
    '数据备份': '数据',
    '日志归档': '日志'
  }
  const backupType = typeMap[label]
  if (backupType) {
    createBackupByType(backupType)
  } else {
    ElMessage.info('恢复功能开发中')
  }
}

async function createBackupByType(type) {
  try {
    await ElMessageBox.confirm(`确定要执行${type}备份吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    const data = await createBackup({ type })
    ElMessage.success(`${type}备份成功`)
    records.value.unshift(data)
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(`${type}备份失败`)
    }
  }
}

async function handleDownload(id) {
  try {
    const response = await downloadBackup(id)
    const blob = new Blob([response], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `backup-${id}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定要删除该备份吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteBackup(id)
    ElMessage.success('删除成功')
    loadRecords()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function loadSchedule() {
  try {
    const data = await getSchedule()
    Object.assign(autoBackup, data)
  } catch (e) {
    console.error('加载备份计划失败', e)
  }
}

async function saveSchedule() {
  try {
    await updateSchedule({ ...autoBackup })
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

function resetSchedule() {
  Object.assign(autoBackup, defaultSchedule)
}

onMounted(() => {
  loadRecords()
  loadSchedule()
})
</script>

<style scoped>
.backup { width: 100%; }
.b-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}
.b-card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,0.08); }
.b-label { font-size: 15px; font-weight: 600; color: #303133; margin-top: 6px; }
.b-desc { font-size: 12px; color: #909399; margin-top: 2px; }

.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
</style>