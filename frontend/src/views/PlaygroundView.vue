<script setup lang="ts">
import { ref } from 'vue'
import ProjectCard from '@/components/projects/ProjectCard.vue'
</script>

<template>
  <!-- Main Container -->
  <div class="min-h-screen bg-gray-100 p-4 sm:p-6 lg:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Playground Title -->
      <h1 class="text-3xl font-bold text-gray-800 mb-8 border-b pb-2 border-gray-300">
        Component Playground
      </h1>

      <!-- Responsive Grid for Sections -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Section 1: Core Components -->
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 class="text-xl font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-200">
            Core Components
          </h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">ProjectCard</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- ProjectCard will go here -->
                ProjectCard Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">TaskItem (List)</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- TaskItem (list style) will go here -->
                TaskItem (List) Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">TaskItem (Board)</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- TaskItem (board style) will go here -->
                TaskItem (Board) Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">AgentAvatar</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm flex items-center justify-center space-x-2"
              >
                <!-- AgentAvatar will go here -->
                <span class="inline-block h-8 w-8 rounded-full bg-gray-300"></span>
                <span>AgentAvatar Placeholder</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 2: Container & Layout Components -->
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 class="text-xl font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-200">
            Containers & Layouts
          </h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">TaskList</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- TaskList will go here -->
                TaskList Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">ProjectGrid / ProjectList</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- ProjectGrid / ProjectList will go here -->
                ProjectGrid/List Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">KanbanBoard</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- KanbanBoard will go here -->
                KanbanBoard Placeholder
                <p class="text-xs mt-1">(Internally uses KanbanColumn & TaskItem)</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 3: Interaction & Form Components -->
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 class="text-xl font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-200">
            Interaction & Forms
          </h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">TaskCreatorForm (in Modal)</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- Trigger for ModalWrapper > TaskCreatorForm -->
                <button class="bg-blue-500 text-white text-xs py-1 px-2 rounded hover:bg-blue-600">
                  Show Form
                </button>
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">AgentSelector</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- AgentSelector will go here -->
                AgentSelector Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">DatePicker</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- DatePicker will go here -->
                DatePicker Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">StatusDropdown</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- StatusDropdown will go here -->
                StatusDropdown Placeholder
              </div>
            </div>
          </div>
        </div>

        <!-- Section 4: UI Primitives & Utility -->
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
          <h2 class="text-xl font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-200">
            UI Primitives & Utility
          </h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">BaseButton</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-gray-400 text-sm space-x-2 flex flex-wrap gap-y-2"
              >
                <!-- BaseButton examples -->
                <button class="bg-blue-500 text-white text-xs py-1 px-2 rounded hover:bg-blue-600">
                  Primary
                </button>
                <button
                  class="bg-gray-200 text-gray-700 text-xs py-1 px-2 rounded hover:bg-gray-300"
                >
                  Secondary
                </button>
                <button class="bg-red-500 text-white text-xs py-1 px-2 rounded hover:bg-red-600">
                  Danger
                </button>
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">BaseInput</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- BaseInput will go here -->
                BaseInput Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">LoadingIndicator</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- LoadingIndicator will go here -->
                LoadingIndicator Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">EmptyState</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- EmptyState will go here -->
                EmptyState Placeholder
              </div>
            </div>
            <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">NotificationToast</h3>
              <div
                class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm"
              >
                <!-- NotificationToast trigger/example -->
                NotificationToast Placeholder
              </div>
            </div>
          </div>
        </div>

        <!-- Add more sections as needed -->
        <!-- Example: Detail Views Section -->
        <!--
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200 md:col-span-2 lg:col-span-1"> // Example spanning
          <h2 class="text-xl font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-200">
            Detail Views
          </h2>
          <div class="space-y-4">
             <div>
              <h3 class="text-sm font-medium text-gray-500 mb-1">TaskDetailView</h3>
              <div class="border border-dashed border-gray-300 p-4 rounded text-center text-gray-400 text-sm">
                TaskDetailView Placeholder (maybe trigger a modal)
              </div>
            </div>
          </div>
        </div>
        -->
      </div>
      <!-- End Responsive Grid -->
    </div>
    <!-- End Max Width Container -->
  </div>
  <!-- End Main Container -->
</template>
