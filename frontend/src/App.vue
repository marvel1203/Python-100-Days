<template>
  <div id="app" class="app-shell">
    <el-container class="shell-container">
      <el-header class="shell-header">
        <AppHeader />
      </el-header>
      <el-container class="layout-body">
        <el-aside v-if="showSidebar" class="shell-aside">
          <AppSidebar />
        </el-aside>
        <el-main class="shell-main">
          <div class="main-content-card">
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </el-main>
      </el-container>
      <el-footer class="shell-footer">
        <AppFooter />
      </el-footer>
    </el-container>

    <!-- 悬浮按钮 -->
    <FloatingButton />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppSidebar from './components/layout/AppSidebar.vue'
import FloatingButton from './components/FloatingButton.vue'
import AppFooter from './components/layout/AppFooter.vue'

const route = useRoute()
const showSidebar = computed(() => !['/login', '/register'].includes(route.path))
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: radial-gradient(circle at 20% 20%, rgba(255, 211, 154, 0.35), transparent 55%),
    radial-gradient(circle at 80% 0%, rgba(144, 202, 255, 0.25), transparent 50%),
    #f4f6fb;
}

.shell-container {
  min-height: 100vh;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.shell-header,
.shell-footer {
  background: transparent;
  padding: 0;
  border: none;
}

.layout-body {
  max-width: 2000px;
  margin: 0 auto;
  width: 100%;
  background: transparent;
}

.shell-aside {
  width: 240px;
  background: transparent;
  border: none;
}

.shell-main {
  padding: 20px 24px 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow: visible;
}

.main-content-card {
  min-height: calc(100vh - 220px);
  background: linear-gradient(180deg, #ffffff 0%, #fcfdff 100%);
  border-radius: 26px;
  box-shadow: 0 40px 60px rgba(15, 23, 42, 0.12);
  padding: 36px 40px;
  width: 90%;
  margin: 0 auto;
  overflow: visible;
  transition: box-shadow 0.2s ease;
}

.main-content-card:hover {
  box-shadow: 0 46px 70px rgba(15, 23, 42, 0.16);
}

@media (max-width: 1024px) {
  .shell-main {
    padding: 24px 20px;
  }

  .main-content-card {
    width: 100%;
    padding: 28px 24px;
  }
}

.shell-footer {
  display: flex;
  justify-content: center;
  padding-bottom: 30px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<style>
:root {
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: #1f2937;
  background-color: #f4f6fb;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #f4f6fb;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.el-button--primary {
  background: linear-gradient(135deg, #ff915f 0%, #ff5f87 100%);
  border: none;
  box-shadow: 0 12px 24px rgba(255, 111, 145, 0.32);
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #ff7a4e 0%, #ff4f79 100%);
  box-shadow: 0 16px 28px rgba(255, 111, 145, 0.38);
}

.el-dialog {
  border-radius: 24px !important;
  overflow: hidden;
  box-shadow: 0 36px 60px rgba(15, 23, 42, 0.18);
  backdrop-filter: blur(20px);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(249, 250, 253, 0.9) 100%);
}

.el-dialog__header {
  margin-right: 0 !important;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  padding: 24px 28px 18px;
}

.el-dialog__body {
  padding: 24px 28px 12px;
}

.el-dialog__footer {
  padding: 0 28px 28px;
}

.el-overlay-dialog {
  backdrop-filter: blur(10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
