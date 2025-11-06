<template>
  <div class="dashboard-container">
    <!-- 侧边栏保持不变 -->
    <div class="dashboard-sidebar">
      <!-- ... 侧边栏代码保持不变 ... -->
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-main">
      <!-- 顶部导航 -->
      <div class="dashboard-header">
        <div>
          <el-text size="large">医生排班管理</el-text>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
          <el-badge :value="notificationCount" class="item">
            <el-icon :size="20"><Bell /></el-icon>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span style="cursor: pointer; display: flex; align-items: center; gap: 8px;">
              <el-avatar :size="32">{{ userStore.userName?.charAt(0) || 'A' }}</el-avatar>
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
        <!-- 筛选和操作栏 -->
        <el-card style="margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; gap: 12px; flex-wrap: wrap;">
              <el-date-picker
                v-model="selectedDate"
                type="date"
                placeholder="选择日期"
                style="width: 200px;"
                @change="loadSchedulePreview"
              />

              <el-select 
                v-model="selectedTimeslot" 
                placeholder="选择时间段" 
                style="width: 150px;" 
                clearable
                @change="loadSchedulePreview"
              >
                <el-option label="全部时段" value="" />
                <el-option label="凌晨 (00:00-06:00)" value="1" />
                <el-option label="上午 (06:00-12:00)" value="2" />
                <el-option label="下午 (12:00-18:00)" value="3" />
                <el-option label="晚上 (18:00-23:59)" value="4" />
              </el-select>
            </div>

            <div style="display: flex; gap: 12px;">
              <el-button type="primary" @click="showGenerateDialog = true">
                <el-icon><Plus /></el-icon>
                生成排班
              </el-button>
              <el-button type="success" @click="showBatchDialog = true">
                <el-icon><Calendar /></el-icon>
                批量排班
              </el-button>
              <el-button type="warning" @click="showClearDialog = true">
                <el-icon><Delete /></el-icon>
                清除排班
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 排班预览 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">
                排班预览 - {{ selectedDate ? formatDate(selectedDate) : '今日' }}
              </span>
              <el-button type="primary" link @click="loadSchedulePreview">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <!-- 排班表格 -->
          <el-table 
            :data="scheduleData" 
            border 
            style="width: 100%"
            v-loading="loading"
          >
            <el-table-column prop="sectionID" label="排班ID" width="100" />
            <el-table-column prop="doctorName" label="医生" width="150">
              <template #default="{ row }">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-avatar :size="32">{{ row.doctorName?.charAt(0) || 'D' }}</el-avatar>
                  <span>{{ row.doctorName }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="roomNumber" label="诊室" width="100" />
            <el-table-column prop="timeRange" label="时间段" width="150">
              <template #default="{ row }">
                <el-tag :type="getTimeslotType(row.timeslotID)">
                  {{ getTimeslotLabel(row.timeslotID) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="restappiontment" label="剩余预约" width="100">
              <template #default="{ row }">
                <el-text :type="row.restappiontment > 0 ? 'success' : 'danger'">
                  {{ row.restappiontment }}
                </el-text>
              </template>
            </el-table-column>
            <el-table-column prop="restregistration" label="剩余挂号" width="100" />
            <el-table-column prop="totalregistration" label="总名额" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.restappiontment > 0 ? 'success' : 'danger'">
                  {{ row.restappiontment > 0 ? '可预约' : '已满' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="scheduleData.length === 0 && !loading" style="text-align: center; padding: 40px;">
            <el-empty description="暂无排班数据" />
          </div>
        </el-card>

        <!-- 统计信息 -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
          <el-card>
            <el-statistic title="总排班数" :value="totalSchedules">
              <template #suffix>个</template>
            </el-statistic>
          </el-card>
          <el-card>
            <el-statistic title="可预约数" :value="availableAppointments">
              <template #suffix>个</template>
            </el-statistic>
          </el-card>
          <el-card>
            <el-statistic title="医生数量" :value="doctorCount">
              <template #suffix>人</template>
            </el-statistic>
          </el-card>
          <el-card>
            <el-statistic title="诊室使用" :value="roomUsage">
              <template #suffix>间</template>
            </el-statistic>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 生成排班对话框 -->
    <el-dialog
      v-model="showGenerateDialog"
      title="生成排班"
      width="500px"
    >
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="开始日期" required>
          <el-date-picker
            v-model="generateForm.startDate"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="结束日期" required>
          <el-date-picker
            v-model="generateForm.endDate"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="时间段">
          <el-checkbox-group v-model="generateForm.timeslots">
            <el-checkbox label="1">凌晨 (00:00-06:00)</el-checkbox>
            <el-checkbox label="2">上午 (06:00-12:00)</el-checkbox>
            <el-checkbox label="3">下午 (12:00-18:00)</el-checkbox>
            <el-checkbox label="4">晚上 (18:00-23:59)</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="generateSchedules" :loading="generating">
          生成预览
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量排班对话框 -->
    <el-dialog
      v-model="showBatchDialog"
      title="批量排班"
      width="500px"
    >
      <el-alert
        title="一键生成并保存排班到数据库"
        type="info"
        description="系统将自动为所有医生生成指定日期范围的排班"
        style="margin-bottom: 20px;"
      />
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="开始日期" required>
          <el-date-picker
            v-model="batchForm.startDate"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="结束日期" required>
          <el-date-picker
            v-model="batchForm.endDate"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="时间段">
          <el-checkbox-group v-model="batchForm.timeslots">
            <el-checkbox label="1">凌晨 (00:00-06:00)</el-checkbox>
            <el-checkbox label="2">上午 (06:00-12:00)</el-checkbox>
            <el-checkbox label="3">下午 (12:00-18:00)</el-checkbox>
            <el-checkbox label="4">晚上 (18:00-23:59)</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchDialog = false">取消</el-button>
        <el-button type="success" @click="generateAndSaveSchedules" :loading="saving">
          生成并保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 清除排班对话框 -->
    <el-dialog
      v-model="showClearDialog"
      title="清除排班"
      width="500px"
    >
      <el-alert
        title="警告：此操作将删除指定日期范围内的所有排班"
        type="warning"
        description="清除后数据无法恢复，请谨慎操作"
        style="margin-bottom: 20px;"
      />
      <el-form :model="clearForm" label-width="100px">
        <el-form-item label="开始日期" required>
          <el-date-picker
            v-model="clearForm.startDate"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="结束日期" required>
          <el-date-picker
            v-model="clearForm.endDate"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showClearDialog = false">取消</el-button>
        <el-button type="danger" @click="clearSchedules" :loading="clearing">
          确认清除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { adminAPI } from '@/api'
import {
  House, Calendar, OfficeBuilding, User, Money, Monitor,
  DataAnalysis, Setting, Bell, ArrowDown, Plus, Delete, Refresh
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const activeMenu = ref('schedule')
const selectedDate = ref(new Date())
const selectedTimeslot = ref('')
const loading = ref(false)
const generating = ref(false)
const saving = ref(false)
const clearing = ref(false)

// 对话框控制
const showGenerateDialog = ref(false)
const showBatchDialog = ref(false)
const showClearDialog = ref(false)

// 排班数据
const scheduleData = ref([])
const generatedSchedules = ref([])

// 表单数据
const generateForm = ref({
  startDate: new Date(),
  endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7天后
  timeslots: ['1', '2']
})

const batchForm = ref({
  startDate: new Date(),
  endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
  timeslots: ['1', '2']
})

const clearForm = ref({
  startDate: new Date(),
  endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
})

// 计算属性
const totalSchedules = computed(() => scheduleData.value.length)
const availableAppointments = computed(() => 
  scheduleData.value.reduce((sum, item) => sum + item.restappiontment, 0)
)
const doctorCount = computed(() => {
  const doctors = new Set(scheduleData.value.map(item => item.doctorID))
  return doctors.size
})
const roomUsage = computed(() => {
  const rooms = new Set(scheduleData.value.map(item => item.roomID))
  return rooms.size
})
const notificationCount = computed(() => scheduleData.value.filter(item => item.restappiontment === 0).length)

// 方法
const handleMenuSelect = (index) => {
  activeMenu.value = index
  if (index === 'overview') {
    router.push('/admin')
  } else if (index === 'schedule') {
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

const formatDate = (date) => {
  return new Date(date).toISOString().split('T')[0]
}

const getTimeslotLabel = (timeslotID) => {
  const map = {
    1: '(00:00-06:00)',
    2: '(06:00-12:00)',
    3: '(12:00-18:00)',
    4: '(18:00-23:59)'
  }
  return map[timeslotID] || `时段${timeslotID}`
}

const getTimeslotType = (timeslotID) => {
  const map = {
    1: 'success',
    2: 'warning',
    3: 'info',
    4: 'primary'
  }
  return map[timeslotID] || 'info'
}

// API调用方法
const loadSchedulePreview = async () => {
  try {
    loading.value = true
    const date = selectedDate.value ? formatDate(selectedDate.value) : formatDate(new Date())
    const res = await adminAPI.previewSchedules({ date })
    
    if (res.code === 200 && res.data) {
      let schedules = res.data.schedules || []
      
      // 根据选择的时间段过滤
      if (selectedTimeslot.value) {
        schedules = schedules.filter(schedule => 
          schedule.timeslotID.toString() === selectedTimeslot.value
        )
      }
      
      scheduleData.value = schedules
      ElMessage.success(`加载了 ${schedules.length} 条排班记录`)
    } else {
      scheduleData.value = []
      ElMessage.warning('暂无排班数据')
    }
  } catch (error) {
    console.error('加载排班预览失败:', error)
    ElMessage.error('加载排班数据失败')
    scheduleData.value = []
  } finally {
    loading.value = false
  }
}

const generateSchedules = async () => {
  if (!generateForm.value.startDate || !generateForm.value.endDate) {
    ElMessage.warning('请选择开始日期和结束日期')
    return
  }

  try {
    generating.value = true
    const res = await adminAPI.generateSchedules({
      startDate: formatDate(generateForm.value.startDate),
      endDate: formatDate(generateForm.value.endDate),
      timeslots: generateForm.value.timeslots.map(Number)
    })

    if (res.code === 200) {
      generatedSchedules.value = res.data.schedules || []
      ElMessage.success(`生成了 ${generatedSchedules.value.length} 条排班记录`)
      showGenerateDialog.value = false
      
      // 可以选择保存或直接查看
      ElMessageBox.confirm(
        `已生成 ${generatedSchedules.value.length} 条排班记录，是否保存到数据库？`,
        '保存排班',
        {
          confirmButtonText: '保存',
          cancelButtonText: '仅预览',
          type: 'success'
        }
      ).then(() => {
        saveSchedules()
      })
    }
  } catch (error) {
    console.error('生成排班失败:', error)
    ElMessage.error('生成排班失败')
  } finally {
    generating.value = false
  }
}

const saveSchedules = async () => {
  if (generatedSchedules.value.length === 0) {
    ElMessage.warning('没有可保存的排班数据')
    return
  }

  try {
    saving.value = true
    const res = await adminAPI.saveSchedules({
      schedules: generatedSchedules.value
    })

    if (res.code === 200) {
      ElMessage.success(`成功保存 ${res.data.savedCount} 条排班记录`)
      loadSchedulePreview() // 刷新预览
    }
  } catch (error) {
    console.error('保存排班失败:', error)
    ElMessage.error('保存排班失败')
  } finally {
    saving.value = false
  }
}

const generateAndSaveSchedules = async () => {
  if (!batchForm.value.startDate || !batchForm.value.endDate) {
    ElMessage.warning('请选择开始日期和结束日期')
    return
  }

  try {
    saving.value = true
    const res = await adminAPI.generateAndSaveSchedules({
      startDate: formatDate(batchForm.value.startDate),
      endDate: formatDate(batchForm.value.endDate),
      timeslots: batchForm.value.timeslots.map(Number)
    })

    if (res.code === 200) {
      ElMessage.success('排班生成并保存成功')
      showBatchDialog.value = false
      loadSchedulePreview() // 刷新预览
    }
  } catch (error) {
    console.error('批量排班失败:', error)
    ElMessage.error('批量排班失败')
  } finally {
    saving.value = false
  }
}

const clearSchedules = async () => {
  if (!clearForm.value.startDate || !clearForm.value.endDate) {
    ElMessage.warning('请选择开始日期和结束日期')
    return
  }

  try {
    clearing.value = true
    const res = await adminAPI.clearSchedules({
      startDate: formatDate(clearForm.value.startDate),
      endDate: formatDate(clearForm.value.endDate)
    })

    if (res.code === 200) {
      ElMessage.success('排班清除成功')
      showClearDialog.value = false
      loadSchedulePreview() // 刷新预览
    }
  } catch (error) {
    console.error('清除排班失败:', error)
    ElMessage.error('清除排班失败')
  } finally {
    clearing.value = false
  }
}

// 生命周期
onMounted(() => {
  loadSchedulePreview()
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.dashboard-sidebar {
  width: 240px;
  background: white;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
}

.dashboard-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dashboard-header {
  background: white;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.schedule-calendar {
  overflow-x: auto;
}

.schedule-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px;
  min-height: 60px;
}

.shift-tag {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.shift-tag:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

.shift-morning {
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
  color: white;
}

.shift-afternoon {
  background: linear-gradient(135deg, #E6A23C 0%, #F3C77E 100%);
  color: white;
}

.shift-quota {
  font-weight: bold;
  margin-left: 4px;
}
</style>