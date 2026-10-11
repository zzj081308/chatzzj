<script setup lang="ts">
import { computed, watch, ref, nextTick } from 'vue'
import { NScrollbar } from 'naive-ui'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import { useFriendsStore } from '../../stores/friends'
import MessageBubble from './MessageBubble.vue'
import TypingIndicator from './TypingIndicator.vue'

const chatStore = useChatStore()
const authStore = useAuthStore()
const friendsStore = useFriendsStore()
const scrollRef = ref<any>(null)

const activeMessages = computed(() => {
  return chatStore.activeFriendId ? chatStore.getMessages(chatStore.activeFriendId) : []
})

const isTyping = computed(() => {
  return chatStore.activeFriendId ? chatStore.typingUsers.has(chatStore.activeFriendId) : false
})


const activeFriend = computed(() =>
  friendsStore.friends.find((f) => f.id === chatStore.activeFriendId)
)

function getSenderAvatar(senderId: number): string | null {
  if (senderId === authStore.user?.id) {
    return authStore.user?.avatar_url || null
  }
  return activeFriend.value?.avatar_url || null
}

function getSenderName(senderId: number): string {
  if (senderId === authStore.user?.id) {
    return authStore.user?.username || '?'
  }
  return activeFriend.value?.username || '?'
}

watch(
  () => activeMessages.value.length,
  () => {
    nextTick(() => {
      scrollRef.value?.scrollTo({ top: 999999 })
    })
  }
)

function onScroll(e: Event) {
  const target = e.target as HTMLElement
  if (target.scrollTop <= 50 && chatStore.activeFriendId) {
    const cursor = chatStore.nextCursors.get(chatStore.activeFriendId)
    const hasMore = chatStore.hasMore.get(chatStore.activeFriendId)
    if (hasMore && cursor) {
      const prevHeight = target.scrollHeight
      chatStore.loadHistory(chatStore.activeFriendId, cursor).then(() => {
        nextTick(() => {
          target.scrollTop = target.scrollHeight - prevHeight
        })
      })
    }
  }
}
</script>

<template>
  <div class="chat-window">
    <NScrollbar ref="scrollRef" class="messages-container" @scroll="onScroll">
      <div class="messages-list">
        <MessageBubble
          v-for="msg in activeMessages"
          :key="msg.client_msg_id || msg.id"
          :message="msg"
          :is-own="msg.sender_id === authStore.user?.id"
          :sender-avatar="getSenderAvatar(msg.sender_id)"
          :sender-name="getSenderName(msg.sender_id)"
        />
        <TypingIndicator v-if="isTyping" />
      </div>
    </NScrollbar>
  </div>
</template>

<style scoped>
.chat-window {
  flex: 1;
  overflow: hidden;
  background: #f5f6fa;
}
.messages-container {
  height: 100%;
}
.messages-list {
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  gap: 2px;
  min-height: 100%;
  justify-content: flex-end;
}
</style>
