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
}

export const patientAPI = {
  getAppointments: () => request.get("/patient/appointments"),
  createAppointment: (data) => request.post("/patient/appointments", data),
  getReports: () => request.get("/patient/reports"),
  getHealthRecords: () => request.get("/patient/health-records"),
}

export const doctorAPI = {
  getPatients: () => request.get("/doctor/patients"),
  getSchedule: () => request.get("/doctor/schedule"),
  createPrescription: (data) => request.post("/doctor/prescriptions", data),
  getMedicalRecords: (patientId) => request.get(`/doctor/medical-records/${patientId}`),
}

export const pharmacyAPI = {
  getPrescriptions: () => request.get("/pharmacy/prescriptions"),
  getInventory: () => request.get("/pharmacy/inventory"),
  updateInventory: (data) => request.put("/pharmacy/inventory", data),
  dispenseMedicine: (id) => request.post(`/pharmacy/prescriptions/${id}/dispense`),
}

export const adminAPI = {
  getStatistics: () => request.get("/admin/statistics"),
  getDepartments: () => request.get("/admin/departments"),
  getFinancialReport: () => request.get("/admin/financial-report"),
  getStaffList: () => request.get("/admin/staff"),
}

export default request
