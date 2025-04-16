<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Navigation',
  },
  items: {
    type: Array,
    default: () => [],
  },
  isOpen: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['toggle', 'item-click'])

const sidebarOpen = ref(props.isOpen)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
  emit('toggle', sidebarOpen.value)
}

const handleItemClick = (item) => {
  emit('item-click', item)
}

const sidebarWidthClass = computed(() => (sidebarOpen.value ? 'w-64' : 'w-16'))
</script>

<template>
  <div
    :class="[
      'h-full flex flex-col bg-gray-100 shadow-md transition-all duration-300 ease-in-out',
      sidebarWidthClass,
    ]"
  >
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
      <h2 class="text-lg font-medium truncate" v-show="sidebarOpen">{{ title }}</h2>
      <button
        class="text-gray-600 hover:text-gray-900 focus:outline-none p-1"
        @click="toggleSidebar"
      >
        <span class="text-xl">{{ sidebarOpen ? '×' : '☰' }}</span>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <ul class="py-2">
        <li
          v-for="(item, index) in items"
          :key="index"
          class="cursor-pointer"
          @click="handleItemClick(item)"
        >
          <div class="flex items-center px-4 py-2 hover:bg-gray-200 transition-colors duration-200">
            <span
              v-if="item.icon"
              class="text-lg mr-3 flex-shrink-0"
              :class="{ 'mx-auto': !sidebarOpen }"
            >
              {{ item.icon }}
            </span>
            <span v-if="sidebarOpen" class="truncate">{{ item.text }}</span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
