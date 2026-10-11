import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Message } from '../types'
import * as messagesApi from '../api/messages'

export const useChatStore = defineStore('chat', () => {
  const activeFriendId = ref<number | null>(null)
  const messages = ref<Map<number, Message[]>>(new Map())
  const unreadCounts = ref<Map<number, number>>(new Map())
  const aiThinkingSince = ref<number | null>(null)
  const typingUsers = ref<Set<number>>(new Set())
  const hasMore = ref<Map<number, boolean>>(new Map())
  const nextCursors = ref<Map<number, number | null>>(new Map())

  function getMessages(friendId: number): Message[] {
    return messages.value.get(friendId) || []
  }

  function addMessage(friendId: number, message: Message) {
    const existing = messages.value.get(friendId) || []
    // Avoid duplicates by client_msg_id or server id
    const dup = existing.find(
      (m) => (message.client_msg_id && m.client_msg_id === message.client_msg_id) ||
             (message.id && m.id === message.id)
    )
    if (!dup) {
      // Append to end �?messages are stored oldest-first
      messages.value.set(friendId, [...existing, message])
    }
  }

  function updateMessageStatus(clientMsgId: string, serverId: number, createdAt: string) {
    for (const [, msgs] of messages.value) {
      const msg = msgs.find((m) => m.client_msg_id === clientMsgId)
      if (msg) {
        msg.id = serverId
        msg.created_at = createdAt
        msg.pending = false
        break
      }
    }
  }

  function setMessages(friendId: number, msgs: Message[]) {
    messages.value.set(friendId, msgs)
  }

  function prependMessages(friendId: number, olderMsgs: Message[]) {
    const existing = messages.value.get(friendId) || []
    const existingIds = new Set(existing.map((m) => m.id))
    const newMsgs = olderMsgs.filter((m) => !existingIds.has(m.id))
    // newMsgs are older �?put them before existing (oldest-first order)
    messages.value.set(friendId, [...newMsgs, ...existing])
  }

  async function loadHistory(friendId: number, cursor?: number) {
    const res = await messagesApi.getMessageHistory(friendId, cursor)
    if (cursor) {
      prependMessages(friendId, res.messages.reverse())
    } else {
      setMessages(friendId, res.messages.reverse())
    }
    hasMore.value.set(friendId, res.has_more)
    nextCursors.value.set(friendId, res.next_cursor)
    return res
  }


  function setAiThinking(timestamp: number | null) {
    aiThinkingSince.value = timestamp
  }

  function setTyping(userId: number, isTyping: boolean) {
    if (isTyping) {
      typingUsers.value.add(userId)
    } else {
      typingUsers.value.delete(userId)
    }
  }

  function setUnreadCount(friendId: number, count: number) {
    unreadCounts.value.set(friendId, count)
  }

  function clearUnread(friendId: number) {
    unreadCounts.value.set(friendId, 0)
  }

  function removeMessageByClientId(friendId: number, clientMsgId: string) {
    const msgs = getMessages(friendId).filter(m => m.client_msg_id !== clientMsgId)
    setMessages(friendId, msgs)
  }

  function markMessageFailed(clientMsgId: string) {
    for (const [, msgs] of messages.value) {
      const msg = msgs.find((m) => m.client_msg_id === clientMsgId)
      if (msg) {
        msg.pending = false
        msg.failed = true
        break
      }
    }
  }

  function clearMessages(friendId: number) {
    messages.value.delete(friendId)
    hasMore.value.delete(friendId)
    nextCursors.value.delete(friendId)
  }

  function setActiveFriend(friendId: number | null) {
    activeFriendId.value = friendId
    if (friendId) {
      clearUnread(friendId)
    }
  }

  return {
    aiThinkingSince, setAiThinking,
    activeFriendId, messages, unreadCounts, typingUsers, hasMore, nextCursors,
    getMessages, addMessage, updateMessageStatus, setMessages, prependMessages,
    loadHistory, setTyping, setUnreadCount, clearUnread, setActiveFriend,
    removeMessageByClientId, markMessageFailed, clearMessages,
  }
})


