import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // state
  const loading = ref(false)
  const title = ref('HoloOrb')

  // getters
  const isLoading = computed(() => loading.value)
  const appTitle = computed(() => title.value)

  // actions
  function setLoading(val) {
    loading.value = val
  }

  function setTitle(val) {
    title.value = val
    document.title = val
  }

  return {
    loading,
    title,
    isLoading,
    appTitle,
    setLoading,
    setTitle
  }
})
