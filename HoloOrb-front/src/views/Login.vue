<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-header">
        <el-icon class="logo-icon"><Aim /></el-icon>
        <h1 class="title">HoloOrb</h1>
        <p class="subtitle">智能运维管理平台</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            type="text"
            placeholder="用户名"
            prefix-icon="User"
            :disabled="loading"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            :disabled="loading"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item class="remember-item">
          <el-checkbox v-model="form.remember">记住密码</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { login } from '@/api/users'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 3, max: 32, message: '密码长度为3-32个字符', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const res = await login(form)
      if (res.access_token) {
        userStore.setToken(res.access_token)
        userStore.setUserInfo(res.user || { username: form.username })
        if (form.remember) {
          localStorage.setItem('username', form.username)
        } else {
          localStorage.removeItem('username')
        }
        ElMessage.success('登录成功')
        router.push('/dashboard')
      } else {
        ElMessage.error('登录失败，请检查账号密码')
      }
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}

const savedUsername = localStorage.getItem('username')
if (savedUsername) {
  form.username = savedUsername
  form.remember = true
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-wrapper {
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 12px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.login-form :deep(.el-input__prefix) {
  color: #909399;
}

.remember-item {
  margin-bottom: 24px !important;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}


</style>