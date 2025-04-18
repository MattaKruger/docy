<script setup lang="ts">
import { useQuery } from '@pinia/colada';
import { getFilesApiV1FilesGet, GetProjectsApiV1ProjectsGetData } from '@/client';

import { ref, computed } from 'vue'
import { tryOnMounted } from '@vueuse/core'
import { useRouter } from 'vue-router'

import ProjectCombobox from '@/components/ProjectCombobox.vue';

import type { components } from '@/api'

type FileInfo = components['schemas']['FileInfo']
type Project = components['schemas']['Project']

const router = useRouter()

const {
  state: files,
  asyncStatus,
  isLoading,
  refresh,
  refetch
} = useQuery({
  key: ["files"],
  query: async () =>
})




const query = ref('')
const filteredProjects = computed(() =>
  query.value === ''
    ? projects.value
    : projects.value.filter((project) =>
        project.name.toLowerCase().includes(query.value.toLowerCase()),
      ),
)

tryOnMounted(async () => {
  await projectStore.fetchProjects()
  await fileStore.fetchFiles()
  loading.value = false
})
</script>
<template>
  <div>
    <div class="mb-6 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-white">
        <!-- Project combobox -->
        <ProjectCombobox />
        <!-- <Combobox v-model="selectedProject">
          <ComboboxInput @change="query = $event.target.value" />
          <ComboboxOptions>
            <ComboboxOption v-for="project in filteredProjects" :key="project.id" :value="project">
              {{ project.name }}
            </ComboboxOption>
          </ComboboxOptions>
        </Combobox> -->
      </h1>
    </div>
  </div>
</template>
