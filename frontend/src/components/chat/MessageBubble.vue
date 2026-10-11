<script setup lang="ts">
import { NAvatar, NButton, NImage, NTag, NText } from 'naive-ui'
import type { Message } from '../../types'
import { formatMessageTime } from '../../utils/formatTime'
import { useWebSocket } from '../../composables/useWebSocket'

const props = defineProps<{
  message: Message
  isOwn: boolean
  senderAvatar: string | null
  senderName: string
}>()

const ws = useWebSocket()

function retrySend() {
  if (!props.message.client_msg_id) return
  ws.sendMessage(
    props.message.receiver_id,
    props.message.message_type,
    props.message.content || undefined,
    props.message.image_url || undefined,
    props.message.file_url || undefined,
    props.message.file_name || undefined,
  )
}
</script>

<template>
  <div class="message-row" :class="{ own: isOwn }">
    <!-- Friend avatar (left side) -->
    <template v-if="!isOwn">
      <NImage
        v-if="senderAvatar"
        :src="senderAvatar"
        width="30"
        height="30"
        class="avatar-nimage"
        :img-props="{ style: 'object-fit: cover; border-radius: 50%; width: 30px; height: 30px;' }"
      />
      <NAvatar v-else :size="30" round class="avatar">
        {{ senderName[0]?.toUpperCase() || '?' }}
      </NAvatar>
    </template>

    <div class="bubble-wrapper">
      <div class="bubble" :class="{ own: isOwn, pending: message.pending, failed: message.failed }">
        <!-- Text message -->
        <template v-if="message.message_type === 'text'">
          <NText>{{ message.content }}</NText>
        </template>

        <!-- Image message -->
        <template v-else-if="message.message_type === 'image' && message.image_url">
          <NImage :src="message.image_url" width="200" class="message-image" />
        </template>

        <!-- File message -->
        <template v-else-if="message.message_type === 'file' && message.file_url">
          <a class="file-message" :href="message.file_url" target="_blank" download>
            <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            <div class="file-info">
              <span class="file-name">{{ message.file_name || message.file_url?.split('/').pop() || '文件' }}</span>
              <span class="file-action">点击下载</span>
            </div>
          </a>
        </template>

        <!-- Pending indicator -->
        <NTag v-if="message.pending" type="info" size="small" :bordered="false" class="pending-tag">
          发送中...
        </NTag>

        <!-- Failed indicator with retry button -->
        <div v-if="message.failed && isOwn" class="failed-row">
          <NTag type="error" size="small" :bordered="false">发送失败</NTag>
          <NButton size="tiny" type="error" quaternary @click="retrySend">重试</NButton>
        </div>
      </div>
      <div class="message-time" :class="{ own: isOwn }">
        {{ formatMessageTime(message.created_at) }}
      </div>
    </div>

    <!-- Own avatar (right side) -->
    <template v-if="isOwn">
      <NImage
        v-if="senderAvatar"
        :src="senderAvatar"
        width="30"
        height="30"
        class="avatar-nimage"
        :img-props="{ style: 'object-fit: cover; border-radius: 50%; width: 30px; height: 30px;' }"
      />
      <NAvatar v-else :size="30" round class="avatar">
        {{ senderName[0]?.toUpperCase() || '?' }}
      </NAvatar>
    </template>
  </div>
</template>

<style scoped>
.message-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin-bottom: 12px;
}
.message-row.own {
  flex-direction: row-reverse;
}
.avatar {
  flex-shrink: 0;
}
.avatar-nimage {
  flex-shrink: 0;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
}
.bubble-wrapper {
  max-width: 55%;
  display: flex;
  flex-direction: column;
}
.own .bubble-wrapper {
  align-items: flex-end;
}
.bubble {
  padding: 8px 14px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
  position: relative;
  word-break: break-word;
}
.bubble.own {
  background: #5b8def;
  color: #fff;
}
.bubble.own :deep(.n-text) {
  color: #fff;
}
.bubble.pending {
  opacity: 0.7;
}
.bubble.failed {
  border: 2px solid #e88080;
  background: #fff5f5;
}
.failed-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}
.message-image {
  border-radius: 8px;
  cursor: pointer;
}
.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  padding: 0 4px;
}
.message-time.own {
  text-align: right;
}
.pending-tag {
  margin-top: 4px;
}
.file-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f0f2f5;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  min-width: 180px;
  transition: background 0.2s;
}
.file-message:hover {
  background: #e4e7ec;
}
.own .file-message {
  background: rgba(255,255,255,0.15);
}
.own .file-message:hover {
  background: rgba(255,255,255,0.25);
}
.file-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.file-name {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 150px;
}
.file-action {
  font-size: 11px;
  color: #888;
}
.own .file-action {
  color: rgba(255,255,255,0.7);
}
.file-message svg {
  flex-shrink: 0;
}
</style>
