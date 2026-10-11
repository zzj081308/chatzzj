import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { useFriendsStore } from '../stores/friends'
import { sendMessageRest } from '../api/messages'
import type { Message } from '../types'

const ACK_TIMEOUT_MS = 5000
const TYPING_THROTTLE_MS = 1000

function generateId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

const ws = ref<WebSocket | null>(null)
const connected = ref(false)
const reconnectAttempt = ref(0)
const maxReconnectDelay = 30000
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let isConnecting = false

const pendingAcks = new Map<string, ReturnType<typeof setTimeout>>()
const lastTypingSent = new Map<number, number>()
let visibilityCleanup: (() => void) | null = null

export function useWebSocket() {
  const authStore = useAuthStore()
  const chatStore = useChatStore()
  const friendsStore = useFriendsStore()

  function connect() {
    if (isConnecting) return
    if (ws.value && (ws.value.readyState === WebSocket.OPEN || ws.value.readyState === WebSocket.CONNECTING)) {
      return
    }

    const token = authStore.accessToken
    if (!token) return

    isConnecting = true

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/chat?token=${token}`

    if (ws.value) {
      ws.value.onclose = null
      ws.value.close()
      ws.value = null
    }

    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      connected.value = true
      isConnecting = false
      reconnectAttempt.value = 0
    }

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleMessage(data)
    }

    ws.value.onclose = () => {
      connected.value = false
      isConnecting = false
      ws.value = null
      clearAllPendingAcks()
      scheduleReconnect()
    }

    ws.value.onerror = () => {
      isConnecting = false
      ws.value?.close()
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempt.value), maxReconnectDelay)
    reconnectAttempt.value++
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      if (!connected.value) {
        connect()
      }
    }, delay)
  }

  function clearAllPendingAcks() {
    for (const [clientMsgId, timer] of pendingAcks) {
      clearTimeout(timer)
      chatStore.markMessageFailed(clientMsgId)
    }
    pendingAcks.clear()
  }

  function handleMessage(data: any) {
    switch (data.type) {
      case 'new_message': {
        const msg: Message = {
          id: data.id,
          sender_id: data.sender_id,
          receiver_id: data.receiver_id,
          message_type: data.message_type,
          content: data.content,
          image_url: data.image_url,
          file_url: data.file_url || null,
          file_name: data.file_name || null,
          is_read: data.is_read,
          created_at: data.created_at,
        }
        const friendId = data.sender_id === authStore.user?.id ? data.receiver_id : data.sender_id
        chatStore.addMessage(friendId, msg)
        // Clear AI thinking indicator when AI responds
        if (data.sender_id !== authStore.user?.id) {
          chatStore.setAiThinking(null)
        }
        if (chatStore.activeFriendId !== friendId) {
          const current = chatStore.unreadCounts.get(friendId) || 0
          chatStore.setUnreadCount(friendId, current + 1)
        }
        friendsStore.fetchFriends()
        break
      }
      case 'message_sent': {
        const timer = pendingAcks.get(data.client_msg_id)
        if (timer) {
          clearTimeout(timer)
          pendingAcks.delete(data.client_msg_id)
        }
        chatStore.updateMessageStatus(data.client_msg_id, data.server_id, data.created_at)
        break
      }
      case 'typing': {
        chatStore.setTyping(data.sender_id, data.is_typing)
        break
      }
      case 'read_receipt': {
        break
      }
      case 'friend_online': {
        friendsStore.setOnline(data.user_id, true)
        break
      }
      case 'friend_offline': {
        friendsStore.setOnline(data.user_id, false)
        chatStore.setTyping(data.user_id, false)
        break
      }
      case 'new_friend_request':
      case 'friend_request_accepted':
      case 'friend_request_update': {
        friendsStore.fetchFriends()
        friendsStore.fetchPendingRequests()
        break
      }
      case 'online_friends': {
        if (data.user_ids) {
          for (const uid of data.user_ids) {
            friendsStore.setOnline(uid, true)
          }
        }
        break
      }
      case 'pong':
        break
      case 'error': {
        console.error('WebSocket error:', data.detail)
        break
      }
    }
  }

  function send(data: Record<string, any>) {
    if (ws.value && connected.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
      return true
    }
    return false
  }

  async function sendMessage(
    receiverId: number,
    messageType: 'text' | 'image' | 'file',
    content?: string,
    imageUrl?: string,
    fileUrl?: string,
    fileName?: string,
  ) {
    const clientMsgId = generateId()
    const optimisticMsg: Message = {
      id: 0,
      sender_id: authStore.user!.id,
      receiver_id: receiverId,
      message_type: messageType,
      content: content || null,
      image_url: imageUrl || null,
      file_url: fileUrl || null,
      file_name: fileName || null,
      is_read: false,
      created_at: new Date().toISOString(),
      client_msg_id: clientMsgId,
      pending: true,
    }
    chatStore.addMessage(receiverId, optimisticMsg)

    const wsSent = send({
      type: 'chat_message',
      receiver_id: receiverId,
      message_type: messageType,
      content: content || null,
      image_url: imageUrl || null,
      file_url: fileUrl || null,
      file_name: fileName || null,
      client_msg_id: clientMsgId,
    })

    if (wsSent) {
      const timeout = setTimeout(async () => {
        pendingAcks.delete(clientMsgId)
        try {
          const msg = await sendMessageRest(receiverId, messageType, content, imageUrl, fileUrl, fileName)
          chatStore.updateMessageStatus(clientMsgId, msg.id, msg.created_at)
        } catch (err: any) {
          chatStore.markMessageFailed(clientMsgId)
        }
      }, ACK_TIMEOUT_MS)
      pendingAcks.set(clientMsgId, timeout)
    } else {
      try {
        const msg = await sendMessageRest(receiverId, messageType, content, imageUrl, fileUrl, fileName)
        chatStore.updateMessageStatus(clientMsgId, msg.id, msg.created_at)
        friendsStore.fetchFriends()
      } catch (err: any) {
        chatStore.removeMessageByClientId(receiverId, clientMsgId)
      }
    }
  }

  function sendTyping(receiverId: number, isTyping: boolean) {
    if (isTyping) {
      const now = Date.now()
      const last = lastTypingSent.get(receiverId) || 0
      if (now - last < TYPING_THROTTLE_MS) return
      lastTypingSent.set(receiverId, now)
    } else {
      lastTypingSent.delete(receiverId)
    }
    send({ type: 'typing', receiver_id: receiverId, is_typing: isTyping })
  }

  function sendReadReceipt(senderId: number, lastReadMessageId: number) {
    send({ type: 'read_receipt', sender_id: senderId, last_read_message_id: lastReadMessageId })
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    clearAllPendingAcks()
    lastTypingSent.clear()
    isConnecting = false
    ws.value?.close()
    ws.value = null
    connected.value = false
  }

  if (!visibilityCleanup) {
    const handler = () => {
      if (document.visibilityState === 'visible' && !connected.value && !isConnecting) {
        connect()
      }
    }
    document.addEventListener('visibilitychange', handler)
    visibilityCleanup = () => document.removeEventListener('visibilitychange', handler)
  }

  return {
    ws, connected, connect, disconnect, send, sendMessage, sendTyping, sendReadReceipt,
  }
}
