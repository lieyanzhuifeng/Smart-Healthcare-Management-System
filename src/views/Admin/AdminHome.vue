<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="dashboard-sidebar">
      <div style="padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="color: #F56C6C; margin: 0;">管理端</h2>
      </div>
      <el-menu :default-active="activeMenu" @select="handleMenuSelect">
        <el-menu-item index="home">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="schedule">
          <el-icon><Calendar /></el-icon>
          <span>医生排班</span>
        </el-menu-item>
        <el-menu-item index="statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-main">
      <!-- 顶部导航 -->
      <div class="dashboard-header">
        <div>
          <el-text size="large">医院管理系统</el-text>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
          <el-badge :value="notifications.length" class="item">
            <el-icon :size="20"><Bell /></el-icon>
          </el-badge>
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
              <div class="stat-value">{{ statistics.outpatientVolume }}</div>
              <div class="stat-label">今日门诊量</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#67C23A"><Money /></el-icon>
              <div class="stat-value">¥{{ (statistics.revenue / 1000).toFixed(0) }}K</div>
              <div class="stat-label">今日收入</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#E6A23C"><OfficeBuilding /></el-icon>
              <div class="stat-value">{{ statistics.bedUsageRate }}%</div>
              <div class="stat-label">床位使用率</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#F56C6C"><Star /></el-icon>
              <div class="stat-value">{{ statistics.patientSatisfaction }}</div>
              <div class="stat-label">患者满意度</div>
            </div>
          </div>

          <!-- 图表区域 -->
          <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px;">
            <el-card>
              <template #header>
                <span style="font-weight: bold;">门诊量趋势（最近7天）</span>
              </template>
              <div ref="chartRef" style="height: 300px;"></div>
            </el-card>

            <el-card>
              <template #header>
                <span style="font-weight: bold;">科室分布</span>
              </template>
              <div ref="pieChartRef" style="height: 300px;"></div>
            </el-card>
          </div>

          <!-- 系统通知 -->
          <el-card>
            <template #header>
              <span style="font-weight: bold;">系统通知</span>
            </template>
            <div v-if="notifications.length === 0" style="text-align: center; padding: 20px; color: #999;">
              暂无通知
            </div>
            <el-timeline v-else>
              <el-timeline-item v-for="notif in notifications" :key="notif.id" :timestamp="notif.time" color="#409EFF">
                <p><strong>{{ notif.title }}</strong></p>
                <p>{{ notif.content }}</p>
              </el-timeline-item>
            </el-timeline>
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
import { adminAPI } from '@/api/index'
import * as echarts from 'echarts'
import {
  House, Calendar, DataAnalysis, Bell,
  ArrowDown, User, Money, OfficeBuilding, Star
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('home')
const loading = ref(false)
const chartRef = ref(null)
const pieChartRef = ref(null)

const statistics = ref({
  outpatientVolume: 0,
  revenue: 0,
  bedUsageRate: 0,
  patientSatisfaction: 0
})
const notifications = ref([])

const loadAdminData = async () => {
  loading.value = true
  try {
    // 获取统计数据
    const statsRes = await adminAPI.getStatistics()
    statistics.value = statsRes.data || {}

    // 获取系统通知
    const notifRes = await adminAPI.getNotifications()
    notifications.value = notifRes.data || []

    // 延迟初始化图表
    setTimeout(() => {
      initCharts()
    }, 300)
  } catch (error) {
    console.log('[v0] Error loading admin data:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const initCharts = async () => {
  try {
    // 获取门诊量趋势
    const trendRes = await adminAPI.getOutpatientTrend({ days: 7 })
    const trendData = trendRes.data || {}

    // 获取科室分布
    const deptRes = await adminAPI.getDepartmentDistribution()
    const deptData = deptRes.data || []

    // 门诊量趋势图
    if (chartRef.value && trendData.labels) {
      const chart = echarts.init(chartRef.value)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: trendData.labels
        },
        yAxis: { type: 'value' },
        series: [{
          data: trendData.values || [],
          type: 'line',
          smooth: true,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ])
          }
        }]
      })
    }

    // 科室分布饼图
    if (pieChartRef.value && deptData.length > 0) {
      const pieChart = echarts.init(pieChartRef.value)
      pieChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie',
          radius: '70%',
          data: deptData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      })
    }
  } catch (error) {
    console.log('[v0] Error initializing charts:', error)
  }
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  if (index === 'schedule') {
    router.push('/admin/schedule')
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  }
}

onMounted(() => {
  loadAdminData()
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
