import { createRouter, createWebHistory } from "vue-router"
import { useUserStore } from "@/store/user"

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
    meta: { title: "登录" },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/Register.vue"),
    meta: { title: "注册" },
  },
  {
    path: "/patient",
    name: "Patient",
    component: () => import("@/views/Patient/PatientHome.vue"),
    meta: { title: "患者端", requiresAuth: true, role: "patient" },
  },
  {
    path: "/patient/appointment",
    name: "PatientAppointment",
    component: () => import("@/views/Patient/PatientAppointment.vue"),
    meta: { title: "预约挂号", requiresAuth: true, role: "patient" },
  },
  {
    path: "/patient/records",
    name: "PatientRecords",
    component: () => import("@/views/Patient/PatientRecords.vue"),
    meta: { title: "就诊记录", requiresAuth: true, role: "patient" },
  },
  {
    path: "/doctor",
    name: "Doctor",
    component: () => import("@/views/Doctor/DoctorHome.vue"),
    meta: { title: "医生端", requiresAuth: true, role: "doctor" },
  },
  {
    path: "/pharmacy",
    name: "Pharmacy",
    component: () => import("@/views/Pharmacy/PharmacyHome.vue"),
    meta: { title: "药房端", requiresAuth: true, role: "pharmacy" },
  },
  {
    path: "/admin",
    name: "Admin",
    component: () => import("@/views/Admin/AdminHome.vue"),
    meta: { title: "管理端", requiresAuth: true, role: "admin" },
  },
  {
    path: "/admin/schedule",
    name: "AdminSchedule",
    component: () => import("@/views/Admin/AdminSchedule.vue"),
    meta: { title: "医生排班", requiresAuth: true, role: "admin" },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next("/login")
  } else if (to.meta.role && userStore.userRole !== to.meta.role) {
    next("/login")
  } else {
    document.title = to.meta.title || "智慧医疗管理系统"
    next()
  }
})

export default router
