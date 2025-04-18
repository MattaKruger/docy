<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const recentProjects = ref([
  { id: 1, name: 'Annual Report Analysis', date: '2023-11-15', progress: 75 },
  { id: 2, name: 'Market Research Summary', date: '2023-11-10', progress: 90 },
  { id: 3, name: 'Technical Documentation', date: '2023-11-05', progress: 60 },
])

const activeAgents = ref([
  { id: 1, name: 'Data Extractor', status: 'Running', documents: 247 },
  { id: 2, name: 'Summarizer', status: 'Idle', documents: 125 },
  { id: 3, name: 'FAQ Generator', status: 'Running', documents: 89 },
])
const stats = ref([
  { label: 'Total Documents', value: '1,234', icon: '📄' },
  { label: 'Projects', value: '12', icon: '📁' },
  { label: 'Active Agents', value: '5', icon: '🤖' },
])
</script>

<template>
  <!-- Welcome Banner -->
  <section
    class="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-6 mb-8 text-white"
  >

    <h1 class="text-3xl font-bold mb-2">Welcome to Docy</h1>
    <p class="mb-4 max-w-2xl">
      Your intelligent document management system. Organize, analyze, and extract insights from your
      documents with ease.
    </p>
    <div class="flex space-x-4 mt-4">
      <button
        class="bg-white text-indigo-600 px-4 py-2 rounded-md font-medium hover:bg-opacity-90 transition"
        @click="router.push('/projects/new')"
      >
        New Project
      </button>
      <button
        class="bg-indigo-700 text-white px-4 py-2 rounded-md font-medium hover:bg-indigo-800 transition border border-indigo-400"
        @click="router.push('/documents/upload')"
      >
        Upload Documents
      </button>
    </div>
  </section>
  <div box-="square">
    <h1>Hi Mom</h1>
  </div>
  <!-- Stats Overview -->
  <section class="mb-8">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        v-for="(stat, index) in stats"
        :key="index"
        class="bg-white rounded-lg shadow p-6 flex items-center"
      >
        <div class="text-3xl mr-4 bg-indigo-100 p-3 rounded-full text-indigo-600">
          {{ stat.icon }}
        </div>
        <div>
          <div class="text-2xl font-bold text-gray-800">{{ stat.value }}</div>
          <div class="text-gray-500">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Main Content Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Recent Projects -->
    <section class="lg:col-span-2 bg-white rounded-lg shadow">
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-800">Recent Projects</h2>
        <button class="text-indigo-600 hover:text-indigo-800" @click="router.push('/projects')">
          View All
        </button>
      </div>
      <div class="p-4">
        <div v-if="recentProjects.length" class="space-y-4">
          <div
            v-for="project in recentProjects"
            :key="project.id"
            class="border-b border-gray-100 pb-4 last:border-0 last:pb-0"
          >
            <div class="flex justify-between items-center mb-2">
              <h3 class="font-medium">{{ project.name }}</h3>
              <span class="text-sm text-gray-500">{{ project.date }}</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-indigo-600 h-2 rounded-full"
                :style="`width: ${project.progress}%`"
              ></div>
            </div>
            <div class="text-right mt-1 text-sm text-gray-600">
              {{ project.progress }}% Complete
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          No recent projects found. Start by creating a new project.
        </div>
      </div>
    </section>

    <!-- Active Agents -->
    <section class="bg-white rounded-lg shadow">
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h2 class="text-xl font-semibold text-gray-800">Active Agents</h2>
        <button class="text-indigo-600 hover:text-indigo-800" @click="router.push('/agents')">
          Manage
        </button>
      </div>
      <div class="p-4">
        <div v-if="activeAgents.length" class="space-y-4">
          <div
            v-for="agent in activeAgents"
            :key="agent.id"
            class="border-b border-gray-100 pb-4 last:border-0 last:pb-0"
          >
            <div class="flex justify-between items-center">
              <h3 class="font-medium">{{ agent.name }}</h3>
              <span
                class="px-2 py-1 text-xs rounded-full"
                :class="
                  agent.status === 'Running'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                "
              >
                {{ agent.status }}
              </span>
            </div>
            <div class="text-sm text-gray-500 mt-1">{{ agent.documents }} documents processed</div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          No active agents. Configure agents to automate your workflow.
        </div>
      </div>
    </section>
  </div>

  <!-- Quick Actions -->
  <section class="mt-8 bg-white rounded-lg shadow">
    <div class="p-4 border-b border-gray-200">
      <h2 class="text-xl font-semibold text-gray-800">Quick Actions</h2>
    </div>
    <div class="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
      <button
        class="p-4 border border-gray-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-200 transition text-center"
        @click="router.push('/documents/upload')"
      >
        <div class="text-2xl mb-2">📄</div>
        <div class="font-medium">Upload Document</div>
      </button>
      <button
        class="p-4 border border-gray-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-200 transition text-center"
        @click="router.push('/projects/new')"
      >
        <div class="text-2xl mb-2">📁</div>
        <div class="font-medium">New Project</div>
      </button>
      <button
        class="p-4 border border-gray-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-200 transition text-center"
        @click="router.push('/agents/new')"
      >
        <div class="text-2xl mb-2">🤖</div>
        <div class="font-medium">Create Agent</div>
      </button>
      <button
        class="p-4 border border-gray-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-200 transition text-center"
        @click="router.push('/search')"
      >
        <div class="text-2xl mb-2">🔍</div>
        <div class="font-medium">Search Documents</div>
      </button>
    </div>
  </section>
</template>
