<script setup>
import { onMounted, ref } from 'vue'
import { healthCheck, sayHello } from '@/api/example'

const apiStatus = ref('pending')
const greeting = ref('')
const timestamp = ref('')

async function loadStatus() {
  try {
    const [health, hello] = await Promise.all([healthCheck(), sayHello('HoloOrb User')])
    apiStatus.value = health.status
    timestamp.value = health.timestamp
    greeting.value = hello.greeting
  } catch (e) {
    apiStatus.value = 'offline'
    greeting.value = '后端服务未启动'
  }
}

onMounted(loadStatus)
</script>

<template>
  <div class="home">
    <section class="hero">
      <div class="hero-left">
        <h1 class="title">
          欢迎来到 <span class="gradient">HoloOrb</span>
        </h1>
        <p class="subtitle">
          Flask 后端 · Vue 3 前端 · 全栈项目脚手架
        </p>
        <div class="badges">
          <span class="badge">Flask 3</span>
          <span class="badge">Vue 3</span>
          <span class="badge">Vite</span>
          <span class="badge">Pinia</span>
          <span class="badge">Axios</span>
        </div>
        <div class="status-card" @click="loadStatus">
          <div class="status-row">
            <span class="status-label">后端状态</span>
            <span class="status-value" :class="apiStatus">
              <span class="dot"></span>
              {{ apiStatus === 'healthy' ? '运行中' : apiStatus === 'pending' ? '检测中...' : '未连接' }}
            </span>
          </div>
          <div class="status-row" v-if="greeting">
            <span class="status-label">问候信息</span>
            <span class="status-value">{{ greeting }}</span>
          </div>
          <div class="status-row" v-if="timestamp">
            <span class="status-label">响应时间</span>
            <span class="status-value">{{ timestamp }}</span>
          </div>
          <p class="status-tip">点击卡片重新检测</p>
        </div>
      </div>
      <div class="hero-right">
        <div class="orb"></div>
      </div>
    </section>

    <section class="features">
      <h2>特性</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">🛠️</div>
          <h3>工程化结构</h3>
          <p>Flask 应用工厂模式 + 蓝图分层，Vue 3 Vite 脚手架 + 路由/状态管理/请求封装</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔐</div>
          <h3>安全配套</h3>
          <p>JWT 认证、CORS 跨域、统一响应格式、Axios 拦截器完整示例</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📦</div>
          <h3>ORM 就绪</h3>
          <p>Flask-SQLAlchemy 已集成，提供 Base 模型及 SQLite 开箱即用</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3>开发体验</h3>
          <p>前后端一键启动脚本、代理转发、热更新、自动打开浏览器</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 48px;
  align-items: center;
  padding: 40px 0 64px;
}
.title {
  font-size: 48px;
  line-height: 1.2;
  margin: 0 0 16px;
  color: #1f2937;
}
.gradient {
  background: linear-gradient(135deg, #4f46e5 0%, #ec4899 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.subtitle {
  font-size: 18px;
  color: #6b7280;
  margin: 0 0 24px;
}
.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 32px;
}
.badge {
  padding: 6px 14px;
  background: #f3f4f6;
  border-radius: 999px;
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}
.status-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 20px 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  max-width: 460px;
}
.status-card:hover {
  border-color: #4f46e5;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.08);
}
.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
}
.status-label {
  color: #6b7280;
}
.status-value {
  color: #1f2937;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-value.healthy {
  color: #10b981;
}
.status-value.offline {
  color: #ef4444;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9ca3af;
}
.status-value.healthy .dot {
  background: #10b981;
  animation: pulse 2s infinite;
}
.status-value.offline .dot {
  background: #ef4444;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.status-tip {
  margin: 12px 0 0;
  font-size: 12px;
  color: #9ca3af;
  text-align: right;
}
.hero-right {
  display: flex;
  justify-content: center;
  align-items: center;
}
.orb {
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #fff 0%, #a5b4fc 35%, #4f46e5 70%, #1e1b4b 100%);
  box-shadow:
    0 0 80px rgba(79, 70, 229, 0.4),
    inset -20px -40px 80px rgba(30, 27, 75, 0.5),
    inset 20px 20px 60px rgba(255, 255, 255, 0.3);
  animation: float 6s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16px); }
}
.features {
  padding: 32px 0;
}
.features h2 {
  font-size: 28px;
  color: #1f2937;
  margin: 0 0 24px;
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}
.feature-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.2s ease;
}
.feature-card:hover {
  border-color: #4f46e5;
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(79, 70, 229, 0.12);
}
.feature-icon {
  font-size: 36px;
  margin-bottom: 12px;
}
.feature-card h3 {
  font-size: 18px;
  color: #1f2937;
  margin: 0 0 8px;
}
.feature-card p {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 768px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .title {
    font-size: 36px;
  }
  .orb {
    width: 200px;
    height: 200px;
  }
}
</style>
