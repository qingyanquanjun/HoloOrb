<script setup>
import { RouterView } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
</script>

<template>
  <div class="layout">
    <NavBar />
    <main class="main">
      <RouterView />
    </main>
    <footer class="footer">
      <p>&copy; 2026 HoloOrb · Powered by Flask + Vue 3</p>
    </footer>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
  box-sizing: border-box;
}
.footer {
  padding: 24px;
  text-align: center;
  color: #888;
  font-size: 14px;
  border-top: 1px solid #eee;
}
</style>
