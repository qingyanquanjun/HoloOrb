<script setup>
</script>

<template>
  <div class="about">
    <h1>关于 HoloOrb</h1>
    <p class="lead">
      HoloOrb 是一个基于 Flask + Vue 3 的全栈项目脚手架，帮助你快速构建现代化 Web 应用。
    </p>

    <h2>技术栈</h2>
    <ul class="stack-list">
      <li><strong>后端</strong>：Flask 3 · Flask-SQLAlchemy · Flask-JWT-Extended · Flask-CORS</li>
      <li><strong>前端</strong>：Vue 3 · Vite · Vue Router 4 · Pinia · Axios</li>
      <li><strong>工具</strong>：python-dotenv · 应用工厂模式 · 蓝图分层</li>
    </ul>

    <h2>目录结构</h2>
    <h3>后端</h3>
    <pre class="code-block">HoloOrb/
├── app.py                  # 入口文件（应用工厂）
├── config.py               # 多环境配置
├── extensions.py           # Flask 扩展集中初始化
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量示例
├── run.bat                 # Windows 启动脚本
└── apps/
    ├── api/                # API 路由（蓝图）
    │   ├── __init__.py
    │   ├── health.py
    │   └── example.py
    ├── models/             # 数据模型
    │   ├── __init__.py
    │   └── base.py
    └── common/             # 通用工具
        ├── __init__.py
        └── response.py</pre>

    <h3>前端</h3>
    <pre class="code-block">HoloOrb-front/
├── index.html
├── vite.config.js          # Vite 配置（含代理）
├── package.json
└── src/
    ├── main.js
    ├── App.vue
    ├── router/index.js     # 路由配置
    ├── stores/             # Pinia 状态管理
    │   ├── app.js
    │   └── user.js
    ├── api/example.js      # 接口请求封装
    ├── utils/request.js    # Axios 封装
    ├── layouts/            # 布局
    │   └── DefaultLayout.vue
    ├── components/         # 组件
    │   └── NavBar.vue
    └── views/              # 页面
        ├── HomeView.vue
        ├── AboutView.vue
        └── DemoView.vue</pre>
  </div>
</template>

<style scoped>
.about {
  max-width: 860px;
}
h1 {
  font-size: 36px;
  color: #1f2937;
  margin: 0 0 16px;
}
h2 {
  font-size: 22px;
  color: #1f2937;
  margin: 32px 0 12px;
}
h3 {
  font-size: 17px;
  color: #374151;
  margin: 20px 0 8px;
}
.lead {
  font-size: 16px;
  color: #6b7280;
  line-height: 1.7;
}
.stack-list {
  line-height: 2;
  color: #374151;
}
.code-block {
  background: #1f2937;
  color: #e5e7eb;
  padding: 16px 20px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.7;
  overflow-x: auto;
  margin: 0;
}
</style>
