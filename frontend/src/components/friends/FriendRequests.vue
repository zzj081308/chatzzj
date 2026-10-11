<script setup lang="ts">
import { NPopover, NButton, NAvatar, useMessage } from 'naive-ui'
import { useFriendsStore } from '../../stores/friends'

const friendsStore = useFriendsStore()
const msg = useMessage()

async function accept(requestId: number) {
  try {
    await friendsStore.acceptRequest(requestId)
    msg.success('已接受好友请求')
  } catch (err: any) {
    msg.error(err.response?.data?.detail || '操作失败')
  }
}

async function reject(requestId: number) {
  try {
    await friendsStore.rejectRequest(requestId)
    msg.success('已拒绝好友请求')
  } catch (err: any) {
    msg.error(err.response?.data?.detail || '操作失败')
  }
}
</script>

<template>
  <NPopover trigger="click" placement="bottom-start">
    <template #trigger>
      <slot name="trigger">
        <NButton text size="small">好友请求</NButton>
      </slot>
    </template>

    <div class="requests-popover">
      <h4 class="popover-title">好友请求</h4>
      <div v-if="!friendsStore.pendingRequests.length" class="empty-hint">
        暂无待处理的好友请求
      </div>
      <div
        v-for="req in friendsStore.pendingRequests"
        :key="req.id"
        class="request-item"
      >
        <div class="request-user">
          <NAvatar :size="36" round>
            {{ req.sender?.username?.[0]?.toUpperCase() || '?' }}
          </NAvatar>
          <div class="request-info">
            <span class="request-name">{{ req.sender?.username }}</span>
            <span v-if="req.message" class="request-message">{{ req.message }}</span>
          </div>
        </div>
        <div class="request-actions">
          <NButton size="tiny" type="primary" @click="accept(req.id)">接受</NButton>
          <NButton size="tiny" @click="reject(req.id)">拒绝</NButton>
        </div>
      </div>
    </div>
  </NPopover>
</template>

<style scoped>
.requests-popover {
  width: 300px;
  padding: 8px 0;
}
.popover-title {
  margin: 0 0 8px;
  font-size: 15px;
}
.empty-hint {
  text-align: center;
  padding: 16px;
  color: #999;
  font-size: 13px;
}
.request-item {
  padding: 10px 0;
  border-bottom: 1px solid var(--n-border-color);
}
.request-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.request-info {
  display: flex;
  flex-direction: column;
}
.request-name {
  font-size: 14px;
  font-weight: 500;
}
.request-message {
  font-size: 12px;
  color: #999;
}
.request-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
