import { ref, computed } from 'vue';
import { defineStore } from 'pinia';

import { client } from './client';
import type { components } from '../api';

type ChatRead = components["schemas"]["ChatRead"];
type ChatCreate = components["schemas"]["ChatCreate"];
type ChatReadWithMessages = components["schemas"]["ChatReadWithMessages"];
type MessageRead = components["schemas"]["MessageRead"];
type MessageCreate = components["schemas"]["MessageCreate"];

export const useChatStore = defineStore('chat', () => {
  const chats = ref<ChatRead[]>([]);
  const selectedChat = ref<ChatReadWithMessages | null>(null);
  const chatCreate = ref<ChatCreate>({
    name: "",
  });

  const isLoadingChats = ref(false);
  const isLoadingMessages = ref(false);
  const isSendingMessages = ref(false);
  const isCreatingChat = ref(false);

  const apiError = ref<string | null>(null);

  const currentMessages = computed((): MessageRead[] => {
    return selectedChat.value?.messages ?? [];
  });

  async function fetchChats() {
    isLoadingChats.value = true;
    apiError.value = null;
    try {
      const { data, error: apiError } = await client.GET('/api/v1/chat_v2/chats/');
      chats.value = data ?? [];
    } catch (err) {
      console.error('Error fetching chats:', err)
      apiError.value = err instanceof Error ? err.message : 'Unknown error occurred'
    } finally {
      isLoadingChats.value = false
    }
  }

  async function createChat() {
    isCreatingChat.value = true;
    apiError.value = null;
    try {
      const { data, error: apiError } = await client.POST('/api/v1/chat_v2/chats/');

      chats.value.push(data);
    } catch (err) {
      console.error('Error creating chat:', err)
      apiError.value = err instanceof Error ? err.message : 'Unknown error occurred'
    } finally {
      isCreatingChat.value = false
    }
  }
});
