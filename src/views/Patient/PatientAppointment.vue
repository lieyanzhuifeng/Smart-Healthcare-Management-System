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
          <el-badge :value="reminderCount" class="item">
            <el-icon :size="20"><Bell /></el-icon>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span style="cursor: pointer; display: flex; align-items: center; gap: 8px;">
              <el-avatar :size="32">{{ userStore.userName?.charAt(0) || 'P' }}</el-avatar>
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
                  <el-text type="info" size="small">(真实API数据)</el-text>
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
                  clearable
                />
                <el-row :gutter="16" v-loading="loadingDepartments">
                  <el-col
                    v-for="dept in filteredDepartments"
                    :key="dept.officeID"
                    :span="8"
                    style="margin-bottom: 16px;"
                  >
                    <el-card
                      shadow="hover"
                      :class="{ 'selected-card': appointmentForm.officeId === dept.officeID }"
                      @click="selectDepartment(dept)"
                      style="cursor: pointer; height: 120px; display: flex; align-items: center; justify-content: center;"
                    >
                      <div style="text-align: center;">
                        <el-icon :size="40" color="#409EFF">
                          <FirstAidKit />
                        </el-icon>
                        <div style="margin-top: 12px; font-weight: bold;">{{ dept.name }}</div>
                        <!-- <el-text type="info" size="small">{{ dept.doctorCount || 0 }} 位医生</el-text> -->
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
                <div v-if="filteredDepartments.length === 0 && !loadingDepartments" style="text-align: center; padding: 40px;">
                  <el-empty description="暂无科室数据" />
                </div>
              </div>

              <!-- 步骤2: 选择医生 -->
              <div v-if="currentStep === 1">
                <div style="margin-bottom: 16px;">
                  <el-text strong>当前科室：</el-text>
                  <el-tag type="primary">{{ selectedDepartment?.name }}</el-tag>
                </div>
                <el-table 
                  :data="doctors" 
                  style="width: 100%" 
                  v-loading="loadingDoctors"
                  empty-text="该科室暂无医生"
                >
                  <el-table-column label="医生" width="200">
                    <template #default="{ row }">
                      <div style="display: flex; align-items: center; gap: 12px;">
                        <el-avatar :size="50">{{ row.doctor_name?.charAt(0) || 'D' }}</el-avatar>
                        <div>
                          <div style="font-weight: bold;">{{ row.doctor_name }}</div>
                          <el-tag size="small" type="success">{{ row.position_name }}</el-tag>
                        </div>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="office_name" label="科室" />
                  <el-table-column prop="expertise_name" label="专长" />
                  <el-table-column prop="age" label="年龄" width="80" />
                  <el-table-column label="患者数量" width="100">
                    <template #default="{ row }">
                      <el-text type="info">{{ row.NumberOfPatients || 0 }}人</el-text>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                      <el-button
                        type="primary"
                        size="small"
                        @click="selectDoctor(row)"
                        :disabled="loadingSchedule"
                      >
                        {{ loadingSchedule && appointmentForm.doctorId === row.doctorID ? '加载中...' : '选择' }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <!-- 步骤3: 选择时间 -->
              <div v-if="currentStep === 2">
                <div style="margin-bottom: 16px;">
                  <el-text strong>当前医生：</el-text>
                  <el-tag type="success">{{ selectedDoctor?.doctor_name }} - {{ selectedDoctor?.position_name }}</el-tag>
                </div>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div style="margin-bottom: 16px;">
                      <el-text style="font-weight: bold;">选择日期</el-text>
                    </div>
                    <el-date-picker
                      v-model="selectedDate"
                      type="date"
                      placeholder="选择日期"
                      style="width: 100%; margin-bottom: 20px;"
                      :disabled-date="disabledDate"
                      @change="loadDoctorSchedule"
                    />
                    
                    <div v-if="doctorSchedule.length > 0">
                      <el-text type="info" style="margin-bottom: 12px; display: block;">可用排班时段</el-text>
                      <div class="time-slots-container">
                        <div
                          v-for="schedule in doctorSchedule"
                          :key="schedule.sectionID"
                          :class="['time-slot', { 'selected': appointmentForm.sectionId === schedule.sectionID }]"
                          @click="selectTimeSlot(schedule)"
                        >
                          <div class="time-range">
                            {{ schedule.starttime }} - {{ schedule.endtime }}
                          </div>
                          <div class="slot-info">
                            <el-text type="info" size="small">
                              剩余: {{ schedule.restappiontment }} / {{ schedule.totalappiontment }}
                            </el-text>
                          </div>
                          <div v-if="schedule.restappiontment === 0" class="slot-full">
                            已满
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-else-if="selectedDate && !loadingSchedule">
                      <el-empty description="该日期暂无排班" :image-size="80" />
                    </div>
                  </el-col>
                  
                  <el-col :span="12">
                    <div style="margin-bottom: 16px;">
                      <el-text style="font-weight: bold;">预约信息</el-text>
                    </div>
                    <el-card v-if="appointmentForm.sectionId" shadow="never">
                      <template #header>
                        <span style="font-weight: bold;">预约详情</span>
                      </template>
                      <el-descriptions :column="1" size="small">
                        <el-descriptions-item label="医生">
                          {{ selectedDoctor?.doctor_name }}
                        </el-descriptions-item>
                        <el-descriptions-item label="科室">
                          {{ selectedDoctor?.office_name }}
                        </el-descriptions-item>
                        <el-descriptions-item label="专长">
                          {{ selectedDoctor?.expertise_name }}
                        </el-descriptions-item>
                        <el-descriptions-item label="日期">
                          {{ selectedDateFormatted }}
                        </el-descriptions-item>
                        <el-descriptions-item label="时间">
                          {{ selectedTimeSlotInfo?.starttime }} - {{ selectedTimeSlotInfo?.endtime }}
                        </el-descriptions-item>
                        <el-descriptions-item label="剩余名额">
                          <el-text :type="selectedTimeSlotInfo?.restappiontment > 0 ? 'success' : 'danger'">
                            {{ selectedTimeSlotInfo?.restappiontment }}
                          </el-text>
                        </el-descriptions-item>
                      </el-descriptions>
                    </el-card>
                    <el-card v-else shadow="never">
                      <el-empty description="请选择时间段" :image-size="80" />
                    </el-card>
                  </el-col>
                </el-row>
              </div>

              <!-- 步骤4: 确认信息 -->
              <div v-if="currentStep === 3">
                <el-alert
                  title="请确认预约信息"
                  type="info"
                  :closable="false"
                  style="margin-bottom: 20px;"
                />
                
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="就诊科室" label-class-name="desc-label">
                    {{ selectedDepartment?.name }}
                  </el-descriptions-item>
                  <el-descriptions-item label="就诊医生">
                    {{ selectedDoctor?.doctor_name }} ({{ selectedDoctor?.position_name }})
                  </el-descriptions-item>
                  <el-descriptions-item label="医生专长">
                    {{ selectedDoctor?.expertise_name }}
                  </el-descriptions-item>
                  <el-descriptions-item label="就诊日期">
                    {{ selectedDateFormatted }}
                  </el-descriptions-item>
                  <el-descriptions-item label="就诊时间">
                    {{ selectedTimeSlotInfo?.starttime }} - {{ selectedTimeSlotInfo?.endtime }}
                  </el-descriptions-item>
                  <el-descriptions-item label="预约状态">
                    <el-tag type="success">待就诊</el-tag>
                  </el-descriptions-item>
                </el-descriptions>

                <el-divider />

                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                  <el-text type="info">
                    <el-icon><InfoFilled /></el-icon>
                    温馨提示：请按时就诊，如需取消请提前操作
                  </el-text>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div style="margin-top: 30px; text-align: right;">
                <el-button 
                  v-if="currentStep > 0" 
                  @click="prevStep"
                  :disabled="submitting"
                >
                  上一步
                </el-button>
                <el-button
                  v-if="currentStep < 3"
                  type="primary"
                  @click="nextStep"
                  :disabled="!canProceed || submitting"
                  :loading="loadingSchedule"
                >
                  {{ currentStep === 2 && loadingSchedule ? '加载中...' : '下一步' }}
                </el-button>
                <el-button
                  v-if="currentStep === 3"
                  type="primary"
                  @click="submitAppointment"
                  :loading="submitting"
                >
                  {{ submitting ? '预约中...' : '确认预约' }}
                </el-button>
              </div>
            </el-card>
          </el-col>

          <!-- 右侧：我的预约 -->
          <el-col :span="8">
            <el-card>
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-weight: bold;">我的预约</span>
                  <el-button type="primary" link @click="loadMyAppointments">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              
              <div v-loading="loadingAppointments">
                <el-timeline>
                  <el-timeline-item
                    v-for="appointment in myAppointments.slice().reverse()"
                    :key="appointment.appointmentID"
                    :timestamp="appointment.date + ' ' + appointment.starttime"
                    :color="getAppointmentColor(appointment.state)"
                  >
                    <el-card shadow="hover" size="small">
                      <div style="margin-bottom: 8px;">
                        <el-tag :type="getAppointmentStatusType(appointment.state)" size="small">
                          {{ getAppointmentStatusText(appointment.state) }}
                        </el-tag>
                      </div>
                      <div style="margin-bottom: 4px;">
                        <el-text strong>{{ appointment.office_name }} - {{ appointment.doctor_name }}</el-text>
                      </div>
                      <div style="margin-bottom: 4px;">
                        <el-text type="info" size="small">
                          {{ appointment.date }} {{ appointment.starttime }}-{{ appointment.endtime }}
                        </el-text>
                      </div>
                      <div style="display: flex; gap: 8px; margin-top: 12px;">
                        <el-button size="small" type="primary" link @click="viewAppointmentDetail(appointment)">
                          查看详情
                        </el-button>
                        <el-button
                          v-if="appointment.state === 1"
                          size="small"
                          type="danger"
                          link
                          @click="cancelAppointment(appointment.appointmentID)"
                          :loading="cancelingAppointmentId === appointment.appointmentID"
                        >
                          {{ cancelingAppointmentId === appointment.appointmentID ? '取消中...' : '取消预约' }}
                        </el-button>
                      </div>
                    </el-card>
                  </el-timeline-item>
                </el-timeline>
                <el-empty 
                  v-if="myAppointments.length === 0 && !loadingAppointments" 
                  description="暂无预约记录" 
                  :image-size="100" 
                />
              </div>
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
                <ul style="margin: 8px 0; padding-left: 20px; font-size: 12px;">
                  <li>请提前15分钟到达医院候诊</li>
                  <li>请携带有效身份证件和医保卡</li>
                  <li>如需取消请至少提前2小时操作</li>
                  <li>连续爽约3次将暂停预约权限</li>
                  <li>如有特殊情况请及时联系医院</li>
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
  FirstAidKit, Refresh, InfoFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const activeMenu = ref('appointment')

// 预约表单
const currentStep = ref(0)
const submitting = ref(false)
const loadingDepartments = ref(false)
const loadingDoctors = ref(false)
const loadingSchedule = ref(false)
const loadingAppointments = ref(false)
const cancelingAppointmentId = ref(null)

const appointmentForm = ref({
  officeId: null,
  doctorId: null,
  sectionId: null
})

// 数据
const searchDepartment = ref('')
const departments = ref([])
const doctors = ref([])
const doctorSchedule = ref([])
const myAppointments = ref([])
const selectedDate = ref(new Date())

// 计算属性
const filteredDepartments = computed(() => {
  if (!searchDepartment.value) return departments.value
  return departments.value.filter(dept =>
    dept.name.toLowerCase().includes(searchDepartment.value.toLowerCase())
  )
})

const selectedDepartment = computed(() =>
  departments.value.find(d => d.officeID === appointmentForm.value.officeId)
)

const selectedDoctor = computed(() =>
  doctors.value.find(d => d.doctorID === appointmentForm.value.doctorId)
)

const selectedTimeSlotInfo = computed(() =>
  doctorSchedule.value.find(s => s.sectionID === appointmentForm.value.sectionId)
)

const selectedDateFormatted = computed(() => {
  if (!selectedDate.value) return ''
  return new Date(selectedDate.value).toISOString().split('T')[0]
})

const canProceed = computed(() => {
  if (currentStep.value === 0) return appointmentForm.value.officeId !== null
  if (currentStep.value === 1) return appointmentForm.value.doctorId !== null
  if (currentStep.value === 2) return appointmentForm.value.sectionId !== null
  return true
})

const reminderCount = computed(() => {
  return myAppointments.value.filter(appt => appt.state === 1).length
})

// 生命周期
onMounted(async () => {
  await loadDepartments()
  await loadMyAppointments()
})

// API调用方法
const loadDepartments = async () => {
  try {
    loadingDepartments.value = true
    const res = await patientAPI.getOffices()
    if (res.code === 200 && res.data) {
      departments.value = res.data
    } else {
      ElMessage.warning('获取科室列表失败')
    }
  } catch (error) {
    console.error('加载科室列表失败:', error)
    ElMessage.error('加载科室列表失败')
  } finally {
    loadingDepartments.value = false
  }
}

const loadDoctorsByOffice = async (officeId) => {
  try {
    loadingDoctors.value = true
    const res = await patientAPI.getDoctorsByOffice(officeId)
    if (res.code === 200 && res.data) {
      doctors.value = res.data
    } else {
      ElMessage.warning('获取医生列表失败')
      doctors.value = []
    }
  } catch (error) {
    console.error('加载医生列表失败:', error)
    ElMessage.error('加载医生列表失败')
    doctors.value = []
  } finally {
    loadingDoctors.value = false
  }
}

const loadDoctorSchedule = async () => {
  if (!appointmentForm.value.doctorId || !selectedDate.value) return
  
  try {
    loadingSchedule.value = true
    const dateStr = new Date(selectedDate.value).toISOString().split('T')[0]
    const res = await patientAPI.getDoctorSchedule({
      doctorId: appointmentForm.value.doctorId,
      date: dateStr
    })
    
    if (res.code === 200 && res.data) {
      doctorSchedule.value = Array.isArray(res.data) ? res.data : []
      // 重置选中的时间段
      appointmentForm.value.sectionId = null
    } else {
      doctorSchedule.value = []
      ElMessage.warning('该医生在该日期暂无排班')
    }
  } catch (error) {
    console.error('加载医生排班失败:', error)
    ElMessage.error('加载医生排班失败')
    doctorSchedule.value = []
  } finally {
    loadingSchedule.value = false
  }
}

const loadMyAppointments = async () => {
  try {
    loadingAppointments.value = true
    const res = await patientAPI.getAppointments()
    if (res.code === 200 && res.data) {
      myAppointments.value = res.data.appointments || []
    } else {
      myAppointments.value = []
    }
  } catch (error) {
    console.error('加载预约列表失败:', error)
    ElMessage.error('加载预约列表失败')
    myAppointments.value = []
  } finally {
    loadingAppointments.value = false
  }
}

// 交互方法
const selectDepartment = async (dept) => {
  appointmentForm.value.officeId = dept.officeID
  appointmentForm.value.doctorId = null
  appointmentForm.value.sectionId = null
  await loadDoctorsByOffice(dept.officeID)
}

const selectDoctor = async (doctor) => {
  appointmentForm.value.doctorId = doctor.doctorID
  appointmentForm.value.sectionId = null
  // 默认选择今天
  selectedDate.value = new Date()
  await loadDoctorSchedule()
  nextStep()
}

const selectTimeSlot = (schedule) => {
  if (schedule.restappiontment > 0) {
    appointmentForm.value.sectionId = schedule.sectionID
  } else {
    ElMessage.warning('该时段已满，请选择其他时段')
  }
}

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
  if (!appointmentForm.value.sectionId) {
    ElMessage.warning('请选择预约时间段')
    return
  }

  try {
    submitting.value = true
    
    // 检查预约可用性
    const availabilityRes = await patientAPI.checkAppointmentAvailability(appointmentForm.value.sectionId)
    if (availabilityRes.code === 200 && !availabilityRes.data.is_available) {
      ElMessage.error('该时段已被预约，请重新选择')
      return
    }
    
    // 创建预约
    const res = await patientAPI.createAppointment({
      sectionId: appointmentForm.value.sectionId
    })
    
    if (res.code === 200) {
      ElMessage.success('预约成功！')
      
      // 重置表单
      currentStep.value = 0
      appointmentForm.value = {
        officeId: null,
        doctorId: null,
        sectionId: null
      }
      selectedDate.value = new Date()
      doctorSchedule.value = []
      
      // 刷新预约列表
      await loadMyAppointments()
    } else {
      ElMessage.error(res.message || '预约失败')
    }
  } catch (error) {
    console.error('预约失败:', error)
    ElMessage.error(error.message || '预约失败，请重试')
  } finally {
    submitting.value = false
  }
}

