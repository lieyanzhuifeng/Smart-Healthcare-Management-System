<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="dashboard-sidebar">
      <div style="padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="color: #409EFF; margin: 0;">患者端</h2>
      </div>
      <el-menu :default-active="activeMenu" @select="handleMenuSelect">
        <el-menu-item index="home">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="appointment">
          <el-icon><Calendar /></el-icon>
          <span>预约挂号</span>
        </el-menu-item>
        <el-menu-item index="records">
          <el-icon><Document /></el-icon>
          <span>就诊记录</span>
        </el-menu-item>
        <el-menu-item index="reminders">
          <el-icon><Bell /></el-icon>
          <span>健康提醒</span>
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
          <el-badge :value="reminders.length" class="item">
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
        <!-- 加载状态 -->
        <el-skeleton v-if="loading" :rows="5" animated />

        <div v-else>
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

            <el-card shadow="hover" style="cursor: pointer;">
              <div style="display: flex; align-items: center; gap: 16px;">
                <el-icon :size="40" color="#67C23A"><DocumentCopy /></el-icon>
                <div>
                  <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">就诊记录</div>
                  <el-text type="info">{{ registrations.length }} 条记录</el-text>
                </div>
              </div>
            </el-card>

            <el-card shadow="hover" style="cursor: pointer;">
              <div style="display: flex; align-items: center; gap: 16px;">
                <el-icon :size="40" color="#E6A23C"><DataAnalysis /></el-icon>
                <div>
                  <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">健康提醒</div>
                  <el-text type="info">{{ reminders.length }} 条待处理</el-text>
                </div>
              </div>
            </el-card>

            <el-card shadow="hover" style="cursor: pointer;">
              <div style="display: flex; align-items: center; gap: 16px;">
                <el-icon :size="40" color="#F56C6C"><User /></el-icon>
                <div>
                  <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">个人信息</div>
                  <el-text type="info">{{ patientProfile.name || '未知' }}</el-text>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 我的预约 -->
          <el-card style="margin-bottom: 20px;">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold;">我的预约</span>
                <el-button type="primary" size="small" @click="$router.push('/patient/appointment')">
                  新建预约
                </el-button>
              </div>
            </template>
            <div v-if="appointments.length === 0" style="text-align: center; padding: 20px; color: #999;">
              暂无预约信息
            </div>
            <el-table v-else :data="appointments.slice().reverse()" style="width: 100%">
              <el-table-column prop="office_name" label="科室" width="120" />
              <el-table-column prop="doctor_name" label="医生" width="100" />
              <el-table-column prop="date" label="就诊日期" width="120" />
              <el-table-column prop="starttime" label="就诊时间" width="100" />
              <el-table-column prop="endtime" label="结束时间" width="100" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.state === 1 ? 'success' : 'info'">
                    {{ row.state === 1 ? '有效' : '已完成' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="{ row }">
                  <el-button v-if="row.state === 1" type="danger" link size="small" @click="cancelAppt(row.appointmentID)">
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
            <div v-if="reminders.length === 0" style="text-align: center; padding: 20px; color: #999;">
              暂无健康提醒
            </div>
            <el-timeline v-else>
              <el-timeline-item v-for="reminder in reminders.slice(0, 5)" :key="reminder.id" :timestamp="reminder.time" color="#409EFF">
                <p><strong>{{ reminder.type }}</strong></p>
                <p>{{ reminder.content }}</p>
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
import { patientAPI } from '@/api/index'
import {
  House, Calendar, Document, DocumentCopy, Bell,
  DataAnalysis, ArrowDown, User
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('home')
const loading = ref(false)

const appointments = ref([])
const registrations = ref([])
const reminders = ref([])
const patientProfile = ref({})

const loadPatientData = async () => {
  loading.value = true
  try {
    // 获取预约列表
    const apptRes = await patientAPI.getAppointments()
    appointments.value = apptRes.data?.appointments || []

    // 获取挂号历史
    const regRes = await patientAPI.getRegistrationHistory()
    registrations.value = regRes.data || []

    // 获取健康提醒
    const reminderRes = await patientAPI.getReminders()
    reminders.value = reminderRes.data || []

    // 获取患者信息
    const profileRes = await patientAPI.getProfile()
    patientProfile.value = profileRes.data || {}
  } catch (error) {
    console.log('[v0] Error loading patient data:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 取消预约
const cancelAppt = async (appointmentId) => {
  try {
    await patientAPI.cancelAppointment(appointmentId)
    ElMessage.success('预约已取消')
    loadPatientData()
  } catch (error) {
    ElMessage.error('取消预约失败')
  }
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  if (index === 'appointment') {
    router.push('/patient/appointment')
  } else if (index === 'records') {
    router.push('/patient/records')
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
  loadPatientData()
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
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}
</style>
