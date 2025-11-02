<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="dashboard-sidebar">
      <div style="padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="color: #F56C6C; margin: 0;">管理端</h2>
      </div>
      <el-menu :default-active="activeMenu" @select="handleMenuSelect">
        <el-menu-item index="overview">
          <el-icon><House /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        <el-menu-item index="schedule">
          <el-icon><Calendar /></el-icon>
          <span>医生排班</span>
        </el-menu-item>
        <el-menu-item index="departments">
          <el-icon><OfficeBuilding /></el-icon>
          <span>科室管理</span>
        </el-menu-item>
        <el-menu-item index="staff">
          <el-icon><User /></el-icon>
          <span>人员管理</span>
        </el-menu-item>
        <el-menu-item index="financial">
          <el-icon><Money /></el-icon>
          <span>财务报表</span>
        </el-menu-item>
        <el-menu-item index="equipment">
          <el-icon><Monitor /></el-icon>
          <span>设备管理</span>
        </el-menu-item>
        <el-menu-item index="statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
        <el-menu-item index="settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
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
          <el-badge :value="2" class="item">
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
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="dashboard-content">
        <!-- 统计卡片 -->
        <div class="card-grid">
          <div class="stat-card" style="--start-color: #409EFF; --end-color: #66B1FF;">
            <el-icon :size="32"><House /></el-icon>
            <div class="stat-value">1,245</div>
            <div class="stat-label">今日门诊量</div>
            <el-text type="info" size="small">较昨日 +12%</el-text>
          </div>

          <div class="stat-card" style="--start-color: #67C23A; --end-color: #95D475;">
            <el-icon :size="32"><Money /></el-icon>
            <div class="stat-value">¥328K</div>
            <div class="stat-label">今日收入</div>
            <el-text type="info" size="small">较昨日 +8%</el-text>
          </div>

          <div class="stat-card" style="--start-color: #E6A23C; --end-color: #F3C77E;">
            <el-icon :size="32"><OfficeBuilding /></el-icon>
            <div class="stat-value">85%</div>
            <div class="stat-label">床位使用率</div>
            <el-text type="info" size="small">较昨日 +3%</el-text>
          </div>

          <div class="stat-card" style="--start-color: #F56C6C; --end-color: #F89898;">
            <el-icon :size="32"><Star /></el-icon>
            <div class="stat-value">4.8</div>
            <div class="stat-label">患者满意度</div>
            <el-text type="info" size="small">本月平均</el-text>
          </div>
        </div>

        <!-- 图表区域 -->
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px;">
          <el-card>
            <template #header>
              <span style="font-weight: bold;">门诊量趋势</span>
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

        <!-- 科室管理 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">科室概览</span>
              <el-button type="primary" size="small">
                <el-icon><Plus /></el-icon>
                添加科室
              </el-button>
            </div>
          </template>
          <el-table :data="departments" style="width: 100%">
            <el-table-column prop="name" label="科室名称" width="150" />
            <el-table-column prop="director" label="科室主任" width="100" />
            <el-table-column prop="doctors" label="医生数" width="100" />
            <el-table-column prop="beds" label="床位数" width="100" />
            <el-table-column prop="occupancy" label="床位使用率" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.occupancy" :color="getProgressColor(row.occupancy)" />
              </template>
            </el-table-column>
            <el-table-column prop="todayPatients" label="今日接诊" width="100" />
            <el-table-column prop="revenue" label="本月收入" width="120" />
            <el-table-column label="操作" width="150">
              <template #default>
                <el-button type="primary" link size="small">编辑</el-button>
                <el-button type="success" link size="small">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 系统通知 -->
        <el-card>
          <template #header>
            <span style="font-weight: bold;">系统通知</span>
          </template>
          <el-timeline>
            <el-timeline-item timestamp="2025-01-15 10:30" color="#409EFF">
              <p><strong>设备维护提醒</strong></p>
              <p>CT设备将于明天进行例行维护，请提前安排患者检查</p>
            </el-timeline-item>
            <el-timeline-item timestamp="2025-01-15 09:00" color="#67C23A">
              <p><strong>药品采购完成</strong></p>
              <p>本月药品采购已完成，共采购药品120种，总金额¥85,000</p>
            </el-timeline-item>
            <el-timeline-item timestamp="2025-01-14 16:00" color="#E6A23C">
              <p><strong>人员变动</strong></p>
              <p>内科新入职医生2名，已完成入职培训</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import * as echarts from 'echarts'
import {
  House, OfficeBuilding, User, Money, Monitor,
  DataAnalysis, Setting, Bell, ArrowDown, Star, Plus,
  Calendar
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('overview')
const chartRef = ref(null)
const pieChartRef = ref(null)

const departments = ref([
  { name: '内科', director: '李主任', doctors: 15, beds: 50, occupancy: 85, todayPatients: 156, revenue: '¥125K' },
  { name: '外科', director: '王主任', doctors: 12, beds: 40, occupancy: 78, todayPatients: 98, revenue: '¥98K' },
  { name: '儿科', director: '张主任', doctors: 10, beds: 30, occupancy: 92, todayPatients: 203, revenue: '¥76K' },
  { name: '妇产科', director: '赵主任', doctors: 8, beds: 25, occupancy: 88, todayPatients: 87, revenue: '¥65K' }
])

const getProgressColor = (percentage) => {
  if (percentage > 90) return '#F56C6C'
  if (percentage > 70) return '#E6A23C'
  return '#67C23A'
}

const initCharts = () => {
  // 门诊量趋势图
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [1120, 1320, 1010, 1340, 1290, 1230, 1100],
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
  if (pieChartRef.value) {
    const pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '70%',
        data: [
          { value: 156, name: '内科' },
          { value: 98, name: '外科' },
          { value: 203, name: '儿科' },
          { value: 87, name: '妇产科' }
        ],
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
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  if (index === 'schedule') {
    router.push('/admin/schedule')
  } else {
    ElMessage.info(`切换到：${index}`)
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  } else {
    ElMessage.info(`点击了：${command}`)
  }
}

onMounted(() => {
  initCharts()
})
</script>

<style scoped>
/* 使用全局样式 */
</style>
