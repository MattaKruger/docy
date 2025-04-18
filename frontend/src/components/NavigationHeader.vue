<script setup lang="ts">
import { ref, computed } from 'vue'


interface Item {
  text: string;
  icon: string;
}

interface HeaderLink {
  text: string;
  href: string
}

const props = defineProps<{
  siteTitle?: string
  title?: string
  items?: Array<Item>
  isOpen?: boolean
  headerLinks?: Array<HeaderLink>
}>();

const emit = defineEmits(['toggle', 'item-click', 'header-link-click'])

const sidebarOpen = ref(props.isOpen)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
  emit('toggle', sidebarOpen.value)
}

const handleItemClick = (item: Item) => {
  emit('item-click', item)
}

const handleHeaderLinkClick = (link: HeaderLink) => {
  emit('header-link-click', link)
}

const sidebarWidthClass = computed(() => (sidebarOpen.value ? 'w-64' : 'w-16'))
</script>

<template>
  <div class="flex flex-col h-screen">
    <!-- Header Component -->
    <header class="bg-zinc-950 text-white shadow-md z-10">
      <div
        class="container mx-auto px-4 py-4 flex flex-col md:flex-row items-center justify-between"
      >
        <div class="flex items-center mb-4 md:mb-0">
          <button class="text-white mr-3 focus:outline-none" @click="toggleSidebar">
            <span class="text-xl">{{ sidebarOpen ? '×' : '☰' }}</span>
          </button>
          <h1 class="text-xl font-bold">{{ siteTitle }}</h1>
        </div>
        <nav>
          <ul class="flex flex-wrap space-x-1 md:space-x-6">
            <li
              v-for="(link, index) in headerLinks"
              :key="index"
              @click="handleHeaderLinkClick(link)"
            >
              <a :href="link.href" class="cursor-pointer px-3 py-2 hover:bg-indigo-700 rounded-md transition">
                {{ link.text }}
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>

    <!-- Main Content Area with Sidebar -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Component -->
      <div
        :class="[
          'flex flex-col bg-zinc-950 text-white shadow-md transition-all duration-300 ease-in-out',
          sidebarWidthClass,
        ]"
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-indigo-500">
          <h2 class="text-lg font-medium truncate" v-show="sidebarOpen">{{ title }}</h2>
        </div>

        <div class="flex-1 overflow-y-auto">
          <ul class="py-2">
            <li
              v-for="(item, index) in items"
              :key="index"
              class="cursor-pointer"
              @click="handleItemClick(item)"
            >
              <div
                class="flex items-center px-4 py-2 hover:bg-indigo-700 transition-colors duration-200"
              >
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

      <!-- Content Area -->
      <div class="flex-1 overflow-auto p-6">
        <slot></slot>
      </div>
    </div>
  </div>
</template>
