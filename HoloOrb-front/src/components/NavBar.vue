<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const navItems = [
  { name: 'HomePage', label: '首页', path: '/' },
  { name: 'Demo', label: '演示', path: '/demo' },
  { name: 'About', label: '关于', path: '/about' }
]

const isActive = (path) => computed(() => route.path === path)
</script>

<template>
  <header class="navbar">
    <div class="nav-inner">
      <RouterLink to="/" class="logo">
        <span class="logo-icon">🌀</span>
        <span class="logo-text">HoloOrb</span>
      </RouterLink>
      <nav class="nav-links">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          class="nav-link"
          :class="{ active: isActive(item.path).value }"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  background: #ffffff;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: saturate(180%) blur(12px);
  background: rgba(255, 255, 255, 0.9);
}
.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  font-weight: 700;
  font-size: 20px;
  color: #2c3e50;
}
.logo-icon {
  font-size: 24px;
}
.nav-links {
  display: flex;
  gap: 8px;
}
.nav-link {
  padding: 8px 16px;
  color: #555;
  text-decoration: none;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s ease;
}
.nav-link:hover {
  background: #f0f4ff;
  color: #4f46e5;
}
.nav-link.active {
  background: #4f46e5;
  color: #fff;
}
</style>
