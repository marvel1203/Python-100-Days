<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="hero">
          <h1>Python - 100天从新手到大师</h1>
          <p class="subtitle">系统学习Python编程,从零基础到项目实战</p>
          <div class="actions">
            <el-button type="primary" size="large" @click="$router.push('/courses')">
              开始学习
            </el-button>
            <el-button size="large" @click="$router.push('/exercises')">
              练习题库
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="features">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon :size="32" color="#409eff"><Document /></el-icon>
              <span>系统化课程</span>
            </div>
          </template>
          <p>100天涵盖Python基础、进阶到项目实战</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon :size="32" color="#67c23a"><EditPen /></el-icon>
              <span>在线练习</span>
            </div>
          </template>
          <p>丰富的编程练习题库,边学边练,巩固知识</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon :size="32" color="#e6a23c"><TrendCharts /></el-icon>
              <span>学习追踪</span>
            </div>
          </template>
          <p>可视化学习进度,记录每一步成长</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { Document, EditPen, TrendCharts } from '@element-plus/icons-vue'
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 40px;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 20px;
}

.subtitle {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.features {
  margin-top: 40px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}
</style>
