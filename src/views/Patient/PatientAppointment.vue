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
        <el-menu-item index="overview" @click="$router.push('/patient')">
          <el-icon><House /></el-icon>
          <span>首页概览</span>
        </el-menu-item>
        <el-menu-item index="appointment">
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
            <el-breadcrumb-item>预约挂号</el-breadcrumb-item>
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
        <el-row :gutter="20">
          <!-- 左侧：预约表单 -->
          <el-col :span="16">
            <el-card>
              <template #header>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-icon color="#409EFF"><Calendar /></el-icon>
                  <span style="font-weight: bold;">预约挂号</span>
                </div>
              </template>

              <el-steps :active="currentStep" finish-status="success" style="margin-bottom: 30px;">
                <el-step title="选择科室" />
                <el-step title="选择医生" />
                <el-step title="选择时间" />
                <el-step title="确认信息" />
              </el-steps>

              <!-- 步骤1: 选择科室 -->
              <div v-if="currentStep === 0">
                <el-input
                  v-model="searchDepartment"
                  placeholder="搜索科室"
                  :prefix-icon="Search"
                  style="margin-bottom: 20px;"
                />
                <el-row :gutter="16">
                  <el-col
                    v-for="dept in filteredDepartments"
                    :key="dept.id"
                    :span="8"
                    style="margin-bottom: 16px;"
                  >
                    <el-card
                      shadow="hover"
                      :class="{ 'selected-card': appointmentForm.departmentId === dept.id }"
                      @click="selectDepartment(dept)"
                      style="cursor: pointer;"
                    >
                      <div style="text-align: center;">
                        <el-icon :size="40" :color="dept.color">
                          <component :is="dept.icon" />
                        </el-icon>
                        <div style="margin-top: 12px; font-weight: bold;">{{ dept.name }}</div>
                        <el-text type="info" size="small">{{ dept.doctorCount }} 位医生</el-text>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>

              <!-- 步骤2: 选择医生 -->
              <div v-if="currentStep === 1">
                <el-table :data="doctors" style="width: 100%">
                  <el-table-column type="selection" width="55" />
                  <el-table-column label="医生" width="200">
                    <template #default="{ row }">
                      <div style="display: flex; align-items: center; gap: 12px;">
                        <el-avatar :size="50" :src="row.avatar" />
                        <div>
                          <div style="font-weight: bold;">{{ row.name }}</div>
                          <el-tag size="small" :type="row.titleType">{{ row.title }}</el-tag>
                        </div>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="specialty" label="专长" />
                  <el-table-column prop="experience" label="从业年限" width="100" />
                  <el-table-column label="评分" width="120">
                    <template #default="{ row }">
                      <el-rate v-model="row.rating" disabled show-score />
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                      <el-button
                        type="primary"
                        size="small"
                        @click="selectDoctor(row)"
                      >
                        选择
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <!-- 步骤3: 选择时间 -->
              <div v-if="currentStep === 2">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div style="margin-bottom: 16px;">
                      <el-text style="font-weight: bold;">选择日期</el-text>
                    </div>
                    <el-calendar v-model="appointmentForm.date" style="height: 400px;">
                      <template #date-cell="{ data }">
                        <div
                          :class="{ 'available-date': isDateAvailable(data.day) }"
                          @click="selectDate(data.day)"
                        >
                          {{ data.day.split('-').slice(2).join('-') }}
                        </div>
                      </template>
                    </el-calendar>
                  </el-col>
                  <el-col :span="12">
                    <div style="margin-bottom: 16px;">
                      <el-text style="font-weight: bold;">选择时段</el-text>
                    </div>
                    <div v-if="appointmentForm.date">
                      <div style="margin-bottom: 20px;">
                        <el-text type="info">上午时段</el-text>
                        <el-row :gutter="12" style="margin-top: 12px;">
                          <el-col
                            v-for="slot in morningSlots"
                            :key="slot.time"
                            :span="8"
                            style="margin-bottom: 12px;"
                          >
                            <el-button
                              :type="appointmentForm.time === slot.time ? 'primary' : 'default'"
                              :disabled="!slot.available"
                              @click="selectTime(slot.time)"
                              style="width: 100%;"
                            >
                              {{ slot.time }}
                              <el-text v-if="!slot.available" type="info" size="small">已满</el-text>
                            </el-button>
                          </el-col>
                        </el-row>
                      </div>
                      <div>
                        <el-text type="info">下午时段</el-text>
                        <el-row :gutter="12" style="margin-top: 12px;">
                          <el-col
                            v-for="slot in afternoonSlots"
                            :key="slot.time"
                            :span="8"
                            style="margin-bottom: 12px;"
                          >
                            <el-button
                              :type="appointmentForm.time === slot.time ? 'primary' : 'default'"
                              :disabled="!slot.available"
                              @click="selectTime(slot.time)"
                              style="width: 100%;"
                            >
                              {{ slot.time }}
                              <el-text v-if="!slot.available" type="info" size="small">已满</el-text>
                            </el-button>
                          </el-col>
                        </el-row>
                      </div>
                    </div>
                    <el-empty v-else description="请先选择日期" :image-size="100" />
                  </el-col>
                </el-row>
              </div>

              <!-- 步骤4: 确认信息 -->
              <div v-if="currentStep === 3">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="就诊科室">
                    {{ selectedDepartment?.name }}
                  </el-descriptions-item>
                  <el-descriptions-item label="就诊医生">
                    {{ selectedDoctor?.name }} ({{ selectedDoctor?.title }})
                  </el-descriptions-item>
                  <el-descriptions-item label="就诊日期">
                    {{ appointmentForm.date }}
                  </el-descriptions-item>
                  <el-descriptions-item label="就诊时间">
                    {{ appointmentForm.time }}
                  </el-descriptions-item>
                  <el-descriptions-item label="挂号费用">
                    <el-text type="danger" style="font-size: 18px; font-weight: bold;">
                      ¥{{ selectedDoctor?.fee || 0 }}
                    </el-text>
                  </el-descriptions-item>
                </el-descriptions>

                <el-divider />

                <el-form :model="appointmentForm" label-width="100px">
                  <el-form-item label="就诊人">
                    <el-input v-model="appointmentForm.patientName" placeholder="请输入就诊人姓名" />
                  </el-form-item>
                  <el-form-item label="联系电话">
                    <el-input v-model="appointmentForm.phone" placeholder="请输入联系电话" />
                  </el-form-item>
                  <el-form-item label="身份证号">
                    <el-input v-model="appointmentForm.idCard" placeholder="请输入身份证号" />
                  </el-form-item>
                  <el-form-item label="病情描述">
                    <el-input
                      v-model="appointmentForm.description"
                      type="textarea"
                      :rows="4"
                      placeholder="请简要描述您的病情（选填）"
                    />
                  </el-form-item>
                </el-form>
              </div>

              <!-- 操作按钮 -->
              <div style="margin-top: 30px; text-align: right;">
                <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
                <el-button
                  v-if="currentStep < 3"
                  type="primary"
                  @click="nextStep"
                  :disabled="!canProceed"
                >
                  下一步
                </el-button>
                <el-button
                  v-if="currentStep === 3"
                  type="primary"
                  @click="submitAppointment"
                  :loading="submitting"
                >
                  确认预约
                </el-button>
              </div>
            </el-card>
          </el-col>

          <!-- 右侧：我的预约 -->
          <el-col :span="8">
            <el-card>
              <template #header>
                <span style="font-weight: bold;">我的预约</span>
              </template>
              <el-timeline>
                <el-timeline-item
                  v-for="appointment in myAppointments"
                  :key="appointment.id"
                  :timestamp="appointment.date + ' ' + appointment.time"
                  :color="appointment.status === '待就诊' ? '#409EFF' : '#67C23A'"
                >
                  <el-card shadow="hover">
                    <div style="margin-bottom: 8px;">
                      <el-tag :type="appointment.status === '待就诊' ? 'warning' : 'success'">
                        {{ appointment.status }}
                      </el-tag>
                    </div>
                    <div style="margin-bottom: 4px;">
                      <el-text>{{ appointment.department }} - {{ appointment.doctor }}</el-text>
                    </div>
                    <div style="display: flex; gap: 8px; margin-top: 12px;">
                      <el-button size="small" type="primary" link>查看详情</el-button>
                      <el-button
                        v-if="appointment.status === '待就诊'"
                        size="small"
                        type="danger"
                        link
                        @click="cancelAppointment(appointment.id)"
                      >
                        取消预约
                      </el-button>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-if="myAppointments.length === 0" description="暂无预约记录" :image-size="100" />
            </el-card>

            <!-- 温馨提示 -->
            <el-card style="margin-top: 20px;">
              <template #header>
                <span style="font-weight: bold;">温馨提示</span>
              </template>
              <el-alert
                title="预约须知"
                type="info"
                :closable="false"
                style="margin-bottom: 12px;"
              >
                <ul style="margin: 8px 0; padding-left: 20px;">
                  <li>请提前15分钟到达医院</li>
                  <li>请携带身份证和就诊卡</li>
                  <li>如需取消请提前24小时</li>
                  <li>爽约3次将影响信用</li>
                </ul>
              </el-alert>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { patientAPI } from '@/api'
