<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="dashboard-sidebar">
      <div style="padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="color: #67C23A; margin: 0;">医生端</h2>
      </div>
      <el-menu :default-active="activeMenu" @select="handleMenuSelect">
        <el-menu-item index="home">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="patients">
          <el-icon><User /></el-icon>
          <span>今日患者</span>
        </el-menu-item>
        <el-menu-item index="prescriptions">
          <el-icon><Tickets /></el-icon>
          <span>处方管理</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-main">
      <!-- 顶部导航 -->
      <div class="dashboard-header">
        <div>
          <el-text size="large">欢迎回来，{{ userStore.userName }}</el-text>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
          <el-dropdown @command="handleCommand">
            <span style="cursor: pointer; display: flex; align-items: center; gap: 8px;">
              <el-avatar :size="32">{{ userStore.userName.charAt(0) }}</el-avatar>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="dashboard-content">
        <!-- 加载状态 -->
        <el-skeleton v-if="loading" :rows="5" animated />

        <div v-else>
          <!-- 统计卡片 -->
          <div class="card-grid">
            <div class="stat-card">
              <el-icon :size="32" color="#409EFF"><User /></el-icon>
              <div class="stat-value">{{ statistics.todayPatients }}</div>
              <div class="stat-label">今日患者</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#67C23A"><Tickets /></el-icon>
              <div class="stat-value">{{ statistics.pendingPatients }}</div>
              <div class="stat-label">待接诊患者</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#E6A23C"><Document /></el-icon>
              <div class="stat-value">{{ statistics.pendingRecords }}</div>
              <div class="stat-label">待记录</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#F56C6C"><Bell /></el-icon>
              <div class="stat-value">{{ statistics.consultRequests }}</div>
              <div class="stat-label">咨询请求</div>
            </div>
          </div>

          <!-- 今日患者列表 -->
          <el-card style="margin-bottom: 20px;">
            <template #header>
              <span style="font-weight: bold;">今日患者列表</span>
            </template>
            <div v-if="todayPatients.length === 0" style="text-align: center; padding: 20px; color: #999;">
              暂无今日患者
            </div>
            <el-table v-else :data="todayPatients" style="width: 100%">
              <el-table-column prop="name" label="患者姓名" width="120" />
              <el-table-column prop="age" label="年龄" width="80" />
              <el-table-column prop="time" label="预约时间" width="150" />
              <el-table-column prop="complaint" label="主诉" width="200" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="{ row }">
                  <el-button type="primary" link size="small">接诊</el-button>
                  <el-button type="success" link size="small">查看历史</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { doctorAPI } from '@/api/index'
import {
  House, User, Tickets, ArrowDown, Bell, Document
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('home')
const loading = ref(false)

const todayPatients = ref([])
const statistics = ref({
  todayPatients: 0,
  pendingPatients: 0,
  pendingRecords: 0,
  consultRequests: 0
})

const loadDoctorData = async () => {
  loading.value = true
  try {
    // 获取今日患者列表
    const patientRes = await doctorAPI.getTodayPatients()
    todayPatients.value = patientRes.data || []

    // 获取统计数据
    const statsRes = await doctorAPI.getStatistics()
    statistics.value = statsRes.data || {}
  } catch (error) {
    console.log('[v0] Error loading doctor data:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const typeMap = {
    '待就诊': 'info',
    '就诊中': 'warning',
    '已开处方': 'success',
    '已完成': 'success'
  }
  return typeMap[status] || 'info'
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  }
}

onMounted(() => {
  loadDoctorData()
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.dashboard-sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #eee;
  overflow-y: auto;
}

.dashboard-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #eee;
}

.dashboard-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  padding: 20px;
  background: white;
  border-radius: 4px;
  border: 1px solid #eee;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-label {
  color: #999;
  font-size: 12px;
}
</style>