import { ref } from 'vue'
import { defineStore } from 'pinia'
import { client } from './client'
import type { components } from '../api'

export const useFileStore = defineStore('file', () => {
  const files = ref<components['schemas']['FileInfo'][]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchFiles() {
    loading.value = true
    error.value = null
    try {
      const { data, error: apiError } = await client.GET('/api/v1/files/')
      if (apiError) {
        throw new Error(apiError.message || 'Failed to fetch projects')
      }
      files.value = data || []
    } catch (error) {
      error.value = error.message
    } finally {
      loading.value = false
    }
  }

  return { files, fetchFiles, loading, error }
})
