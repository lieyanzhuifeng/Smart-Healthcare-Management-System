<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="dashboard-sidebar">
      <div style="padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="color: #409EFF; margin: 0;">患者端</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="overview">
          <el-icon><House /></el-icon>
          <span>首页概览</span>
        </el-menu-item>
        <el-menu-item index="appointment" @click="$router.push('/patient/appointment')">
          <el-icon><Calendar /></el-icon>
          <span>预约挂号</span>
        </el-menu-item>
        <el-menu-item index="records" @click="$router.push('/patient/records')">
          <el-icon><Document /></el-icon>
          <span>就诊记录</span>
        </el-menu-item>
        <el-menu-item index="reports">
          <el-icon><DocumentCopy /></el-icon>
          <span>检查报告</span>
        </el-menu-item>
        <el-menu-item index="prescriptions">
          <el-icon><Tickets /></el-icon>
          <span>处方记录</span>
        </el-menu-item>
        <el-menu-item index="health">
          <el-icon><DataAnalysis /></el-icon>
          <span>健康管理</span>
        </el-menu-item>
        <el-menu-item index="telemedicine">
          <el-icon><VideoCamera /></el-icon>
          <span>远程问诊</span>
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
          <el-badge :value="3" class="item">
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
        <!-- 快捷操作卡片 -->
        <div class="card-grid">
          <el-card shadow="hover" style="cursor: pointer;" @click="$router.push('/patient/appointment')">
            <div style="display: flex; align-items: center; gap: 16px;">
              <el-icon :size="40" color="#409EFF"><Calendar /></el-icon>
              <div>
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">预约挂号</div>
                <el-text type="info">快速预约医生</el-text>
              </div>
            </div>
          </el-card>

          <el-card shadow="hover" style="cursor: pointer;" @click="activeMenu = 'reports'">
            <div style="display: flex; align-items: center; gap: 16px;">
              <el-icon :size="40" color="#67C23A"><DocumentCopy /></el-icon>
              <div>
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">检查报告</div>
                <el-text type="info">查看检验结果</el-text>
              </div>
            </div>
          </el-card>

          <el-card shadow="hover" style="cursor: pointer;" @click="activeMenu = 'telemedicine'">
            <div style="display: flex; align-items: center; gap: 16px;">
              <el-icon :size="40" color="#E6A23C"><VideoCamera /></el-icon>
              <div>
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">远程问诊</div>
                <el-text type="info">在线咨询医生</el-text>
              </div>
            </div>
          </el-card>

          <el-card shadow="hover" style="cursor: pointer;" @click="activeMenu = 'health'">
            <div style="display: flex; align-items: center; gap: 16px;">
              <el-icon :size="40" color="#F56C6C"><DataAnalysis /></el-icon>
              <div>
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">健康管理</div>
                <el-text type="info">个性化健康建议</el-text>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 预约信息 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">我的预约</span>
              <el-button type="primary" size="small" @click="activeMenu = 'appointment'">
                新建预约
              </el-button>
            </div>
          </template>
          <el-table :data="appointments" style="width: 100%">
            <el-table-column prop="date" label="就诊日期" width="120" />
            <el-table-column prop="time" label="就诊时间" width="100" />
            <el-table-column prop="department" label="科室" width="120" />
            <el-table-column prop="doctor" label="医生" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '已完成' ? 'success' : 'warning'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button v-if="row.status === '待就诊'" type="primary" link size="small">
                  查看详情
                </el-button>
                <el-button v-if="row.status === '待就诊'" type="danger" link size="small">
                  取消预约
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 健康提醒 -->
        <el-card>
          <template #header>
            <span style="font-weight: bold;">健康提醒</span>
          </template>
          <el-timeline>
            <el-timeline-item timestamp="今天 09:00" color="#409EFF">
              <p>您有一个预约：内科 - 李医生</p>
            </el-timeline-item>
            <el-timeline-item timestamp="明天 14:00" color="#67C23A">
              <p>复诊提醒：请按时服药并准备复查</p>
            </el-timeline-item>
            <el-timeline-item timestamp="2天后" color="#E6A23C">
              <p>体检提醒：年度体检即将到期</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import {
  House, Calendar, Document, DocumentCopy, Tickets,
  DataAnalysis, VideoCamera, Bell, ArrowDown
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('overview')

const appointments = ref([
  { date: '2025-01-15', time: '09:00', department: '内科', doctor: '李医生', status: '待就诊' },
  { date: '2025-01-10', time: '14:30', department: '外科', doctor: '王医生', status: '已完成' },
  { date: '2025-01-05', time: '10:00', department: '儿科', doctor: '张医生', status: '已完成' }
])

const handleMenuSelect = (index) => {
  activeMenu.value = index
  ElMessage.info(`切换到：${index}`)
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
</script>

<style scoped>
/* 使用全局样式 */
</style>
