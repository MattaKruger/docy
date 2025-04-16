<script setup lang="ts">
import { ref } from 'vue'
import { tryOnMounted } from '@vueuse/core'

import { useProjectStore } from '@/stores/project'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

import DataTable from '@/components/DataTable.vue'

import type { components } from '@/api'

type Project = components['schemas']['Project']

const router = useRouter()
const loading = ref(true)

const projectStore = useProjectStore()

// TODO figure a way out to dynamically generate columns based on 'schemas[TYPE]' fields.
// Prob not that hard.
const columns = [
  {
    key: 'name',
    label: 'Project name',
    sortable: true,
  },
  {
    key: 'project_type',
    label: 'Project type',
    sortable: true,
  },
  {
    key: 'description',
    label: 'Description',
    sortable: true,
  },
  {
    key: 'framework',
    label: 'Framework',
    sortable: true,
  },
]

const actions = [
  {
    label: 'View',
    icon: '👁️',
    variant: 'default',
    handler: (project: Project) => {
      router.push(`/projects/${project.id}`)
    },
  },
  {
    label: 'Edit',
    icon: '✏️',
    variant: 'primary',
    handler: (project: Project) => {
      router.push(`/projects/${project.id}/edit`)
    },
  },
  {
    label: 'Delete',
    icon: '🗑️',
    variant: 'danger',
    handler: (project: Project) => {
      if (confirm(`Are you sure you want to delete "${project.name}"?`)) {
        deleteProject(project.id)
      }
    },
  },
]

tryOnMounted(async () => {
  await projectStore.fetchProjects()
  loading.value = false
})

const { projects } = storeToRefs(projectStore)

const handleRowClick = (project: Project) => {
  router.push(`/projects/${project.id}`)
}

const createNewProject = () => {
  router.push('/projects/new')
}

// Handle project deletion
const deleteProject = (id: number) => {
  projects.value = projects.value.filter((p) => p.id !== id)
}

const handleSelectionChange = (selectedItems) => {
  console.log('Selected items:', selectedItems)
}
</script>

<template>
  <div>
    <!-- <Tabs /> -->
    <div class="mb-6 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-white">Projects</h1>
      <button
        @click="createNewProject"
        class="bg-indigo-600 text-white px-4 py-2 rounded-md font-medium hover:bg-indigo-700 transition cursor-pointer"
      >
        New Project
      </button>
    </div>

    <DataTable
      :columns="columns"
      :items="projects"
      :loading="loading"
      :actions="actions"
      :items-per-page="5"
      bg-color="bg-gray-900"
      selectable
      searchable
      pagination
      striped
      empty-text="No projects found. Create a new project to get started."
      @row-click="handleRowClick"
      @selection-change="handleSelectionChange"
    >
      <template #toolbar>
        <button
          class="bg-gray-200 text-gray-700 px-3 py-1 rounded-md text-sm hover:bg-gray-300 transition ml-2"
        >
          Export
        </button>
      </template>
    </DataTable>
  </div>
</template>
