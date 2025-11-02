import axios from "axios"
import { ElMessage } from "element-plus"
import { useUserStore } from "@/store/user"

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || "请求失败")
      return Promise.reject(new Error(res.message || "请求失败"))
    }
    return res
  },
  (error) => {
    ElMessage.error(error.message || "网络错误")
    return Promise.reject(error)
  },
)

// API接口
export const authAPI = {
  login: (data) => request.post("/auth/login", data),
  logout: () => request.post("/auth/logout"),
  register: (data) => request.post("/auth/account/create", data),
  getProfile: () => request.get("/auth/profile"),
  changePassword: (data) => request.post("/auth/change-password", data),
}

export const patientAPI = {
  // 预约相关
  getAppointments: () => request.get("/patient/appointments"),
  createAppointment: (data) => request.post("/patient/appointments", data),
  cancelAppointment: (id) => request.delete(`/patient/appointments/${id}`),

  // 科室和医生
  getOffices: () => request.get("/patient/offices"),
  getDoctorsByOffice: (officeId) => request.get(`/patient/doctors/by-office/${officeId}`),

  // 排班查询
  getDoctorSchedule: (params) => request.get("/patient/schedule/doctor", { params }),
  getOfficeSchedule: (params) => request.get("/patient/schedule/office", { params }),

  // 挂号相关
  register: (data) => request.post("/patient/registration/register", data),
  getRegistrationHistory: () => request.get("/patient/registration/history"),
  getRegistrationDetails: (params) => request.get("/patient/registration/details", { params }),
  checkAppointmentAvailability: (sectionId) =>
    request.get(`/patient/registration/appointment-availability/${sectionId}`),

  // 其他
  getProfile: () => request.get("/patient/profile"),
  getReports: () => request.get("/patient/reports"),
  getReminders: () => request.get("/patient/reminders"),
}

export const doctorAPI = {
  getTodayPatients: () => request.get("/doctor/patients/today"),
  getStatistics: () => request.get("/doctor/statistics"),
  getAIDiagnose: (patientId) => request.get(`/doctor/ai-diagnose/${patientId}`),
  createPrescription: (data) => request.post("/doctor/prescriptions", data),
}

export const pharmacyAPI = {
  getPrescriptions: (params) => request.get("/pharmacy/prescriptions", { params }),
  dispensePrescription: (id) => request.post(`/pharmacy/prescriptions/${id}/dispense`),
  getInventoryAlerts: () => request.get("/pharmacy/inventory/alerts"),
  getStatistics: () => request.get("/pharmacy/statistics"),
}

export const adminAPI = {
  // 排班管理
  generateSchedules: (data) => request.post("/admin/schedules/generate", data),
  saveSchedules: (data) => request.post("/admin/schedules/save", data),
  generateAndSaveSchedules: (data) => request.post("/admin/schedules/generate-and-save", data),
  clearSchedules: (data) => request.post("/admin/schedules/clear", data),
  previewSchedules: (params) => request.get("/admin/schedules/preview", { params }),

  // 统计数据
  getStatistics: () => request.get("/admin/statistics"),
  getOutpatientTrend: (params) => request.get("/admin/statistics/outpatient-trend", { params }),
  getDepartmentDistribution: () => request.get("/admin/statistics/department-distribution"),

  // 其他
  getDepartments: () => request.get("/admin/departments"),
  getNotifications: () => request.get("/admin/notifications"),
}

export default request
