<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useFriendsStore } from '../../stores/friends'
import { useChatStore } from '../../stores/chat'
import { NAvatar, NButton, NBadge, NInput, NPopover, useMessage } from 'naive-ui'
import { uploadAvatar } from '../../api/upload'
import FriendListItem from '../friends/FriendListItem.vue'
import SearchFriend from '../friends/SearchFriend.vue'
import FriendRequests from '../friends/FriendRequests.vue'

const router = useRouter()
const authStore = useAuthStore()
const friendsStore = useFriendsStore()
const chatStore = useChatStore()
const msg = useMessage()

const searchQuery = ref('')
const avatarUploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const filteredFriends = computed(() => {
  if (!searchQuery.value.trim()) return friendsStore.sortedFriends
  return friendsStore.sortedFriends.filter((f) =>
    f.username.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const pendingCount = computed(() => friendsStore.pendingRequests.length)

function selectFriend(friendId: number) {
  chatStore.setActiveFriend(friendId)
  chatStore.loadHistory(friendId)
  chatStore.clearUnread(friendId)
  router.push(`/chat/${friendId}`)
}

function goToAdmin() {
  router.push('/admin')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function triggerAvatarUpload() {
  fileInputRef.value?.click()
}

async function handleAvatarChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  avatarUploading.value = true
  try {
    const res = await uploadAvatar(file)
    if (authStore.user) {
      authStore.user.avatar_url = res.avatar_url
      localStorage.setItem('user', JSON.stringify(authStore.user))
    }
    msg.success('头像更新成功')
  } catch (err: any) {
    msg.error(err.response?.data?.detail || '头像上传失败')
  } finally {
    avatarUploading.value = false
    // Reset file input
    if (target) target.value = ''
  }
}
</script>

<template>
  <div class="sidebar-container">
    <div class="sidebar-header">
      <div class="user-info">
        <div class="avatar-wrapper" @click="triggerAvatarUpload" :class="{ uploading: avatarUploading }">
          <NAvatar :size="36" round :src="authStore.user?.avatar_url || undefined">
            {{ authStore.user?.username?.[0]?.toUpperCase() }}
          </NAvatar>
          <div class="avatar-overlay">
            <span class="camera-icon">📷</span>
          </div>
        </div>
        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          style="display: none"
          @change="handleAvatarChange"
        />
        <span class="username">{{ authStore.user?.username }}</span>
      </div>
      <NPopover trigger="click" placement="bottom-end">
        <template #trigger>
          <NButton text size="small" class="logout-btn">⚙️</NButton>
        </template>
        <NButton type="error" size="small" @click="handleLogout">退出登录</NButton>
      </NPopover>
    </div>

    <div class="sidebar-search">
      <NInput v-model:value="searchQuery" placeholder="搜索好友..." clearable size="small" />
    </div>

    <div class="admin-link" v-if="authStore.user?.is_admin">
      <NButton text size="small" class="action-btn admin-btn" @click="goToAdmin">
        ⚙️ 管理后台
      </NButton>
    </div>

    <div class="sidebar-actions">
      <SearchFriend />
      <FriendRequests>
        <template #trigger>
          <NButton text size="small" class="action-btn">
            好友请求
            <NBadge v-if="pendingCount" :value="pendingCount" type="error" />
          </NButton>
        </template>
      </FriendRequests>
    </div>

    <div class="friend-list">
      <FriendListItem
        v-for="friend in filteredFriends"
        :key="friend.id"
        :friend="friend"
        :active="chatStore.activeFriendId === friend.id"
        @click="selectFriend(friend.id)"
      />
      <div v-if="!filteredFriends.length" class="empty-friends">
        暂无好友
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--n-border-color);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar-wrapper {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  transition: opacity 0.2s;
}
.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}
.avatar-wrapper.uploading {
  opacity: 0.5;
  pointer-events: none;
}
.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}
.camera-icon {
  font-size: 14px;
}
.username {
  font-weight: 600;
  font-size: 16px;
}
.sidebar-search {
  padding: 10px 16px;
}
.sidebar-actions {
  display: flex;
  gap: 8px;
  padding: 0 16px 10px;
}
.friend-list {
  flex: 1;
  overflow-y: auto;
}
.empty-friends {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}
</style>
