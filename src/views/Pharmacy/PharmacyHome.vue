<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="dashboard-sidebar">
      <div style="padding: 20px; border-bottom: 1px solid #eee;">
        <h2 style="color: #E6A23C; margin: 0;">药房端</h2>
      </div>
      <el-menu :default-active="activeMenu" @select="handleMenuSelect">
        <el-menu-item index="home">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="prescriptions">
          <el-icon><Tickets /></el-icon>
          <span>处方配药</span>
        </el-menu-item>
        <el-menu-item index="inventory">
          <el-icon><Package /></el-icon>
          <span>库存管理</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-main">
      <!-- 顶部导航 -->
      <div class="dashboard-header">
        <div>
          <el-text size="large">药房管理系统</el-text>
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
              <el-icon :size="32" color="#409EFF"><Tickets /></el-icon>
              <div class="stat-value">{{ statistics.pendingPrescriptions }}</div>
              <div class="stat-label">待配药处方</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#67C23A"><Package /></el-icon>
              <div class="stat-value">{{ statistics.medicineTypes }}</div>
              <div class="stat-label">药品种类</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#E6A23C"><Warning /></el-icon>
              <div class="stat-value">{{ statistics.stockAlerts }}</div>
              <div class="stat-label">库存预警</div>
            </div>

            <div class="stat-card">
              <el-icon :size="32" color="#F56C6C"><Clock /></el-icon>
              <div class="stat-value">{{ statistics.expiringSoon }}</div>
              <div class="stat-label">即将过期</div>
            </div>
          </div>

          <!-- 待配药处方 -->
          <el-card style="margin-bottom: 20px;">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold;">待配药处方列表</span>
                <el-select v-model="filterType" placeholder="请选择" style="width: 120px;">
                  <el-option label="全部" value="all" />
                  <el-option label="待配药" value="pending" />
                  <el-option label="已配药" value="dispensed" />
                </el-select>
              </div>
            </template>
            <div v-if="prescriptions.length === 0" style="text-align: center; padding: 20px; color: #999;">
              暂无处方
            </div>
            <el-table v-else :data="prescriptions" style="width: 100%">
              <el-table-column prop="patientName" label="患者姓名" width="120" />
              <el-table-column prop="doctorName" label="医生" width="100" />
              <el-table-column prop="time" label="处方时间" width="150" />
              <el-table-column prop="medicines" label="药品" width="250" />
              <el-table-column prop="priority" label="优先级" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.priority === '急' ? 'danger' : 'info'">{{ row.priority }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="dispensePrescription(row.id)">
                    配药
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 库存预警 -->
          <el-card>
            <template #header>
              <span style="font-weight: bold;">库存预警</span>
            </template>
            <div v-if="inventoryAlerts.length === 0" style="text-align: center; padding: 20px; color: #999;">
              暂无库存预警
            </div>
            <el-table v-else :data="inventoryAlerts" style="width: 100%">
              <el-table-column prop="name" label="药品名称" width="150" />
              <el-table-column prop="spec" label="规格" width="120" />
              <el-table-column prop="stock" label="现存库存" width="100" />
              <el-table-column prop="threshold" label="预警阈值" width="100" />
              <el-table-column prop="alertType" label="预警类型" width="100">
                <template #default="{ row }">
                  <el-tag type="warning">{{ row.alertType }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="expiry" label="过期日期" width="120" />
              <el-table-column label="操作">
                <template #default>
                  <el-button type="primary" link size="small">补货</el-button>
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
import { pharmacyAPI } from '@/api/index'
import {
  House, Tickets, Package, ArrowDown, Warning, Clock
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('home')
const loading = ref(false)
const filterType = ref('all')

const prescriptions = ref([])
const inventoryAlerts = ref([])
const statistics = ref({
  pendingPrescriptions: 0,
  medicineTypes: 0,
  stockAlerts: 0,
  expiringSoon: 0
})

const loadPharmacyData = async () => {
  loading.value = true
  try {
    // 获取待配药处方
    const prescRes = await pharmacyAPI.getPrescriptions({ filter: filterType.value })
    prescriptions.value = prescRes.data || []

    // 获取库存预警
    const alertRes = await pharmacyAPI.getInventoryAlerts()
    inventoryAlerts.value = alertRes.data || []

    // 获取统计数据
    const statsRes = await pharmacyAPI.getStatistics()
    statistics.value = statsRes.data || {}
  } catch (error) {
    console.log('[v0] Error loading pharmacy data:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 配药
const dispensePrescription = async (prescriptionId) => {
  try {
    await pharmacyAPI.dispensePrescription(prescriptionId)
    ElMessage.success('配药成功')
    loadPharmacyData()
  } catch (error) {
    ElMessage.error('配药失败')
  }
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
  loadPharmacyData()
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
