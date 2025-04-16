<script setup lang="ts">
import { computed, ref } from 'vue';

interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  width?: string;
  formatter?: (value: any, item: any) => string;
}

interface Action {
  label: string;
  icon?: string;
  variant?: 'default' | 'primary' | 'success' | 'danger' | 'warning' | 'info';
  handler: (item: any) => void;
}

const props = defineProps({
  columns: {
    type: Array as () => Column[],
    required: true
  },
  items: {
    type: Array as () => any[],
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  emptyText: {
    type: String,
    default: 'No data available'
  },
  sortable: {
    type: Boolean,
    default: true
  },
  searchable: {
    type: Boolean,
    default: true
  },
  pagination: {
    type: Boolean,
    default: true
  },
  itemsPerPage: {
    type: Number,
    default: 10
  },
  striped: {
    type: Boolean,
    default: false
  },
  actions: {
    type: Array as () => Action[],
    default: () => []
  },
  selectable: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['row-click', 'sort', 'selection-change']);

// Selection
const selectedRows = ref<any[]>([]);
const allSelected = computed(() => {
  return selectedRows.value.length === filteredItems.value.length && filteredItems.value.length > 0;
});

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedRows.value = [];
  } else {
    selectedRows.value = [...filteredItems.value];
  }
  emit('selection-change', selectedRows.value);
};

const isSelected = (item: any) => {
  return selectedRows.value.includes(item);
};

const toggleSelection = (item: any) => {
  const index = selectedRows.value.indexOf(item);
  if (index === -1) {
    selectedRows.value.push(item);
  } else {
    selectedRows.value.splice(index, 1);
  }
  emit('selection-change', selectedRows.value);
};

const sortBy = ref('');
const sortDesc = ref(false);

const sort = (column: Column) => {
  if (!column.sortable && !props.sortable) return;

  if (sortBy.value === column.key) {
    sortDesc.value = !sortDesc.value;
  } else {
    sortBy.value = column.key;
    sortDesc.value = false;
  }

  emit('sort', { key: sortBy.value, desc: sortDesc.value });
};

const searchQuery = ref('');

const filteredItems = computed(() => {
  let items = [...props.items];

  if (props.searchable && searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    items = items.filter(item => {
      return Object.keys(item).some(key => {
        const value = item[key];
        if (value === null || value === undefined) return false;
        return String(value).toLowerCase().includes(query);
      });
    });
  }

  if (sortBy.value) {
    items = [...items].sort((a, b) => {
      let aValue = a[sortBy.value];
      let bValue = b[sortBy.value];

      // Handle strings for case-insensitive sorting
      if (typeof aValue === 'string') aValue = aValue.toLowerCase();
      if (typeof bValue === 'string') bValue = bValue.toLowerCase();

      if (aValue < bValue) return sortDesc.value ? 1 : -1;
      if (aValue > bValue) return sortDesc.value ? -1 : 1;
      return 0;
    });
  }

  return items;
});

const currentPage = ref(1);
const paginatedItems = computed(() => {
  if (!props.pagination) return filteredItems.value;

  const start = (currentPage.value - 1) * props.itemsPerPage;
  const end = start + props.itemsPerPage;

  return filteredItems.value.slice(start, end);
});

const totalPages = computed(() => {
  return Math.ceil(filteredItems.value.length / props.itemsPerPage);
});

const goToPage = (page: number) => {
  currentPage.value = page;
};

const getCellValue = (item: any, column: Column) => {
  const value = item[column.key];
  if (column.formatter) {
    return column.formatter(value, item);
  }
  return value;
};

const handleRowClick = (item: any) => {
  emit('row-click', item);
};

const handleAction = (action: Action, item: any) => {
  action.handler(item);
};

const resetPagination = () => {
  currentPage.value = 1;
};
</script>

