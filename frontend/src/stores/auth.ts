import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '../types'
import * as authApi from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  function restoreSession() {
    accessToken.value = localStorage.getItem('access_token')
    refreshToken.value = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        user.value = null
      }
    }
  }

  async function login(username: string, password: string) {
    const res = await authApi.login(username, password)
    setAuth(res.user, res.access_token, res.refresh_token)
  }

  async function register(username: string, email: string, password: string) {
    const res = await authApi.register(username, email, password)
    setAuth(res.user, res.access_token, res.refresh_token)
  }

  function setAuth(u: User, access: string, refresh: string) {
    user.value = u
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('user', JSON.stringify(u))
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.clear()
  }

  return { user, accessToken, refreshToken, isAuthenticated, restoreSession, login, register, logout }
})
