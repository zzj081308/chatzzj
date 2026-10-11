<script setup lang="ts">
import { ref, computed } from 'vue'
import { NButton, useMessage } from 'naive-ui'
import { useChatStore } from '../../stores/chat'
import { useFriendsStore } from '../../stores/friends'
import { useWebSocket } from '../../composables/useWebSocket'
import { uploadImage, uploadFile } from '../../api/upload'

const messageText = ref('')
const sending = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const chatStore = useChatStore()
const friendsStore = useFriendsStore()
const ws = useWebSocket()
const msg = useMessage()

let typingTimer: ReturnType<typeof setTimeout> | null = null

interface FilePreview {
  id: string
  file: File
  url: string
  isImage: boolean
  size: number
}

const previews = ref<FilePreview[]>([])
let previewCounter = 0

function addFileToPreview(file: File) {
  const id = 'preview-' + (++previewCounter)
  const isImage = file.type.startsWith('image/')
  const url = isImage ? URL.createObjectURL(file) : ''
  previews.value.push({ id, file, url, isImage, size: file.size })
}

function removePreview(id: string) {
  const idx = previews.value.findIndex(p => p.id === id)
  if (idx >= 0) {
    const preview = previews.value[idx]
    if (preview.url) URL.revokeObjectURL(preview.url)
    previews.value.splice(idx, 1)
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function openFilePicker() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  for (const file of Array.from(input.files)) {
    const dup = previews.value.some(p => p.file.name === file.name && p.file.size === file.size)
    if (!dup) {
      addFileToPreview(file)
    }
  }
  input.value = ''
}

function onTyping() {
  if (!chatStore.activeFriendId) return
  ws.sendTyping(chatStore.activeFriendId, true)
  if (typingTimer) clearTimeout(typingTimer)
      
  typingTimer = setTimeout(() => {
    if (chatStore.activeFriendId) {
      ws.sendTyping(chatStore.activeFriendId, false)
    }
  }, 2000)
}

async function sendAll() {
  const text = messageText.value.trim()
  const files = [...previews.value]
  if (!text && files.length === 0) return
  if (!chatStore.activeFriendId) return

  sending.value = true

  try {
    const uploadedItems: { type: 'image' | 'file'; url: string; name: string }[] = []
    for (const preview of files) {
      try {
        if (preview.isImage) {
          const res = await uploadImage(preview.file)
          uploadedItems.push({ type: 'image', url: res.image_url, name: preview.file.name })
        } else {
          const res = await uploadFile(preview.file)
          uploadedItems.push({ type: 'file', url: res.file_url, name: res.file_name })
        }
      } catch (err: any) {
        msg.error('文件上传失败: ' + preview.file.name)
      }
    }

    if (text) {
      ws.sendMessage(chatStore.activeFriendId, 'text', text)
        // Start AI thinking indicator
        const activeFriend_ = friendsStore.friends.find(f => f.id === chatStore.activeFriendId)
        if (activeFriend_?.is_ai) chatStore.setAiThinking(Date.now())
        // Start AI thinking indicator if chatting with AI assistant
    }

    for (const item of uploadedItems) {
      if (item.type === 'image') {
        ws.sendMessage(chatStore.activeFriendId, 'image', undefined, item.url)
      } else {
        ws.sendMessage(chatStore.activeFriendId, 'file', undefined, undefined, item.url, item.name)
      }
    }

    messageText.value = ''
    for (const p of previews.value) {
      if (p.url) URL.revokeObjectURL(p.url)
    }
    previews.value = []

    if (typingTimer) {
      clearTimeout(typingTimer)
      
      ws.sendTyping(chatStore.activeFriendId, false)
    }
  } finally {
    sending.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendAll()
  }
}

const canSend = computed(() => {
  return messageText.value.trim().length > 0 || previews.value.length > 0
})
</script>

<template>
  <div class="message-input-bar" v-if="chatStore.activeFriendId">
    <div class="file-previews" v-if="previews.length > 0">
      <div class="preview-item" v-for="preview in previews" :key="preview.id">
        <button class="preview-close" @click="removePreview(preview.id)">&times;</button>
        <div class="preview-thumb" v-if="preview.isImage">
          <img :src="preview.url" :alt="preview.file.name" />
        </div>
        <div class="preview-thumb file-thumb" v-else>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
        </div>
        <div class="preview-info">
          <span class="preview-filename">{{ preview.file.name }}</span>
          <span class="preview-size">{{ formatFileSize(preview.size) }}</span>
        </div>
      </div>
    </div>

    <div class="input-row">
      <textarea
        v-model="messageText"
        class="chat-textarea"
        placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
        rows="3"
        @input="onTyping"
        @keydown="handleKeydown"
      ></textarea>
      <div class="input-actions">
        <NButton text class="upload-btn" :disabled="sending" @click="openFilePicker">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </NButton>
        <input
          ref="fileInput"
          type="file"
          multiple
          class="file-input-hidden"
          @change="handleFileSelect"
        />
        <NButton
          type="primary"
          @click="sendAll"
          :disabled="!canSend || sending"
          :loading="sending"
          class="send-btn"
        >
          发送
        </NButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-input-bar {
  border-top: 2px solid #e8e8e8;
  background: #fff;
  padding: 12px 20px;
}

.file-previews {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.preview-item {
  position: relative;
  width: 120px;
  background: #f8f9fb;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

.preview-close {
  position: absolute;
  top: 3px;
  right: 3px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  padding: 0;
}

.preview-close:hover {
  background: rgba(0, 0, 0, 0.7);
}

.preview-thumb {
  width: 100%;
  height: 70px;
  overflow: hidden;
  background: #eef0f4;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-thumb.file-thumb svg {
  width: 32px;
  height: 32px;
  color: #888;
}

.preview-info {
  padding: 4px 6px;
}

.preview-filename {
  display: block;
  font-size: 11px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 108px;
}

.preview-size {
  display: block;
  font-size: 10px;
  color: #999;
}

.input-row {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.chat-textarea {
  flex: 1;
  min-height: 80px;
  max-height: 200px;
  padding: 12px 16px;
  font-size: 15px;
  line-height: 1.6;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  outline: none;
  resize: vertical;
  font-family: inherit;
  transition: border-color 0.2s;
}

.chat-textarea:focus {
  border-color: #5b8def;
}

.input-actions {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.upload-btn {
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 42px;
  width: 42px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.send-btn {
  height: 42px;
  min-width: 76px;
  font-size: 15px;
  border-radius: 8px;
}

.file-input-hidden {
  display: none;
}
</style>