<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <!-- Table Toolbar -->
    <div class="p-4 border-b border-gray-200 flex flex-wrap justify-between items-center">
      <div v-if="searchable" class="w-full md:w-auto mb-4 md:mb-0">
        <div class="relative">
          <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500">
            🔍
          </span>
          <input
            type="text"
            v-model="searchQuery"
            @input="resetPagination"
            placeholder="Search..."
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full md:w-64 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </div>
      <div class="flex items-center">
        <slot name="toolbar"></slot>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <!-- Selection column -->
            <th
              v-if="selectable"
              scope="col"
              class="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-10"
            >
              <input
                type="checkbox"
                :checked="allSelected"
                @change="toggleSelectAll"
                class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
            </th>

            <!-- Data columns -->
            <th
              v-for="column in columns"
              :key="column.key"
              scope="col"
              :class="[
                'py-3 px-4 text-xs font-medium text-gray-500 uppercase tracking-wider',
                column.align ? `text-${column.align}` : 'text-left',
                column.width ? column.width : '',
                (column.sortable || sortable) ? 'cursor-pointer hover:bg-gray-100' : ''
              ]"
              @click="sort(column)"
            >
              <div class="flex items-center space-x-1">
                <span>{{ column.label }}</span>
                <span v-if="sortBy === column.key" class="ml-1">
                  {{ sortDesc ? '▼' : '▲' }}
                </span>
              </div>
            </th>

            <!-- Actions column -->
            <th
              v-if="actions.length > 0"
              scope="col"
              class="py-3 px-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Actions
            </th>
          </tr>
        </thead>

        <tbody
          class="bg-white divide-y divide-gray-200"
          :class="{ 'animate-pulse': loading }"
        >
          <template v-if="loading">
            <tr v-for="i in 3" :key="`skeleton-${i}`">
              <td
                v-if="selectable"
                class="py-4 px-4"
              >
                <div class="h-4 w-4 bg-gray-200 rounded"></div>
              </td>
              <td
                v-for="column in columns"
                :key="`skeleton-${i}-${column.key}`"
                class="py-4 px-4"
              >
                <div class="h-4 bg-gray-200 rounded w-3/4"></div>
              </td>
              <td
                v-if="actions.length > 0"
                class="py-4 px-4"
              >
                <div class="h-8 bg-gray-200 rounded w-24 ml-auto"></div>
              </td>
            </tr>
          </template>

          <template v-else-if="paginatedItems.length > 0">
            <tr
              v-for="(item, index) in paginatedItems"
              :key="index"
              :class="[
                'hover:bg-gray-50 transition-colors cursor-pointer',
                striped && index % 2 === 0 ? 'bg-gray-50' : '',
                isSelected(item) ? 'bg-indigo-50' : ''
              ]"
              @click="handleRowClick(item)"
            >
              <!-- Selection cell -->
              <td
                v-if="selectable"
                class="py-4 px-4"
                @click.stop
              >
                <input
                  type="checkbox"
                  :checked="isSelected(item)"
                  @change="toggleSelection(item)"
                  class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
              </td>

              <!-- Data cells -->
              <td
                v-for="column in columns"
                :key="`${index}-${column.key}`"
                :class="[
                  'py-4 px-4 whitespace-nowrap text-sm text-gray-800',
                  column.align ? `text-${column.align}` : ''
                ]"
              >
                {{ getCellValue(item, column) }}
              </td>

              <!-- Actions cell -->
              <td
                v-if="actions.length > 0"
                class="py-4 px-4 whitespace-nowrap text-right text-sm font-medium"
                @click.stop
              >
                <div class="flex justify-end space-x-2">
                  <button
                    v-for="(action, actionIndex) in actions"
                    :key="actionIndex"
                    @click="handleAction(action, item)"
                    :class="[
                      'inline-flex items-center px-3 py-1.5 border rounded-md text-xs font-medium',
                      action.variant === 'primary' ? 'bg-indigo-600 text-white border-indigo-600 hover:bg-indigo-700' :
                      action.variant === 'success' ? 'bg-green-600 text-white border-green-600 hover:bg-green-700' :
                      action.variant === 'danger' ? 'bg-red-600 text-white border-red-600 hover:bg-red-700' :
                      action.variant === 'warning' ? 'bg-yellow-500 text-white border-yellow-500 hover:bg-yellow-600' :
                      action.variant === 'info' ? 'bg-blue-500 text-white border-blue-500 hover:bg-blue-600' :
                      'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    ]"
                  >
                    <span v-if="action.icon" class="mr-1">{{ action.icon }}</span>
                    {{ action.label }}
                  </button>
                </div>
              </td>
            </tr>
          </template>

          <tr v-else>
            <td
              :colspan="selectable ? columns.length + (actions.length > 0 ? 2 : 1) : columns.length + (actions.length > 0 ? 1 : 0)"
              class="py-8 px-4 text-center text-gray-500"
            >
              {{ emptyText }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="pagination && totalPages > 1"
      class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6"
    >
      <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div>
          <p class="text-sm text-gray-700">
            Showing
            <span class="font-medium">{{ (currentPage - 1) * itemsPerPage + 1 }}</span>
            to
            <span class="font-medium">
              {{ Math.min(currentPage * itemsPerPage, filteredItems.length) }}
            </span>
            of
            <span class="font-medium">{{ filteredItems.length }}</span>
            results
          </p>
        </div>
        <div>
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <!-- Previous Page -->
            <button
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
              class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="sr-only">Previous</span>
              ◀
            </button>

            <!-- Page numbers -->
            <template v-for="page in totalPages" :key="page">
              <button
                v-if="totalPages <= 7 || page === 1 || page === totalPages || Math.abs(page - currentPage) <= 1"
                @click="goToPage(page)"
                :class="[
                  'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                  currentPage === page
                    ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>

              <!-- Ellipsis -->
              <span
                v-else-if="(page === 2 && currentPage > 3) || (page === totalPages - 1 && currentPage < totalPages - 2)"
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
              >
                ...
              </span>
            </template>

            <!-- Next Page -->
            <button
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
              class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="sr-only">Next</span>
              ▶
            </button>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>
