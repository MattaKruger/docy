<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import NavigationHeader from '@/components/NavigationHeader.vue'

const router = useRouter()

type NavigationItem = {
  icon: string
  text: string
  route: string
}

const navigationItems = ref<NavigationItem[]>([
  { icon: '', text: 'Home', route: '/' },
  { icon: '', text: 'Dashboard', route: '/dashboard' },
  { icon: '', text: 'Projects', route: '/projects' },
  { icon: '', text: 'Agents', route: '/agents' },
  { icon: '', text: 'Files', route: '/files' },
  { icon: '', text: 'Playground', route: '/playground' },
  { icon: '⚙️', text: 'Settings', route: '/settings' },
])

const headerLinks = ref([
  { text: 'Home', route: '/' },
  { text: 'Projects', route: '/projects' },
  { text: 'Agents', route: '/agents' },
  { text: 'Files', route: '/documents' },
])

const sidebarOpen = ref(true)

const handleToggle = (isOpen: boolean) => {
  sidebarOpen.value = isOpen
}

const handleItemClick = (item: NavigationItem) => {
  router.push(item.route)
}

const handleHeaderLinkClick = (link) => {
  if (link.href && link.href !== '#') {
    window.location.href = link.href
  } else if (link.route) {
    router.push(link.route)
  }
}
</script>

<template>
  <div class="bg-zinc-950">
    <NavigationHeader
      siteTitle="Docy"
      title="Menu"
      :items="navigationItems"
      :isOpen="sidebarOpen"
      :headerLinks="headerLinks"
      @toggle="handleToggle"
      @item-click="handleItemClick"
      @header-link-click="handleHeaderLinkClick"
    >
      <div class="flex-grow container mx-auto px-4 py-6">
        <router-view></router-view>
      </div>
    </NavigationHeader>
  </div>
</template>
