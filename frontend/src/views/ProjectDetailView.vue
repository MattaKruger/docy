<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'

const activeTab = ref('details')

const tabs = [
  { id: 'details', label: 'Details' },
  { id: 'agents', label: 'Agents' },
  { id: 'tasks', label: 'Tasks' },
  { id: 'files', label: 'Files' },
]

const setActiveTab = (tabId) => {
  activeTab.value = tabId
}

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const project = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const projectId = parseInt(route.params.id as string)
    project.value = await projectStore.getProject(projectId)
    loading.value = false
  } catch (e) {
    error.value = 'Failed to load project details'
  } finally {
    loading.value = false
  }
})

const goBack = () => {
  router.push('/projects')
}

const editProject = () => {
  router.push(`/projects/${route.params.id}/edit`)
}

const deleteProject = () => {
  if (confirm(`Are you sure you want to delete "${project.value.name}"?`)) {
    try {
      // await projectStore.deleteProject(project.value.id);
      // router.push("/projects");
    } catch (e) {
      error.value = 'Failed to delete project'
      return e
    }
  }
}
</script>
<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header with back button -->
    <div class="mb-6 flex justify-between items-center">
      <div class="flex items-center">
        <button @click="goBack" class="mr-4 text-indigo-500 hover:text-indigo-600">← Back</button>
        <h1 class="text-2xl font-bold text-white">Project Details</h1>
      </div>
      <div class="flex space-x-3">
        <button
          @click="editProject"
          class="bg-indigo-600 text-white px-4 py-2 rounded-md font-medium hover:bg-indigo-700 transition"
        >
          Edit Project
        </button>
        <button
          @click="deleteProject"
          class="bg-red-600 text-white px-4 py-2 rounded-md font-medium hover:bg-red-700 transition"
        >
          Delete
        </button>
      </div>
    </div>
    <div class="mb-6">
      <div class="border-b border-gray-700">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="setActiveTab(tab.id)"
            :class="[
              'py-2 px-4 text-center border-b-2 font-medium text-sm',
              activeTab === tab.id
                ? 'border-indigo-500 text-indigo-500'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-400',
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab content -->
      <div class="mt-4">
        <div v-show="activeTab === 'details'">
          <!-- Project details content -->
        </div>
        <div v-show="activeTab === 'files'">
          <!-- Files content -->
        </div>
        <div v-show="activeTab === 'team'">
          <!-- Team content -->
        </div>
        <div v-show="activeTab === 'activity'">
          <!-- Activity content -->
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="bg-gray-800 rounded-lg shadow p-6 animate-pulse">
      <div class="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
      <div class="h-4 bg-gray-700 rounded w-full mb-2"></div>
      <div class="h-4 bg-gray-700 rounded w-5/6 mb-2"></div>
      <div class="h-4 bg-gray-700 rounded w-4/6 mb-6"></div>
      <div class="h-20 bg-gray-700 rounded w-full mb-4"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-lg">
      <p>{{ error }}</p>
      <button @click="goBack" class="mt-2 text-red-600 underline">Return to projects</button>
    </div>

    <!-- Project details -->
    <div v-else-if="project" class="bg-gray-800 rounded-lg shadow overflow-hidden">
      <div class="p-6">
        <h2 class="text-3xl font-bold text-white mb-2">{{ project.name }}</h2>
        <div class="flex flex-wrap gap-2 mb-4">
          <span class="inline-block bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-sm">
            {{ project.project_type }}
          </span>
          <span
            class="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm"
            v-if="project.framework"
          >
            {{ project.framework }}
          </span>
        </div>

        <div class="mb-6">
          <h3 class="text-lg font-semibold text-gray-200 mb-2">Description</h3>
          <p class="text-gray-300">{{ project.description || 'No description available' }}</p>
        </div>

        <!-- You can add more sections based on your project model -->
        <div class="mb-6" v-if="project.created_at">
          <h3 class="text-lg font-semibold text-gray-200 mb-2">Created</h3>
          <p class="text-gray-300">{{ new Date(project.created_at).toLocaleString() }}</p>
        </div>

        <!-- Files or other project resources -->
        <div class="mb-6" v-if="project.files && project.files.length">
          <h3 class="text-lg font-semibold text-gray-200 mb-2">Files</h3>
          <ul class="divide-y divide-gray-700">
            <li v-for="file in project.files" :key="file.id" class="py-2">
              <div class="flex items-center">
                <span class="mr-2">📄</span>
                <span class="text-gray-300">{{ file.name }}</span>
              </div>
            </li>
          </ul>
        </div>

        <!-- Team members or other project metadata -->
        <div class="mb-6" v-if="project.team_members && project.team_members.length">
          <h3 class="text-lg font-semibold text-gray-200 mb-2">Team</h3>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="member in project.team_members"
              :key="member.id"
              class="flex items-center bg-gray-700 px-3 py-1 rounded-full"
            >
              <span class="text-gray-300">{{ member.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="bg-gray-800 rounded-lg shadow p-6 text-center text-gray-400">
      Project not found.
    </div>
  </div>
</template>
