<template>
    <div class="space-y-3">
        <template v-if="loading">
            <p class="text-center py-8 text-gray-500">Loading tasks...</p>
        </template>

        <template v-else-if="error">
            <p class="text-center py-8 text-red-500">
                Error loading tasks: {{ error }}
            </p>
        </template>

        <template v-else-if="tasks.length === 0">
            <p class="text-center py-8 text-gray-500">
                No tasks yet. Add one to get started!
            </p>
        </template>

        <template v-else>
            <div>
                <button @click="counter.decrement()">-</button>
                <span>{{ counter.count }}</span>
                <button @click="counter.increment()">+</button>
            </div>
            <div class="overflow-x-auto shadow-md sm:rounded-lg">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg">
                        <tr>
                            <th
                                scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-warm-gray uppercase tracking-wider"
                            >
                                Status
                            </th>
                            <th
                                scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-warm-gray uppercase tracking-wider"
                            >
                                Task
                            </th>
                            <th
                                scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-warm-gray uppercase tracking-wider"
                            >
                                Agent
                            </th>
                            <th
                                scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-warm-gray uppercase tracking-wider"
                            >
                                Created
                            </th>
                            <th
                                scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-warm-gray uppercase tracking-wider"
                            >
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        <tr v-for="task in tasks" :key="task.id">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <input
                                    type="checkbox"
                                    :checked="task.completed"
                                    @change="() => emit('toggle', task.id)"
                                    class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                                />
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex flex-col">
                                    <span
                                        class="text-sm font-medium text-warm-gray"
                                        >{{ task.name }}</span
                                    >
                                    <span class="text-xs text-gray-500 mt-1">{{
                                        task.description
                                    }}</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex flex-col">
                                    <span class="text-sm text-warm-gray">{{
                                        task.agent.name
                                    }}</span>
                                    <span class="text-xs text-gray-500">
                                        {{ task.agent.agent_model }} ({{
                                            task.agent.agent_type
                                        }})
                                    </span>
                                    <span class="text-xs text-gray-500">
                                        State:
                                        <span
                                            :class="
                                                stateColor(task.agent.state)
                                            "
                                            >{{ task.agent.state }}</span
                                        >
                                    </span>
                                </div>
                            </td>
                            <td
                                class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                            >
                                {{ formatDate(task.agent.created_at) }}
                            </td>
                            <td
                                class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
                            >
                                <button
                                    @click="() => emit('delete', task.id)"
                                    class="text-red-600 hover:text-red-900"
                                    title="Delete task"
                                >
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        class="h-5 w-5"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                        />
                                    </svg>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </template>
    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import client from "../client";
import { addTask, tasks } from "../stores/task";
const tasks = ref([]);
const loading = ref(true);
const error = ref(null);

const emit = defineEmits(["toggle", "delete"]);

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};

const stateColor = (state) => {
    switch (state.toLowerCase()) {
        case "running":
            return "text-green-600";
        case "stopped":
            return "text-red-600";
        case "pending":
            return "text-yellow-600";
        default:
            return "text-gray-600";
    }
};

onMounted(async () => {
    try {
        const { data, error: fetchError } = await client["/tasks/"].GET({});
        if (fetchError) {
            throw new Error(fetchError.message || "Failed to fetch tasks");
        }
        tasks.value = data || [];
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
});
</script>
