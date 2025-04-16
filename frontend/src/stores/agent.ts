import { ref } from 'vue'
import { defineStore } from 'pinia'
import { client } from './client'
import type { components } from '../api'

export const useAgentStore = defineStore('agent', () => {
  const agents = ref<components['schemas']['Agent'][]>([])
  const currentAgent = ref<components['schemas']['Agent'] | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAgents(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const { data, error: apiError } = await client.GET('/api/v1/agents/')

      if (apiError) {
        throw new Error(apiError.message || 'Failed to fetch projects')
      }
      agents.value = data || []
    } catch (err) {
      console.error('Error fetching projects:', err)
      error.value = err instanceof Error ? err.message : 'Unkown error occured'
    } finally {
      loading.value = false
    }
  }

  async function getAgent(agentId: number): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const { data, error: apiError } = await client.GET(`/api/v1/agents/${agentId}`, {
        params: {
          agent_id: agentId,
        },
      })
    } catch (err) {
      console.error(`Error fetching agent ${agentId}:`, err)
      error.value = err instanceof Error ? err.message : 'Unkown error occured'
    } finally {
      loading.value = false
    }
  }

  return {
    agents,
    currentAgent,
    fetchAgents,
    getAgent,
  }
})
