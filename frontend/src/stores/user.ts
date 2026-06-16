import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userId = ref<string>(localStorage.getItem('user_id') || 'default')

  function login(id: string) {
    userId.value = id
    localStorage.setItem('user_id', id)
  }
  function logout() {
    localStorage.removeItem('user_id')
    userId.value = 'default'
  }
  return { userId, login, logout }
})
