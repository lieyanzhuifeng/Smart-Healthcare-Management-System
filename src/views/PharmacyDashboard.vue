<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="dashboard-sidebar">
      <div style="padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="color: #E6A23C; margin: 0;">药房端</h2>
      </div>
      <el-menu :default-active="activeMenu" @select="handleMenuSelect">
        <el-menu-item index="overview">
          <el-icon><House /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="prescriptions">
          <el-icon><Tickets /></el-icon>
          <span>处方管理</span>
        </el-menu-item>
        <el-menu-item index="inventory">
          <el-icon><Box /></el-icon>
          <span>库存管理</span>
        </el-menu-item>
        <el-menu-item index="alerts">
          <el-icon><Warning /></el-icon>
          <span>预警中心</span>
        </el-menu-item>
        <el-menu-item index="statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计报表</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-main">
      <!-- 顶部导航 -->
      <div class="dashboard-header">
        <div>
          <el-text size="large">药房工作台</el-text>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
          <el-badge :value="8" class="item">
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
            <el-icon :size="32"><Tickets /></el-icon>
            <div class="stat-value">45</div>
            <div class="stat-label">待配药处方</div>
          </div>

          <div class="stat-card" style="--start-color: #67C23A; --end-color: #95D475;">
            <el-icon :size="32"><Box /></el-icon>
            <div class="stat-value">1,258</div>
            <div class="stat-label">库存药品种类</div>
          </div>

          <div class="stat-card" style="--start-color: #E6A23C; --end-color: #F3C77E;">
            <el-icon :size="32"><Warning /></el-icon>
            <div class="stat-value">12</div>
            <div class="stat-label">库存预警</div>
          </div>

          <div class="stat-card" style="--start-color: #F56C6C; --end-color: #F89898;">
            <el-icon :size="32"><Clock /></el-icon>
            <div class="stat-value">5</div>
            <div class="stat-label">即将过期</div>
          </div>
        </div>

        <!-- 待配药处方 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">待配药处方</span>
              <el-radio-group v-model="prescriptionFilter" size="small">
                <el-radio-button value="all">全部</el-radio-button>
                <el-radio-button value="urgent">急诊</el-radio-button>
                <el-radio-button value="normal">普通</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <el-table :data="prescriptions" style="width: 100%">
            <el-table-column prop="id" label="处方号" width="120" />
            <el-table-column prop="patientName" label="患者姓名" width="100" />
            <el-table-column prop="doctorName" label="开方医生" width="100" />
            <el-table-column prop="time" label="开方时间" width="160" />
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="{ row }">
                <el-tag :type="row.priority === '急诊' ? 'danger' : 'info'">
                  {{ row.priority }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="medicines" label="药品" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleDispense(row)">
                  配药
                </el-button>
                <el-button type="success" link size="small">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 库存预警 -->
        <el-card>
          <template #header>
            <span style="font-weight: bold;">
              <el-icon><Warning /></el-icon>
              库存预警
            </span>
          </template>
          <el-table :data="alerts" style="width: 100%">
            <el-table-column prop="name" label="药品名称" />
            <el-table-column prop="spec" label="规格" width="120" />
            <el-table-column prop="stock" label="当前库存" width="100">
              <template #default="{ row }">
                <el-text :type="row.stock < 50 ? 'danger' : 'warning'">
                  {{ row.stock }}
                </el-text>
              </template>
            </el-table-column>
            <el-table-column prop="threshold" label="预警阈值" width="100" />
            <el-table-column prop="expiry" label="最近效期" width="120" />
            <el-table-column prop="alertType" label="预警类型" width="120">
              <template #default="{ row }">
                <el-tag :type="row.alertType === '库存不足' ? 'danger' : 'warning'">
                  {{ row.alertType }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default>
                <el-button type="primary" link size="small">
                  申请采购
                </el-button>
                <el-button type="warning" link size="small">
                  调拨
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import {
  House, Tickets, Box, Warning, DataAnalysis,
  Bell, ArrowDown, Clock
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('overview')
const prescriptionFilter = ref('all')

const prescriptions = ref([
  { id: 'RX20250115001', patientName: '张三', doctorName: '李医生', time: '2025-01-15 09:15', priority: '急诊', medicines: '阿莫西林胶囊、布洛芬片' },
  { id: 'RX20250115002', patientName: '李四', doctorName: '王医生', time: '2025-01-15 09:30', priority: '普通', medicines: '感冒灵颗粒、维生素C' },
  { id: 'RX20250115003', patientName: '王五', doctorName: '张医生', time: '2025-01-15 10:00', priority: '普通', medicines: '降压药、阿司匹林' }
])

const alerts = ref([
  { name: '阿莫西林胶囊', spec: '0.25g*24粒', stock: 35, threshold: 50, expiry: '2025-03-15', alertType: '库存不足' },
  { name: '布洛芬缓释片', spec: '0.3g*20片', stock: 120, threshold: 100, expiry: '2025-02-10', alertType: '即将过期' },
  { name: '感冒灵颗粒', spec: '10g*9袋', stock: 28, threshold: 50, alertType: '库存不足' },
  { name: '维生素C片', spec: '100mg*100片', stock: 150, threshold: 100, expiry: '2025-02-28', alertType: '即将过期' }
])

const handleMenuSelect = (index) => {
  activeMenu.value = index
  ElMessage.info(`切换到：${index}`)
}

const handleDispense = async (prescription) => {
  try {
    await ElMessageBox.confirm(
      `确认为患者 ${prescription.patientName} 配药？`,
      '配药确认',
      {
        confirmButtonText: '确认配药',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.success('配药成功')
  } catch {
    ElMessage.info('已取消')
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
</script>

<style scoped>
/* 使用全局样式 */
</style>
