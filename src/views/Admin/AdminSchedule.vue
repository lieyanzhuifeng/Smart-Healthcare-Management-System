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
          <el-text size="large">医生排班管理</el-text>
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
        <!-- 筛选和操作栏 -->
        <el-card style="margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div style="display: flex; gap: 12px; flex-wrap: wrap;">
              <el-select v-model="selectedDepartment" placeholder="选择科室" style="width: 150px;" clearable>
                <el-option label="全部科室" value="" />
                <el-option label="内科" value="内科" />
                <el-option label="外科" value="外科" />
                <el-option label="儿科" value="儿科" />
                <el-option label="妇产科" value="妇产科" />
                <el-option label="骨科" value="骨科" />
                <el-option label="眼科" value="眼科" />
              </el-select>
              
              <el-date-picker
                v-model="selectedWeek"
                type="week"
                format="YYYY 第 ww 周"
                placeholder="选择周"
                style="width: 200px;"
              />

              <el-input
                v-model="searchKeyword"
                placeholder="搜索医生姓名"
                style="width: 200px;"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>

            <div style="display: flex; gap: 12px;">
              <el-button type="primary" @click="showBatchScheduleDialog = true">
                <el-icon><Plus /></el-icon>
                批量排班
              </el-button>
              <el-button type="success" @click="exportSchedule">
                <el-icon><Download /></el-icon>
                导出排班表
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 排班日历视图 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">本周排班概览</span>
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button value="week">周视图</el-radio-button>
                <el-radio-button value="list">列表视图</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <!-- 周视图 -->
          <div v-if="viewMode === 'week'" class="schedule-calendar">
            <el-table :data="filteredDoctors" border style="width: 100%">
              <el-table-column prop="name" label="医生" width="120" fixed>
                <template #default="{ row }">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <el-avatar :size="32">{{ row.name.charAt(0) }}</el-avatar>
                    <div>
                      <div style="font-weight: bold;">{{ row.name }}</div>
                      <el-text size="small" type="info">{{ row.title }}</el-text>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="department" label="科室" width="100" />
              <el-table-column
                v-for="day in weekDays"
                :key="day.value"
                :label="day.label"
                width="140"
              >
                <template #default="{ row }">
                  <div class="schedule-cell">
                    <div
                      v-for="shift in row.schedule[day.value]"
                      :key="shift.id"
                      :class="['shift-tag', `shift-${shift.period}`]"
                      @click="editShift(row, day.value, shift)"
                    >
                      {{ shift.period === 'morning' ? '上午' : '下午' }}
                      <span class="shift-quota">{{ shift.current }}/{{ shift.max }}</span>
                    </div>
                    <el-button
                      v-if="row.schedule[day.value].length < 2"
                      type="primary"
                      link
                      size="small"
                      @click="addShift(row, day.value)"
                    >
                      <el-icon><Plus /></el-icon>
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 列表视图 -->
          <div v-else>
            <el-table :data="scheduleList" border style="width: 100%">
              <el-table-column prop="doctorName" label="医生" width="120" />
              <el-table-column prop="department" label="科室" width="100" />
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="period" label="时段" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.period === 'morning' ? 'success' : 'warning'">
                    {{ row.period === 'morning' ? '上午' : '下午' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="timeRange" label="时间范围" width="150" />
              <el-table-column prop="maxPatients" label="最大接诊数" width="120" />
              <el-table-column prop="currentPatients" label="已预约" width="100">
                <template #default="{ row }">
                  <el-text :type="row.currentPatients >= row.maxPatients ? 'danger' : 'success'">
                    {{ row.currentPatients }}
                  </el-text>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="editScheduleItem(row)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="deleteScheduleItem(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- 统计信息 -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
          <el-card>
            <el-statistic title="本周排班医生" :value="totalDoctors">
              <template #suffix>人</template>
            </el-statistic>
          </el-card>
          <el-card>
            <el-statistic title="总排班数" :value="totalShifts">
              <template #suffix>班次</template>
            </el-statistic>
          </el-card>
          <el-card>
            <el-statistic title="可预约数" :value="availableSlots">
              <template #suffix>个</template>
            </el-statistic>
          </el-card>
          <el-card>
            <el-statistic title="已预约数" :value="bookedSlots">
              <template #suffix>个</template>
            </el-statistic>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 添加/编辑排班对话框 -->
    <el-dialog
      v-model="showScheduleDialog"
      :title="isEditMode ? '编辑排班' : '添加排班'"
      width="500px"
    >
      <el-form :model="scheduleForm" label-width="100px">
        <el-form-item label="医生">
          <el-text>{{ scheduleForm.doctorName }}</el-text>
        </el-form-item>
        <el-form-item label="日期">
          <el-text>{{ scheduleForm.date }}</el-text>
        </el-form-item>
        <el-form-item label="时段">
          <el-radio-group v-model="scheduleForm.period">
            <el-radio value="morning">上午 (08:00-12:00)</el-radio>
            <el-radio value="afternoon">下午 (14:00-18:00)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="最大接诊数">
          <el-input-number v-model="scheduleForm.maxPatients" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="诊室">
          <el-input v-model="scheduleForm.room" placeholder="例如：门诊楼3楼301室" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showScheduleDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSchedule">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量排班对话框 -->
    <el-dialog
      v-model="showBatchScheduleDialog"
      title="批量排班"
      width="600px"
    >
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="选择医生">
          <el-select v-model="batchForm.doctors" multiple placeholder="请选择医生" style="width: 100%;">
            <el-option
              v-for="doctor in allDoctors"
              :key="doctor.id"
              :label="`${doctor.name} - ${doctor.department}`"
              :value="doctor.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="batchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="工作日">
          <el-checkbox-group v-model="batchForm.weekdays">
            <el-checkbox value="1">周一</el-checkbox>
            <el-checkbox value="2">周二</el-checkbox>
            <el-checkbox value="3">周三</el-checkbox>
            <el-checkbox value="4">周四</el-checkbox>
            <el-checkbox value="5">周五</el-checkbox>
            <el-checkbox value="6">周六</el-checkbox>
            <el-checkbox value="0">周日</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="时段">
          <el-checkbox-group v-model="batchForm.periods">
            <el-checkbox value="morning">上午</el-checkbox>
            <el-checkbox value="afternoon">下午</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="最大接诊数">
          <el-input-number v-model="batchForm.maxPatients" :min="1" :max="50" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchScheduleDialog = false">取消</el-button>
        <el-button type="primary" @click="saveBatchSchedule">确定</el-button>
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
  DataAnalysis, Setting, Bell, ArrowDown, Plus, Search, Download
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('schedule')
const viewMode = ref('week')
const selectedDepartment = ref('')
const selectedWeek = ref(new Date())
const searchKeyword = ref('')
const showScheduleDialog = ref(false)
const showBatchScheduleDialog = ref(false)
const isEditMode = ref(false)

const weekDays = [
  { label: '周一', value: 'mon' },
  { label: '周二', value: 'tue' },
  { label: '周三', value: 'wed' },
  { label: '周四', value: 'thu' },
  { label: '周五', value: 'fri' },
  { label: '周六', value: 'sat' },
  { label: '周日', value: 'sun' }
]

const allDoctors = ref([
  {
    id: 1,
    name: '张医生',
    title: '主任医师',
    department: '内科',
    schedule: {
      mon: [{ id: 1, period: 'morning', current: 15, max: 30 }],
      tue: [{ id: 2, period: 'morning', current: 20, max: 30 }, { id: 3, period: 'afternoon', current: 18, max: 25 }],
      wed: [{ id: 4, period: 'afternoon', current: 12, max: 25 }],
      thu: [{ id: 5, period: 'morning', current: 25, max: 30 }],
      fri: [{ id: 6, period: 'morning', current: 22, max: 30 }],
      sat: [],
      sun: []
    }
  },
  {
    id: 2,
    name: '李医生',
    title: '副主任医师',
    department: '外科',
    schedule: {
      mon: [{ id: 7, period: 'afternoon', current: 10, max: 20 }],
      tue: [{ id: 8, period: 'morning', current: 15, max: 25 }],
      wed: [{ id: 9, period: 'morning', current: 18, max: 25 }, { id: 10, period: 'afternoon', current: 16, max: 20 }],
      thu: [{ id: 11, period: 'afternoon', current: 14, max: 20 }],
      fri: [{ id: 12, period: 'morning', current: 20, max: 25 }],
      sat: [{ id: 13, period: 'morning', current: 8, max: 15 }],
      sun: []
    }
  },
  {
    id: 3,
    name: '王医生',
    title: '主治医师',
    department: '儿科',
    schedule: {
      mon: [{ id: 14, period: 'morning', current: 28, max: 35 }, { id: 15, period: 'afternoon', current: 25, max: 30 }],
      tue: [{ id: 16, period: 'morning', current: 30, max: 35 }],
      wed: [{ id: 17, period: 'morning', current: 32, max: 35 }],
      thu: [{ id: 18, period: 'morning', current: 29, max: 35 }, { id: 19, period: 'afternoon', current: 27, max: 30 }],
      fri: [{ id: 20, period: 'morning', current: 31, max: 35 }],
      sat: [{ id: 21, period: 'morning', current: 20, max: 25 }],
      sun: []
    }
  },
  {
    id: 4,
    name: '赵医生',
    title: '主任医师',
    department: '妇产科',
    schedule: {
      mon: [{ id: 22, period: 'morning', current: 12, max: 20 }],
      tue: [{ id: 23, period: 'afternoon', current: 10, max: 18 }],
      wed: [{ id: 24, period: 'morning', current: 15, max: 20 }],
      thu: [{ id: 25, period: 'morning', current: 14, max: 20 }],
      fri: [{ id: 26, period: 'morning', current: 16, max: 20 }, { id: 27, period: 'afternoon', current: 13, max: 18 }],
      sat: [],
      sun: []
    }
  }
])

const scheduleForm = ref({
  doctorId: null,
  doctorName: '',
  date: '',
  period: 'morning',
  maxPatients: 30,
  room: ''
})

const batchForm = ref({
  doctors: [],
  dateRange: [],
  weekdays: ['1', '2', '3', '4', '5'],
  periods: ['morning', 'afternoon'],
  maxPatients: 30
})

const filteredDoctors = computed(() => {
  let result = allDoctors.value

  if (selectedDepartment.value) {
    result = result.filter(d => d.department === selectedDepartment.value)
  }

  if (searchKeyword.value) {
    result = result.filter(d => d.name.includes(searchKeyword.value))
  }

  return result
})

const scheduleList = computed(() => {
  const list = []
  allDoctors.value.forEach(doctor => {
    weekDays.forEach(day => {
      doctor.schedule[day.value].forEach(shift => {
        list.push({
          id: shift.id,
          doctorName: doctor.name,
          department: doctor.department,
          date: day.label,
          period: shift.period,
          timeRange: shift.period === 'morning' ? '08:00-12:00' : '14:00-18:00',
          maxPatients: shift.max,
          currentPatients: shift.current,
          status: shift.current >= shift.max ? '已满' : '可预约'
        })
      })
    })
  })
  return list
})

const totalDoctors = computed(() => filteredDoctors.value.length)
const totalShifts = computed(() => scheduleList.value.length)
const availableSlots = computed(() => scheduleList.value.reduce((sum, item) => sum + (item.maxPatients - item.currentPatients), 0))
const bookedSlots = computed(() => scheduleList.value.reduce((sum, item) => sum + item.currentPatients, 0))

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

const addShift = (doctor, day) => {
  scheduleForm.value = {
    doctorId: doctor.id,
    doctorName: doctor.name,
    date: weekDays.find(d => d.value === day).label,
    period: doctor.schedule[day].length === 0 ? 'morning' : 'afternoon',
    maxPatients: 30,
    room: ''
  }
  isEditMode.value = false
  showScheduleDialog.value = true
}

const editShift = (doctor, day, shift) => {
  scheduleForm.value = {
    doctorId: doctor.id,
    doctorName: doctor.name,
    date: weekDays.find(d => d.value === day).label,
    period: shift.period,
    maxPatients: shift.max,
    room: ''
  }
  isEditMode.value = true
  showScheduleDialog.value = true
}

const saveSchedule = () => {
  ElMessage.success('排班保存成功')
  showScheduleDialog.value = false
}

const saveBatchSchedule = async () => {
  if (batchForm.value.doctors.length === 0) {
    ElMessage.warning('请选择医生')
    return
  }
  if (!batchForm.value.dateRange || batchForm.value.dateRange.length === 0) {
    ElMessage.warning('请选择日期范围')
    return
  }
  
  try {
    const [startDate, endDate] = batchForm.value.dateRange
    const res = await adminAPI.generateAndSaveSchedules({
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
      timeslots: batchForm.value.periods.map(p => p === 'morning' ? 1 : 2)
    })
    
    if (res.code === 200) {
      ElMessage.success('批量排班成功')
      showBatchScheduleDialog.value = false
      await loadSchedulePreview()
    }
  } catch (error) {
    ElMessage.error('批量排班失败')
  }
}

const editScheduleItem = (row) => {
  ElMessage.info(`编辑排班：${row.doctorName} - ${row.date}`)
}

const deleteScheduleItem = (row) => {
  ElMessageBox.confirm('确定要删除这个排班吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

const exportSchedule = () => {
  ElMessage.success('排班表导出成功')
}

const getStatusType = (status) => {
  return status === '已满' ? 'danger' : 'success'
}

onMounted(async () => {
  await loadSchedulePreview()
})

const loadSchedulePreview = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const res = await adminAPI.previewSchedules({ date: today })
    if (res.code === 200 && res.data) {
      // Update schedule data based on backend response
      console.log('Schedule data:', res.data)
    }
  } catch (error) {
    console.error('加载排班预览失败:', error)
  }
}
</script>

<style scoped>
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
