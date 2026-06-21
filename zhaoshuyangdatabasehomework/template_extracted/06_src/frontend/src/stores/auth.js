import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user  = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  function setAuth(accessToken, userInfo) {
    token.value = accessToken
    user.value  = userInfo
    localStorage.setItem('token', accessToken)
    localStorage.setItem('user', JSON.stringify(userInfo))
  }

  function clearAuth() {
    token.value = ''
    user.value  = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isLoggedIn, setAuth, clearAuth }
})
