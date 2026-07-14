<template>
  <div class="users">
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><User /></el-icon> 用户管理</span>
        <div>
          <el-input v-model="q.username" placeholder="搜索用户" size="default" style="width: 200px; margin-right: 10px" clearable @keyup.enter="loadUsers">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button type="primary" size="default" @click="openAdd">
            <el-icon><Plus /></el-icon> 新增用户
          </el-button>
        </div>
      </div>
      <el-table :data="userList" stripe v-loading="loading">
        <el-table-column type="index" width="60" label="#" />
        <el-table-column label="账号" width="180">
          <template #default="{ row }">
            <div class="u-cell">
              <el-avatar :size="34" :style="{ background: avColor(row.id) }">{{ row.username.slice(0,1) }}</el-avatar>
              <div>
                <div class="u-name">{{ row.username }}</div>
                <div class="u-uname">ID: {{ row.id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="130">
          <template #default="{ row }">
            <el-tag size="small" :type="roleT(row.role)">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="220" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row._enabled" @change="(v)=>onStatus(row,v)" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @size-change="loadUsers"
        @current-change="loadUsers"
      />
    </div>

    <el-dialog v-model="dialog" :title="isEdit ? '编辑用户' : '新增用户'" width="540px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="管理员" value="管理员" />
            <el-option label="运维工程师" value="运维工程师" />
            <el-option label="普通用户" value="普通用户" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="初始密码" required>
          <el-input v-model="form.password" show-password placeholder="至少6位" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="onSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resetDialog" title="重置密码" width="400px" destroy-on-close>
      <el-form :model="resetForm" label-width="100px">
        <el-form-item label="新密码" required>
          <el-input v-model="resetForm.password" show-password placeholder="至少6位" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialog = false">取消</el-button>
        <el-button type="primary" @click="submitResetPassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listUsers, createUser, updateUser, deleteUser, resetPassword, updateUserStatus } from '@/api/users'

const loading = ref(false)
const q = reactive({ username: '' })
const userList = ref([])
const pagination = reactive({ page: 1, per_page: 10, total: 0 })

const dialog = ref(false)
const isEdit = ref(false)
const form = reactive({ id: null, username: '', email: '', role: '普通用户', password: '' })

const resetDialog = ref(false)
const resetForm = reactive({ password: '' })
const resetUserId = ref(null)

function avColor(id) {
  const cs = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#9B59B6']
  return cs[id % cs.length]
}

function roleT(r) {
  return { 管理员: 'danger', 运维工程师: 'warning', 普通用户: 'info' }[r] || ''
}

async function loadUsers() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      username: q.username
    }
    const data = await listUsers(params)
    userList.value = (data.items || data.data || []).map(u => ({
      ...u,
      _enabled: u.status === 'active'
    }))
    pagination.total = data.total || 0
  } catch (e) {
    console.error('Failed to load users', e)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function openAdd() {
  isEdit.value = false
  Object.assign(form, { id: null, username: '', email: '', role: '普通用户', password: '' })
  dialog.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    username: row.username,
    email: row.email,
    role: row.role,
    password: ''
  })
  dialog.value = true
}

function handleResetPassword(row) {
  resetUserId.value = row.id
  resetForm.password = ''
  resetDialog.value = true
}

async function submitResetPassword() {
  if (!resetForm.password || resetForm.password.length < 6) {
    ElMessage.warning('密码至少6位')
    return
  }
  try {
    await resetPassword(resetUserId.value, { password: resetForm.password })
    ElMessage.success('密码重置成功')
    resetDialog.value = false
  } catch (e) {
    ElMessage.error('重置密码失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定删除用户「${row.username}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteUser(row.id)
        ElMessage.success('删除成功')
        loadUsers()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

async function onSave() {
  if (!form.username) {
    ElMessage.warning('请填写用户名')
    return
  }
  if (!isEdit.value && (!form.password || form.password.length < 6)) {
    ElMessage.warning('密码至少6位')
    return
  }
  try {
    if (isEdit.value) {
      await updateUser(form.id, { email: form.email, role: form.role })
      ElMessage.success('更新成功')
    } else {
      await createUser(form)
      ElMessage.success('新增成功')
    }
    dialog.value = false
    loadUsers()
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '新增失败')
  }
}

async function onStatus(row, v) {
  try {
    await updateUserStatus(row.id, { status: v ? 'active' : 'disabled' })
    row.status = v ? 'active' : 'disabled'
    ElMessage.success(`用户「${row.username}」已${row.status === 'active' ? '启用' : '禁用'}`)
  } catch (e) {
    row._enabled = !v
    ElMessage.error('状态更新失败')
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users { width: 100%; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
.u-cell { display: flex; align-items: center; gap: 10px; }
.u-name { font-size: 14px; color: #303133; font-weight: 500; }
.u-uname { font-size: 12px; color: #909399; }
</style>