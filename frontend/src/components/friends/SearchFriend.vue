<script setup lang="ts">
import { ref } from 'vue'
import { NPopover, NButton, NInput, NAvatar, useMessage } from 'naive-ui'
import { useFriendsStore } from '../../stores/friends'

const showPopover = ref(false)
const searchQuery = ref('')
const friendsStore = useFriendsStore()
const msg = useMessage()

let searchTimer: ReturnType<typeof setTimeout> | null = null

function onSearchInput(value: string) {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    friendsStore.searchUsers(value)
  }, 300)
}

async function sendRequest(userId: number) {
  try {
    await friendsStore.sendRequest(userId)
    msg.success('好友请求已发送')
  } catch (err: any) {
    msg.error(err.response?.data?.detail || '发送失败')
  }
}
</script>

<template>
  <NPopover trigger="click" :show="showPopover" @update:show="showPopover = $event" placement="bottom-start">
    <template #trigger>
      <NButton text size="small" class="action-btn">➕ 添加好友</NButton>
    </template>

    <div class="search-popover">
      <NInput
        v-model:value="searchQuery"
        placeholder="搜索用户名..."
        clearable
        size="small"
        @update:value="onSearchInput"
      />

      <div class="search-results">
        <div v-if="!searchQuery.trim()" class="search-hint">输入用户名搜索</div>
        <div v-else-if="!friendsStore.searchResults.length" class="search-hint">未找到用户</div>
        <div
          v-for="user in friendsStore.searchResults"
          :key="user.id"
          class="search-item"
        >
          <div class="search-user">
            <NAvatar :size="32" round>{{ user.username[0]?.toUpperCase() }}</NAvatar>
            <span class="search-username">{{ user.username }}</span>
          </div>
          <NButton size="tiny" type="primary" @click="sendRequest(user.id)">添加</NButton>
        </div>
      </div>
    </div>
  </NPopover>
</template>

<style scoped>
.search-popover {
  width: 280px;
  padding: 8px 0;
}
.search-results {
  max-height: 300px;
  overflow-y: auto;
  margin-top: 8px;
}
.search-hint {
  text-align: center;
  padding: 16px;
  color: #999;
  font-size: 13px;
}
.search-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--n-border-color);
}
.search-user {
  display: flex;
  align-items: center;
  gap: 8px;
}
.search-username {
  font-size: 14px;
}
.action-btn {
  font-size: 13px;
}
</style>
