<script setup lang="ts">
import { computed } from 'vue'
import { NAvatar, NBadge, NImage, NText } from 'naive-ui'
import type { Friend } from '../../types'
import { useChatStore } from '../../stores/chat'
import { formatPreviewTime } from '../../utils/formatTime'

const props = defineProps<{
  friend: Friend
  active: boolean
}>()

const chatStore = useChatStore()

const unreadCount = computed(() => {
  const local = chatStore.unreadCounts.get(props.friend.id)
  if (local !== undefined) return local
  return props.friend.unread_count
})
</script>

<template>
  <div class="friend-item" :class="{ active }">
    <div class="friend-avatar">
      <NBadge :type="friend.is_online ? 'success' : 'default'" dot :offset="[-2, 30]">
        <NImage
          v-if="friend.avatar_url"
          :src="friend.avatar_url"
          width="44"
          height="44"
          class="avatar-nimage-friend"
          :img-props="{ style: 'object-fit: cover; border-radius: 50%; width: 44px; height: 44px;' }"
        />
        <NAvatar v-else :size="44" round>
          {{ friend.username[0]?.toUpperCase() }}
        </NAvatar>
      </NBadge>
    </div>
    <div class="friend-content">
      <div class="friend-top">
        <NText strong class="friend-name">{{ friend.username }}</NText>
        <NText depth="3" class="friend-time">
          {{ friend.last_message_time ? formatPreviewTime(friend.last_message_time) : '' }}
        </NText>
      </div>
      <div class="friend-bottom">
        <NText depth="3" class="last-message" :ellipsis="{ tooltip: true }">
          {{ friend.last_message || '暂无消息' }}
        </NText>
        <NBadge v-if="unreadCount" :value="unreadCount" type="error" :max="99" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.friend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid var(--n-border-color);
}
.friend-item:hover {
  background: var(--n-color-hover);
}
.friend-item.active {
  background: var(--n-color-target);
}
.friend-avatar {
  flex-shrink: 0;
}
.avatar-nimage-friend {
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  display: block;
}
.friend-content {
  flex: 1;
  min-width: 0;
}
.friend-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.friend-name {
  font-size: 15px;
}
.friend-time {
  font-size: 11px;
  flex-shrink: 0;
}
.friend-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.last-message {
  font-size: 13px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
