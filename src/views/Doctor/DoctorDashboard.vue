<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="dashboard-sidebar">
      <div style="padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="color: #67C23A; margin: 0;">医生端</h2>
      </div>
      <el-menu :default-active="activeMenu" @select="handleMenuSelect">
        <el-menu-item index="overview">
          <el-icon><House /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="patients">
          <el-icon><User /></el-icon>
          <span>患者列表</span>
        </el-menu-item>
        <el-menu-item index="schedule">
          <el-icon><Calendar /></el-icon>
          <span>我的排班</span>
        </el-menu-item>
        <el-menu-item index="records">
          <el-icon><Document /></el-icon>
          <span>电子病历</span>
        </el-menu-item>
        <el-menu-item index="prescriptions">
          <el-icon><Tickets /></el-icon>
          <span>处方管理</span>
        </el-menu-item>
        <el-menu-item index="consultation">
          <el-icon><ChatDotRound /></el-icon>
          <span>会诊申请</span>
        </el-menu-item>
        <el-menu-item index="ai-assist">
          <el-icon><MagicStick /></el-icon>
          <span>AI辅助诊断</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-main">
      <!-- 顶部导航 -->
      <div class="dashboard-header">
        <div>
          <el-text size="large">{{ userStore.userName }} 医生，您好</el-text>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
          <el-badge :value="5" class="item">
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
            <el-icon :size="32"><User /></el-icon>
            <div class="stat-value">28</div>
            <div class="stat-label">今日接诊</div>
          </div>

          <div class="stat-card" style="--start-color: #67C23A; --end-color: #95D475;">
            <el-icon :size="32"><Calendar /></el-icon>
            <div class="stat-value">15</div>
            <div class="stat-label">待接诊</div>
          </div>

          <div class="stat-card" style="--start-color: #E6A23C; --end-color: #F3C77E;">
            <el-icon :size="32"><Document /></el-icon>
            <div class="stat-value">42</div>
            <div class="stat-label">待审核病历</div>
          </div>

          <div class="stat-card" style="--start-color: #F56C6C; --end-color: #F89898;">
            <el-icon :size="32"><ChatDotRound /></el-icon>
            <div class="stat-value">3</div>
            <div class="stat-label">会诊请求</div>
          </div>
        </div>

        <!-- 今日患者列表 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">今日患者列表</span>
              <el-button type="primary" size="small">
                <el-icon><Plus /></el-icon>
                新建病历
              </el-button>
            </div>
          </template>
          <el-table :data="patients" style="width: 100%">
            <el-table-column prop="id" label="患者ID" width="100" />
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="age" label="年龄" width="80" />
            <el-table-column prop="gender" label="性别" width="80" />
            <el-table-column prop="time" label="预约时间" width="100" />
            <el-table-column prop="complaint" label="主诉" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleDiagnose(row)">
                  诊断
                </el-button>
                <el-button type="success" link size="small">
                  病历
                </el-button>
                <el-button type="warning" link size="small">
                  开处方
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- AI辅助诊断 -->
        <el-card>
          <template #header>
            <span style="font-weight: bold;">
              <el-icon><MagicStick /></el-icon>
              AI辅助诊断建议
            </span>
          </template>
          <el-empty v-if="!selectedPatient" description="请选择患者查看AI诊断建议" />
          <div v-else>
            <el-alert
              title="AI分析结果"
              type="info"
              :closable="false"
              style="margin-bottom: 16px;"
            >
              <p>基于患者症状和历史病历，AI系统提供以下建议：</p>
            </el-alert>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="可能诊断">
                上呼吸道感染（置信度：85%）
              </el-descriptions-item>
              <el-descriptions-item label="建议检查">
                血常规、C反应蛋白
              </el-descriptions-item>
              <el-descriptions-item label="用药建议">
                阿莫西林胶囊、布洛芬缓释片
              </el-descriptions-item>
              <el-descriptions-item label="注意事项">
                注意休息，多饮水，避免受凉
              </el-descriptions-item>
            </el-descriptions>
          </div>
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
  House, User, Calendar, Document, Tickets, ChatDotRound,
  MagicStick, Bell, ArrowDown, Plus
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('overview')
const selectedPatient = ref(null)

const patients = ref([
  { id: 'P001', name: '张三', age: 35, gender: '男', time: '09:00', complaint: '咳嗽、发热3天', status: '待接诊' },
  { id: 'P002', name: '李四', age: 28, gender: '女', time: '09:30', complaint: '头痛、恶心', status: '待接诊' },
  { id: 'P003', name: '王五', age: 45, gender: '男', time: '10:00', complaint: '胸闷、气短', status: '诊断中' },
  { id: 'P004', name: '赵六', age: 52, gender: '女', time: '10:30', complaint: '腹痛、腹泻', status: '已完成' }
])

const getStatusType = (status) => {
  const typeMap = {
    '待接诊': 'warning',
    '诊断中': 'primary',
    '已完成': 'success'
  }
  return typeMap[status] || 'info'
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  ElMessage.info(`切换到：${index}`)
}

const handleDiagnose = (patient) => {
  selectedPatient.value = patient
  ElMessage.success(`开始诊断患者：${patient.name}`)
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
