<script setup lang="ts">
import { ref } from 'vue'
import { tryOnMounted } from '@vueuse/core'

import { useAgentStore } from '@/stores/agent'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import DataTable from '@/components/DataTable.vue'
import type { components } from '@/api'

type Agent = components['schemas']['Agent']

const agentStore = useAgentStore()
const { agents, currentAgent, getAgent } = storeToRefs(agentStore)

const router = useRouter()
const loading = ref(false)

const columns = [
  {
    key: 'name',
    label: 'Agent name',
    sortable: true,
  },
  {
    key: 'state',
    label: 'State',
    sortable: true,
  },
  {
    key: 'agent_type',
    label: 'Agent type',
    sortable: false,
  },
  {
    key: 'agent_model',
    label: 'Agent LLM',
    sortable: false,
  },
  // Not sure if we want to include the system prompt.
  {
    key: 'system_prompt.content',
    label: 'System prompt',
    sortable: false,
  },
]

const submitted = ref(false)
const submitHandler = async () => {
  // Let's pretend this is an ajax request:
  await new Promise((r) => setTimeout(r, 1000))
  submitted.value = true
}
tryOnMounted(async () => {
  await agentStore.fetchAgents()
  loading.value = false
})

const handleRowClick = (agent: Agent) => {
  router.push(`/agents/${agent.id}`)
}

const createNewAgent = () => {
  router.push('/agents/new')
}

const handleSelectionChange = (selectedItems) => {
  console.log('Selected items:', selectedItems)
}
</script>
<template>
  <div>
    <div class="mb-6 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-white">Agents</h1>
      <button
        @click="createNewAgent"
        class="bg-indigo-600 text-white px-4 py-2 rounded-md font-medium hover:bg-indigo-700 transition cursor-pointer"
      >
        New Agent
      </button>
    </div>
    <DataTable
      :columns="columns"
      :items="agents"
      :loading="loading"
      :actions="actions"
      :items-per-page="5"
      bg-color="bg-gray-900"
      selectable
      searchable
      pagination
      striped
      empty-text="No agents found. Create a new agent to get started."
      @row-click="handleRowClick"
      @selection-change="handleSelectionChange"
    />
  </div>
</template>