import {
  House, Calendar, Document, DocumentCopy, Tickets,
  DataAnalysis, VideoCamera, Bell, ArrowDown, Search,
  User, Stethoscope, FirstAidKit, Operation, View
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('appointment')

// 预约表单
const currentStep = ref(0)
const submitting = ref(false)
const appointmentForm = ref({
  departmentId: null,
  doctorId: null,
  date: null,
  time: null,
  patientName: userStore.userName,
  phone: '',
  idCard: '',
  description: ''
})

// 科室数据
const searchDepartment = ref('')
const departments = ref([])
const doctors = ref([])
const myAppointments = ref([])

onMounted(async () => {
  await loadDepartments()
  await loadMyAppointments()
})

const loadDepartments = async () => {
  try {
    const res = await patientAPI.getOffices()
    if (res.code === 200 && res.data) {
      departments.value = res.data.map((office, index) => ({
        id: office.officeID,
        name: office.name,
        icon: 'Stethoscope',
        color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'][index % 5],
        doctorCount: 0
      }))
    }
  } catch (error) {
    ElMessage.error('加载科室列表失败')
  }
}

const filteredDepartments = computed(() => {
  if (!searchDepartment.value) return departments.value
  return departments.value.filter(dept =>
    dept.name.includes(searchDepartment.value)
  )
})

const selectedDepartment = computed(() =>
  departments.value.find(d => d.id === appointmentForm.value.departmentId)
)

// 医生数据
const selectedDoctor = computed(() =>
  doctors.value.find(d => d.id === appointmentForm.value.doctorId)
)

// 时间段数据
const morningSlots = ref([
  { time: '08:00', available: true },
  { time: '08:30', available: true },
  { time: '09:00', available: false },
  { time: '09:30', available: true },
  { time: '10:00', available: true },
  { time: '10:30', available: true },
  { time: '11:00', available: true },
  { time: '11:30', available: false }
])

const afternoonSlots = ref([
  { time: '14:00', available: true },
  { time: '14:30', available: true },
  { time: '15:00', available: true },
  { time: '15:30', available: false },
  { time: '16:00', available: true },
  { time: '16:30', available: true },
  { time: '17:00', available: true },
  { time: '17:30', available: true }
])

const selectDepartment = async (dept) => {
  appointmentForm.value.departmentId = dept.id
  
  try {
    const res = await patientAPI.getDoctorsByOffice(dept.id)
    if (res.code === 200 && res.data) {
      doctors.value = res.data.map(doc => ({
        id: doc.doctorID,
        name: doc.doctor_name,
        title: doc.position_name || '医师',
        titleType: 'success',
        specialty: doc.expertise_name || '全科',
        experience: `${doc.age || 0}年`,
        rating: 4.5,
        fee: 30,
        avatar: '/placeholder.svg?height=50&width=50',
        department: doc.office_name
      }))
    }
  } catch (error) {
    ElMessage.error('加载医生列表失败')
  }
}

// Updated selectDoctor to load doctor's schedule
const selectDoctor = async (doctor) => {
  appointmentForm.value.doctorId = doctor.id
  
  // Load doctor's schedule for the next 7 days
  try {
    const today = new Date()
    const dateStr = today.toISOString().split('T')[0]
    const res = await patientAPI.getDoctorSchedule({
      doctorId: doctor.id,
      date: dateStr
    })
    
    if (res.code === 200 && res.data) {
      // Update time slots based on schedule
      updateTimeSlots(res.data)
    }
  } catch (error) {
    console.error('加载医生排班失败:', error)
  }
  
  nextStep()
}

const updateTimeSlots = (scheduleData) => {
  // Update morning and afternoon slots based on backend data
  if (scheduleData.morning) {
    morningSlots.value = scheduleData.morning.map(slot => ({
      time: slot.time,
      available: slot.available,
      sectionId: slot.sectionId
    }))
  }
  
  if (scheduleData.afternoon) {
    afternoonSlots.value = scheduleData.afternoon.map(slot => ({
      time: slot.time,
      available: slot.available,
      sectionId: slot.sectionId
    }))
  }
}

const canProceed = computed(() => {
  if (currentStep.value === 0) return appointmentForm.value.departmentId !== null
  if (currentStep.value === 1) return appointmentForm.value.doctorId !== null
  if (currentStep.value === 2) return appointmentForm.value.date && appointmentForm.value.time
  return true
})

const nextStep = () => {
  if (canProceed.value && currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const submitAppointment = async () => {
  if (!appointmentForm.value.patientName || !appointmentForm.value.phone) {
    ElMessage.warning('请填写完整的就诊信息')
    return
  }

  try {
    submitting.value = true
    
    // Find the selected time slot to get sectionId
    const allSlots = [...morningSlots.value, ...afternoonSlots.value]
    const selectedSlot = allSlots.find(slot => slot.time === appointmentForm.value.time)
    
    if (!selectedSlot || !selectedSlot.sectionId) {
      ElMessage.error('请选择有效的时间段')
      return
    }
    
    const res = await patientAPI.createAppointment({
      sectionId: selectedSlot.sectionId
    })
    
    if (res.code === 200) {
      ElMessage.success('预约成功！')
      
      // 重置表单
      currentStep.value = 0
      appointmentForm.value = {
        departmentId: null,
        doctorId: null,
        date: null,
        time: null,
        patientName: userStore.userName,
        phone: '',
        idCard: '',
        description: ''
      }
      
      // 刷新预约列表
      await loadMyAppointments()
    }
  } catch (error) {
    ElMessage.error(error.message || '预约失败，请重试')
  } finally {
    submitting.value = false
  }
}

const loadMyAppointments = async () => {
  try {
    const res = await patientAPI.getAppointments()
    if (res.code === 200 && res.data) {
      myAppointments.value = res.data.appointments.map(appt => ({
        id: appt.appointmentID,
        date: appt.date,
        time: appt.starttime,
        department: appt.office_name,
        doctor: appt.doctor_name,
        status: appt.state === 1 ? '待就诊' : '已完成'
      }))
    }
  } catch (error) {
    console.error('加载预约列表失败:', error)
  }
}

const cancelAppointment = async (id) => {
  try {
    await ElMessageBox.confirm('确定要取消这个预约吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await patientAPI.cancelAppointment(id)
    if (res.code === 200) {
      ElMessage.success('已取消预约')
      await loadMyAppointments()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消预约失败')
    }
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
  } else {
    ElMessage.info(`点击了：${command}`)
  }
}

const isDateAvailable = (date) => {
  const today = new Date()
  const checkDate = new Date(date)
  return checkDate >= today
}

const selectDate = (date) => {
  if (isDateAvailable(date)) {
    appointmentForm.value.date = date
  }
}

const selectTime = (time) => {
  appointmentForm.value.time = time
}
</script>

<style scoped>
.selected-card {
  border: 2px solid #409EFF;
  background: #ecf5ff;
}

.available-date {
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.available-date:hover {
  background: #ecf5ff;
  color: #409EFF;
}
</style>
