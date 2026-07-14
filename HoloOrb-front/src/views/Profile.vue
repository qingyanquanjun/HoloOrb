<template>
  <div class="profile-page">
    <div class="panel">
      <div class="profile-header">
        <el-avatar :size="100" style="background: #409EFF">
          {{ userData.name ? userData.name.charAt(0) : 'A' }}
        </el-avatar>
        <div class="profile-info">
          <div class="profile-name">{{ userData.name }}</div>
          <div class="profile-role">{{ userData.role }}</div>
          <div class="profile-email">{{ userData.email }}</div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Setting /></el-icon> 账户设置</span>
        <el-button type="primary" size="small" @click="openPasswordDialog">修改密码</el-button>
      </div>
      <el-form :model="form" label-width="120px" size="default">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="真实姓名" required>
          <el-input v-model="form.name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱" required>
          <el-input v-model="form.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="角色">
          <el-input v-model="form.role" disabled />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存修改</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-dialog v-model="passwordDialog" title="修改密码" width="400px" destroy-on-close>
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="新密码" required>
          <el-input v-model="passwordForm.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="确认密码" required>
          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPasswordChange">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { resetPassword, updateUser } from '@/api/users'

const userStore = useUserStore()

const userData = reactive({
  username: '',
  name: '',
  role: '',
  email: ''
})

const form = reactive({
  username: '',
  name: '',
  email: '',
  role: ''
})

const passwordDialog = ref(false)
const passwordForm = reactive({
  password: '',
  confirm_password: ''
})

function resetForm() {
  form.username = userData.username
  form.name = userData.name
  form.email = userData.email
  form.role = userData.role
}

function openPasswordDialog() {
  passwordForm.password = ''
  passwordForm.confirm_password = ''
  passwordDialog.value = true
}

async function submitPasswordChange() {
  if (!passwordForm.password || passwordForm.password.length < 6) {
    ElMessage.warning('密码至少6位')
    return
  }
  if (passwordForm.password !== passwordForm.confirm_password) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      ElMessage.error('用户信息无效')
      return
    }
    await resetPassword(userId, { password: passwordForm.password })
    ElMessage.success('密码修改成功，请重新登录')
    passwordDialog.value = false
    userStore.logout()
    window.location.href = '/login'
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '修改密码失败')
  }
}

async function handleSave() {
  if (!form.name || !form.email) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    await updateUser(userData.username, {
      email: form.email,
      name: form.name
    })
    userData.name = form.name
    userData.email = form.email
    ElMessage.success('账户信息修改成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '修改失败')
  }
}

onMounted(() => {
  userData.username = userStore.userInfo?.username || ''
  userData.name = userStore.userInfo?.name || userStore.userInfo?.username || ''
  userData.role = userStore.userInfo?.role || ''
  userData.email = userStore.userInfo?.email || ''
  resetForm()
})
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}
.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px 0;
}
.profile-info {
  flex: 1;
}
.profile-name {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}
.profile-role {
  font-size: 14px;
  color: #409EFF;
  margin-bottom: 4px;
}
.profile-email {
  font-size: 14px;
  color: #909399;
}
</style>