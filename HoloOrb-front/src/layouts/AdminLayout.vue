<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside :width="collapsed ? '64px' : '220px'" class="aside">
      <div class="logo-wrap" :class="{ collapsed }">
        <el-icon class="logo-icon"><Aim /></el-icon>
        <span v-if="!collapsed" class="logo-text">HoloOrb</span>
      </div>
      <el-scrollbar class="menu-scroll">
        <el-menu
          :default-active="activeMenu"
          :collapse="collapsed"
          :collapse-transition="false"
          router
          background-color="#001529"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <template v-for="group in menuConfig" :key="group.path">
            <el-sub-menu v-if="group.children && group.children.length > 1" :index="group.path">
              <template #title>
                <el-icon><component :is="group.meta.icon" /></el-icon>
                <span>{{ group.meta.title }}</span>
              </template>
              <el-menu-item
                v-for="child in group.children"
                :key="child.path"
                :index="child.path"
              >
                <el-icon><component :is="child.meta.icon" /></el-icon>
                <template #title>{{ child.meta.title }}</template>
              </el-menu-item>
            </el-sub-menu>
            <!-- 只有一个子菜单时，直接显示为菜单项 -->
            <el-menu-item
              v-else-if="group.children && group.children.length === 1"
              :index="group.children[0].path"
            >
              <el-icon><component :is="group.children[0].meta.icon || group.meta.icon" /></el-icon>
              <template #title>{{ group.meta.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="collapsed = !collapsed">
            <component :is="collapsed ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="(b, i) in breadcrumbs" :key="i">{{ b }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <div class="user-info">
              <el-avatar :size="32" style="background: #409EFF">
                {{ userStore.userInfo?.name?.charAt(0) || userStore.userInfo?.username?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.name || userStore.userInfo?.username || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-item @click="goProfile"><el-icon><User /></el-icon>个人中心</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout"><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="main">
        <RouterView v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </RouterView>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { menuConfig } from '@/config/menu'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const list = ['首页']
  for (const g of menuConfig) {
    const child = (g.children || []).find((c) => c.path === route.path)
    if (child) {
      if (g.meta.title !== child.meta.title) {
        list.push(g.meta.title)
      }
      list.push(child.meta.title)
      break
    }
  }
  return list
})

function goProfile() {
  router.push('/profile')
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.aside {
  background: #001529;
  transition: width 0.25s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-wrap {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 10px;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}
.logo-wrap.collapsed {
  padding: 0;
  justify-content: center;
}
.logo-icon {
  font-size: 24px;
  color: #409EFF;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
  white-space: nowrap;
}

.menu-scroll {
  flex: 1;
  overflow: hidden;
}
:deep(.el-menu) {
  border-right: none;
}
:deep(.el-menu--collapse) {
  width: 64px;
}

.header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px !important;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
  transition: color 0.2s;
}
.collapse-btn:hover {
  color: #409EFF;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-icon {
  font-size: 18px;
  color: #606266;
  cursor: pointer;
  transition: color 0.2s;
}
.header-icon:hover {
  color: #409EFF;
}
.badge :deep(.el-badge__content) {
  margin-top: 4px;
  margin-right: 4px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}
.user-info:hover {
  background: #f5f7fa;
}
.username {
  font-size: 14px;
  color: #303133;
}

.main {
  background: #f0f2f5;
  padding: 20px;
  overflow: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
