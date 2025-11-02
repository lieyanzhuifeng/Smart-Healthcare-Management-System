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
        <el-menu-item index="overview" @click="navigateTo('/patient')">
          <el-icon><House /></el-icon>
          <span>首页概览</span>
        </el-menu-item>
        <el-menu-item index="appointment" @click="navigateTo('/patient/appointment')">
          <el-icon><Calendar /></el-icon>
          <span>预约挂号</span>
        </el-menu-item>
        <el-menu-item index="records">
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
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/patient' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>就诊记录</el-breadcrumb-item>
          </el-breadcrumb>
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
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">就诊记录</span>
              <div style="display: flex; gap: 12px;">
                <el-input
                  v-model="searchText"
                  placeholder="搜索医生、科室"
                  :prefix-icon="Search"
                  style="width: 200px;"
                />
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                />
              </div>
            </div>
          </template>

          <el-table :data="filteredRecords" style="width: 100%">
            <el-table-column prop="date" label="就诊日期" width="120" sortable />
            <el-table-column prop="time" label="就诊时间" width="100" />
            <el-table-column prop="department" label="科室" width="120" />
            <el-table-column prop="doctor" label="医生" width="100" />
            <el-table-column prop="diagnosis" label="诊断结果" min-width="200" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewDetail(row)">
                  查看详情
                </el-button>
                <el-button type="success" link size="small" @click="viewPrescription(row)">
                  查看处方
                </el-button>
                <el-button type="warning" link size="small" @click="downloadReport(row)">
                  下载报告
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div style="margin-top: 20px; text-align: right;">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="records.length"
            />
          </div>
        </el-card>

        <!-- 详情对话框 -->
        <el-dialog v-model="detailVisible" title="就诊详情" width="800px">
          <el-descriptions :column="2" border v-if="selectedRecord">
            <el-descriptions-item label="就诊日期">
              {{ selectedRecord.date }} {{ selectedRecord.time }}
            </el-descriptions-item>
            <el-descriptions-item label="就诊科室">
              {{ selectedRecord.department }}
            </el-descriptions-item>
            <el-descriptions-item label="主治医生">
              {{ selectedRecord.doctor }}
            </el-descriptions-item>
            <el-descriptions-item label="就诊状态">
              <el-tag :type="getStatusType(selectedRecord.status)">
                {{ selectedRecord.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="主诉" :span="2">
              {{ selectedRecord.complaint }}
            </el-descriptions-item>
            <el-descriptions-item label="诊断结果" :span="2">
              {{ selectedRecord.diagnosis }}
            </el-descriptions-item>
            <el-descriptions-item label="治疗方案" :span="2">
              {{ selectedRecord.treatment }}
            </el-descriptions-item>
            <el-descriptions-item label="医嘱" :span="2">
              {{ selectedRecord.advice }}
            </el-descriptions-item>
            <el-descriptions-item label="费用">
              <el-text type="danger" style="font-size: 16px; font-weight: bold;">
                ¥{{ selectedRecord.cost }}
              </el-text>
            </el-descriptions-item>
          </el-descriptions>
        </el-dialog>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { patientAPI } from '@/api'
import {
  House, Calendar, Document, DocumentCopy, Tickets,
  DataAnalysis, VideoCamera, Bell, ArrowDown, Search
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('records')

// 搜索和筛选
const searchText = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

// 就诊记录数据
const records = ref([])

onMounted(async () => {
  await loadRecords()
})

const loadRecords = async () => {
  try {
    const res = await patientAPI.getRegistrationHistory()
    if (res.code === 200 && res.data) {
      records.value = res.data.map(record => ({
        id: record.registrationID,
        date: record.date,
        time: record.starttime,
        department: record.office_name,
        doctor: record.doctor_name,
        diagnosis: record.diagnosis || '待诊断',
        status: getStatusText(record.state),
        complaint: record.complaint || '暂无主诉',
        treatment: record.treatment || '待治疗',
        advice: record.advice || '暂无医嘱',
        cost: record.cost || 0
      }))
    }
  } catch (error) {
    ElMessage.error('加载就诊记录失败')
  }
}

const getStatusText = (state) => {
  const statusMap = {
    0: '待就诊',
    1: '就诊中',
    2: '已开处方',
    3: '药品已准备',
    4: '已完成',
    5: '已取消'
  }
  return statusMap[state] || '未知'
}

const filteredRecords = computed(() => {
  let result = records.value

  // 文本搜索
  if (searchText.value) {
    result = result.filter(record =>
      record.doctor.includes(searchText.value) ||
      record.department.includes(searchText.value)
    )
  }

  // 日期范围筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    result = result.filter(record => {
      const recordDate = new Date(record.date)
      return recordDate >= start && recordDate <= end
    })
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 详情对话框
const detailVisible = ref(false)
const selectedRecord = ref(null)

const getStatusType = (status) => {
  const typeMap = {
    '已完成': 'success',
    '进行中': 'warning',
    '已取消': 'info'
  }
  return typeMap[status] || 'info'
}

const viewDetail = (record) => {
  selectedRecord.value = record
  detailVisible.value = true
}

const viewPrescription = (record) => {
  ElMessage.info('查看处方功能开发中')
}

const downloadReport = (record) => {
  ElMessage.success('报告下载中...')
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
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

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
/* 使用全局样式 */
</style>
