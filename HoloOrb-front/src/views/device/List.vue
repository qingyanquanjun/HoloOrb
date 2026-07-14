<template>
  <div class="device-page">
    <div class="panel query-panel">
      <el-form :inline="true" :model="query" label-width="80px" size="default">
        <el-form-item label="设备名称">
          <el-input v-model="query.keyword" placeholder="输入名称/IP" clearable style="width: 200px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="query.type" placeholder="全部" clearable style="width: 160px">
            <el-option v-for="t in deviceTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="s in deviceStatusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属区域">
          <el-input v-model="query.area" placeholder="输入区域" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadDevices"><el-icon><Search /></el-icon> 查询</el-button>
          <el-button @click="resetQuery"><el-icon><RefreshLeft /></el-icon> 重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="panel">
      <div class="panel-head">
        <span class="panel-title">
          设备列表
          <el-tag type="info" size="small" style="margin-left: 8px">共 {{ pagination.total }} 条</el-tag>
        </span>
        <div class="panel-actions">
          <el-button size="small" @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>
          <el-button size="small" type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 添加设备
          </el-button>
        </div>
      </div>

      <el-table :data="deviceList" stripe style="width: 100%" v-loading="loading">
        <el-table-column type="selection" width="48" />
        <el-table-column prop="id" label="设备ID" width="80" />
        <el-table-column prop="name" label="设备名称" width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP 地址" width="150" />
        <el-table-column prop="area" label="所属区域" width="110" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="dark" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="接口" width="100">
          <template #default="{ row }">
            {{ row.in_use_interfaces || 0 }}/{{ row.interfaces || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="温度" width="80" />
        <el-table-column prop="uptime" label="运行时长" width="120" />
        <el-table-column prop="created_at" label="接入时间" width="160" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="loadDevices"
        @current-change="loadDevices"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px" destroy-on-close>
      <el-form :model="form" label-width="100px" size="default">
        <el-form-item label="设备名称" required>
          <el-input v-model="form.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型" required>
          <el-select v-model="form.type" placeholder="请选择" style="width: 100%">
            <el-option v-for="t in deviceTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP 地址" required>
          <el-input v-model="form.ip" placeholder="例如 10.0.0.1" />
        </el-form-item>
        <el-form-item label="所属区域">
          <el-input v-model="form.area" placeholder="请输入区域" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio v-for="s in deviceStatusOptions" :key="s.value" :label="s.value">{{ s.label }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="接口总数">
          <el-input-number v-model="form.interfaces" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="使用中接口">
          <el-input-number v-model="form.in_use_interfaces" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="viewDialogVisible" title="设备详情" width="600px" destroy-on-close>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="设备ID">{{ viewData.id }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ viewData.name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ viewData.type }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ viewData.ip }}</el-descriptions-item>
        <el-descriptions-item label="所属区域">{{ viewData.area || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(viewData.status)" effect="dark" size="small">{{ statusText(viewData.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="接口总数">{{ viewData.interfaces || 0 }}</el-descriptions-item>
        <el-descriptions-item label="使用中接口">{{ viewData.in_use_interfaces || 0 }}</el-descriptions-item>
        <el-descriptions-item label="温度">{{ viewData.temperature || '-' }}</el-descriptions-item>
        <el-descriptions-item label="运行时长">{{ viewData.uptime || '-' }}</el-descriptions-item>
        <el-descriptions-item label="接入时间">{{ viewData.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ viewData.description || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listDevices, createDevice, updateDevice, deleteDevice } from '@/api/devices'

const loading = ref(false)
const deviceList = ref([])

const deviceTypes = ['服务器', '交换机', '路由器', '无线AP', '防火墙', '存储', 'UPS']
const deviceStatusOptions = [
  { value: 'online', label: '在线' },
  { value: 'offline', label: '离线' },
  { value: 'warning', label: '告警' },
  { value: 'maintenance', label: '维护中' }
]

const query = reactive({ keyword: '', type: '', status: '', area: '' })
const pagination = reactive({ page: 1, per_page: 10, total: 0 })

const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = computed(() => (isEdit.value ? '编辑设备' : '添加设备'))
const form = reactive({ id: null, name: '', type: '', ip: '', area: '', status: 'online', interfaces: 0, in_use_interfaces: 0, description: '' })
const viewData = reactive({})

function resetQuery() {
  query.keyword = ''
  query.type = ''
  query.status = ''
  query.area = ''
  pagination.page = 1
  loadDevices()
}

function statusType(s) {
  return { online: 'success', offline: 'info', warning: 'danger', maintenance: 'warning' }[s] || ''
}

function statusText(s) {
  return { online: '在线', offline: '离线', warning: '告警', maintenance: '维护中' }[s] || s
}

async function loadDevices() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: query.keyword,
      type: query.type,
      status: query.status,
      area: query.area
    }
    const data = await listDevices(params)
    deviceList.value = data.items || data.data || []
    pagination.total = data.total || 0
  } catch (e) {
    console.error('Failed to load devices', e)
    ElMessage.error('加载设备列表失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  Object.assign(form, { id: null, name: '', type: '', ip: '', area: '', status: 'online', interfaces: 0, in_use_interfaces: 0, description: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

function handleView(row) {
  Object.assign(viewData, { ...row })
  viewDialogVisible.value = true
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定删除设备「${row.name}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteDevice(row.id)
        ElMessage.success('删除成功')
        loadDevices()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

function handleExport() {
  const exportData = deviceList.value.map(item => ({
    '设备ID': item.id,
    '设备名称': item.name,
    '类型': item.type,
    'IP地址': item.ip,
    '所属区域': item.area || '-',
    '状态': statusText(item.status),
    '接口总数': item.interfaces || 0,
    '使用中接口': item.in_use_interfaces || 0,
    '温度': item.temperature || '-',
    '运行时长': item.uptime || '-',
    '接入时间': item.created_at || '-'
  }))
  
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '设备列表')
  XLSX.writeFile(wb, `设备列表_${new Date().toISOString().slice(0, 10)}.xlsx`)
}

async function submitForm() {
  if (!form.name || !form.type || !form.ip) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    if (isEdit.value) {
      await updateDevice(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createDevice(form)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadDevices()
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
  }
}

onMounted(() => {
  loadDevices()
})
</script>

<style scoped>
.device-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}
.query-panel :deep(.el-form-item) {
  margin-bottom: 0;
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
  display: flex;
}
</style>