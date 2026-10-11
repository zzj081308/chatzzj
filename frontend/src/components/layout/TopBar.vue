<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { NAvatar, NImage, NText, NButton, NDropdown, useMessage } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { useChatStore } from '../../stores/chat'
import { useFriendsStore } from '../../stores/friends'
import { deleteMessages } from '../../api/messages'

const chatStore = useChatStore()
const friendsStore = useFriendsStore()
const message = useMessage()
const thinkingSeconds = ref<number | null>(null)
let _thinkInt: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  _thinkInt = setInterval(() => {
    const s = chatStore.aiThinkingSince
    thinkingSeconds.value = s ? Math.floor((Date.now() - s) / 1000) : null
  }, 500)
})
onUnmounted(() => {
  if (_thinkInt) clearInterval(_thinkInt)
})
const friend = computed(() =>
  friendsStore.friends.find((f) => f.id === chatStore.activeFriendId)
)
async function handleClearHistory() {
  if (!friend.value) return
  try {
    await deleteMessages(friend.value.id)
    chatStore.clearMessages(friend.value.id)
    message.success('聊天记录已清除')
  } catch (err: any) {
    message.error(err.response?.data?.detail || '清除失败')
  }
}
async function handleDeleteFriend() {
  if (!friend.value) return
  try {
    await friendsStore.removeFriend(friend.value.id)
    message.success('好友已删除')
  } catch (err: any) {
    message.error(err.response?.data?.detail || '删除失败')
  }
}
const dropdownOptions = computed<MenuOption[]>(() => {
  const opts: MenuOption[] = [
    {
      label: '清除聊天记录',
      key: 'clear-history',
    },
  ]
  if (!friend.value?.is_ai) {
    opts.push({
      label: '删除好友',
      key: 'delete-friend',
    })
  }
  return opts
})
function handleDropdownSelect(key: string) {
  if (key === 'clear-history') {
    handleClearHistory()
  } else if (key === 'delete-friend') {
    handleDeleteFriend()
  }
}
</script>

<template>
  <div class="topbar" v-if="friend">
    <div class="friend-info">
      <NImage v-if="friend.avatar_url" :src="friend.avatar_url" width="36" height="36" class="avatar-nimage-topbar"
        :img-props="{ style: 'object-fit: cover; border-radius: 50%; width: 36px; height: 36px;' }" />
      <NAvatar v-else :size="36" round>
        {{ friend.username[0]?.toUpperCase() }}
      </NAvatar>
      <div class="text-info">
        <NText strong>{{ friend.username }}</NText>
        <NText depth="3" :type="friend.is_online ? 'success' : 'default'" class="status-text">
          {{ friend.is_online ? '在线' : '离线' }}
        </NText>
        <div v-if="thinkingSeconds !== null && friend?.username === 'AI助手'" class="ai-thinking">
          <span class="think-spin"></span>思考中...{{ thinkingSeconds }}s
        </div>
      </div>
    </div>
    <NDropdown trigger="click" :options="dropdownOptions" placement="bottom-end" @select="handleDropdownSelect">
      <NButton text size="small" class="more-btn">···</NButton>
    </NDropdown>
  </div>
</template>

<style scoped>

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  width: 100%;
}
.friend-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.avatar-nimage-topbar {
  flex-shrink: 0;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
}
.text-info {
  display: flex;
  flex-direction: column;
}
.status-text {
  font-size: 12px;
}
.more-btn {
  font-size: 20px;
  font-weight: bold;
  letter-spacing: 2px;
  line-height: 1;
}
.think-spin {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #5b8def;
  border-top-color: transparent;
  border-radius: 50%;
  animation: think-spin 0.6s linear infinite;
  margin-right: 4px;
  vertical-align: middle;
}
@keyframes think-spin {
  to { transform: rotate(360deg); }
}

</style>
