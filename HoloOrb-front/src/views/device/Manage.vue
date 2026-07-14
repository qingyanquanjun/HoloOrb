<template>
  <div class="device-manage">
    <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px">
      <template #title>本页面集中管理设备的增删操作，与「设备列表」共享同一份数据。</template>
    </el-alert>

    <el-row :gutter="16">
      <el-col :span="6" v-for="c in cards" :key="c.label">
        <div class="m-card" :style="{ borderLeft: `4px solid ${c.color}` }">
          <div class="m-label">{{ c.label }}</div>
          <div class="m-value" :style="{ color: c.color }">{{ c.value }}</div>
        </div>
      </el-col>
    </el-row>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Plus /></el-icon> 快速添加设备</span>
      </div>
      <el-form :model="addForm" label-width="100px" inline>
        <el-form-item label="设备名称">
          <el-input v-model="addForm.name" placeholder="输入名称" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="addForm.type" placeholder="选择类型" style="width: 180px">
            <el-option v-for="t in deviceTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP 地址">
          <el-input v-model="addForm.ip" placeholder="例如 10.0.0.1" />
        </el-form-item>
        <el-form-item label="区域">
          <el-input v-model="addForm.area" placeholder="区域" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="quickAdd">确认添加</el-button>
          <el-button @click="resetAdd">清空</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Delete /></el-icon> 批量删除设备</span>
        <div>
          <el-button size="small" type="danger" :disabled="!selected.length" @click="batchDelete">
            <el-icon><Delete /></el-icon> 批量删除选中 ({{ selected.length }})
          </el-button>
        </div>
      </div>
      <el-table :data="deviceList" @selection-change="(v) => (selected = v)" stripe v-loading="loading">
        <el-table-column type="selection" width="48" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" width="140" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="ip" label="IP" width="140" />
        <el-table-column prop="area" label="区域" width="120" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusT(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="接入时间" width="160" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" size="small" @click="removeOne(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @size-change="loadDevices"
        @current-change="loadDevices"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listDevices, createDevice, deleteDevice } from '@/api/devices'

const loading = ref(false)
const deviceList = ref([])
const selected = ref([])
const pagination = reactive({ page: 1, per_page: 10, total: 0 })

const deviceTypes = ['服务器', '交换机', '路由器', '无线AP', '防火墙', '存储', 'UPS']

const cards = computed(() => [
  { label: '总设备数', value: pagination.total, color: '#409EFF' },
  { label: '在线设备', value: deviceList.value.filter((d) => d.status === 'online').length, color: '#67C23A' },
  { label: '告警设备', value: deviceList.value.filter((d) => d.status === 'warning').length, color: '#F56C6C' },
  { label: '离线设备', value: deviceList.value.filter((d) => d.status === 'offline').length, color: '#909399' }
])

const addForm = reactive({ name: '', type: '', ip: '', area: '' })

function resetAdd() {
  addForm.name = ''
  addForm.type = ''
  addForm.ip = ''
  addForm.area = ''
}

async function quickAdd() {
  if (!addForm.name || !addForm.type || !addForm.ip) {
    ElMessage.warning('名称/类型/IP 为必填项')
    return
  }
  try {
    await createDevice({
      name: addForm.name,
      type: addForm.type,
      ip: addForm.ip,
      area: addForm.area || '',
      status: 'online'
    })
    ElMessage.success('添加成功')
    resetAdd()
    loadDevices()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

function statusT(s) {
  return { online: 'success', offline: 'info', warning: 'danger', maintenance: 'warning' }[s] || ''
}

function statusText(s) {
  return { online: '在线', offline: '离线', warning: '告警', maintenance: '维护中' }[s] || s
}

async function loadDevices() {
  loading.value = true
  try {
    const data = await listDevices({ page: pagination.page, per_page: pagination.per_page })
    deviceList.value = data.items || data.data || []
    pagination.total = data.total || 0
  } catch (e) {
    console.error('Failed to load devices', e)
  } finally {
    loading.value = false
  }
}

function removeOne(row) {
  ElMessageBox.confirm(`删除「${row.name}」？`, '确认', { type: 'warning' })
    .then(async () => {
      try {
        await deleteDevice(row.id)
        ElMessage.success('已删除')
        loadDevices()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

function batchDelete() {
  ElMessageBox.confirm(`确定删除选中的 ${selected.value.length} 台设备？`, '批量删除', { type: 'warning' })
    .then(async () => {
      try {
        for (const d of selected.value) {
          await deleteDevice(d.id)
        }
        ElMessage.success(`已删除 ${selected.value.length} 台设备`)
        selected.value = []
        loadDevices()
      } catch (e) {
        ElMessage.error('批量删除失败')
      }
    })
    .catch(() => {})
}

onMounted(() => {
  loadDevices()
})
</script>

<style scoped>
.device-manage {
  width: 100%;
}
.m-card {
  background: #fff;
  padding: 16px 18px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}
.m-label {
  color: #909399;
  font-size: 13px;
  margin-bottom: 6px;
}
.m-value {
  font-size: 28px;
  font-weight: 700;
}
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
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
  display: flex;
  align-items: center;
  gap: 6px;
}
:deep(.el-form--inline .el-form-item) {
  margin-bottom: 12px;
}
</style>