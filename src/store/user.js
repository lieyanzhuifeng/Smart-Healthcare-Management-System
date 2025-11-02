import { defineStore } from "pinia"
import { ref, computed } from "vue"

export const useUserStore = defineStore("user", () => {
  const userInfo = ref(null)
  const token = ref(localStorage.getItem("token") || "")

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => userInfo.value?.role || "")
  const userName = computed(() => userInfo.value?.name || "")

  function login(user, userToken) {
    userInfo.value = user
    token.value = userToken
    localStorage.setItem("token", userToken)
    localStorage.setItem("userInfo", JSON.stringify(user))
  }

  function logout() {
    userInfo.value = null
    token.value = ""
    localStorage.removeItem("token")
    localStorage.removeItem("userInfo")
  }

  function initUser() {
    const savedUser = localStorage.getItem("userInfo")
    if (savedUser) {
      userInfo.value = JSON.parse(savedUser)
    }
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    userRole,
    userName,
    login,
    logout,
    initUser,
  }
})