const cancelAppointment = async (appointmentId) => {
  try {
    await ElMessageBox.confirm('确定要取消这个预约吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    cancelingAppointmentId.value = appointmentId
    const res = await patientAPI.cancelAppointment(appointmentId)
    
    if (res.code === 200) {
      ElMessage.success('已取消预约')
      await loadMyAppointments()
    } else {
      ElMessage.error(res.message || '取消预约失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消预约失败')
    }
  } finally {
    cancelingAppointmentId.value = null
  }
}

const viewAppointmentDetail = (appointment) => {
  ElMessage.info(`查看预约详情: ${appointment.doctor_name} - ${appointment.date}`)
  // 这里可以打开详情对话框或跳转到详情页面
}

const getAppointmentStatusText = (state) => {
  const statusMap = {
    1: '待就诊',
    2: '已完成', 
    3: '已取消',
    4: '已过期'
  }
  return statusMap[state] || '未知状态'
}

const getAppointmentStatusType = (state) => {
  const typeMap = {
    1: 'warning',
    2: 'success',
    3: 'info',
    4: 'danger'
  }
  return typeMap[state] || 'info'
}

const getAppointmentColor = (state) => {
  const colorMap = {
    1: '#409EFF', // 蓝色 - 待就诊
    2: '#67C23A', // 绿色 - 已完成
    3: '#909399', // 灰色 - 已取消
    4: '#F56C6C'  // 红色 - 已过期
  }
  return colorMap[state] || '#409EFF'
}

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000 // 禁用今天之前的日期
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  const routeMap = {
    'overview': '/patient',
    'appointment': '/patient/appointment', 
    'records': '/patient/records'
  }
  
  if (routeMap[index]) {
    router.push(routeMap[index])
  } else {
    ElMessage.info(`功能开发中: ${index}`)
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
.selected-card {
  border: 2px solid #409EFF;
  background: #ecf5ff;
}

.time-slots-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.time-slot {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  position: relative;
}

.time-slot:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.time-slot.selected {
  border-color: #409EFF;
  background: #ecf5ff;
}

.time-range {
  font-weight: bold;
  margin-bottom: 4px;
}

.slot-info {
  font-size: 12px;
  color: #909399;
}

.slot-full {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #f56c6c;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
}

:deep(.desc-label) {
  width: 100px;
}
</style>