import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Friend, FriendRequest, UserSearchResult } from '../types'
import * as friendsApi from '../api/friends'
import * as usersApi from '../api/users'
import { useChatStore } from './chat'

export const useFriendsStore = defineStore('friends', () => {
  const friends = ref<Friend[]>([])
  const pendingRequests = ref<FriendRequest[]>([])
  const sentRequests = ref<FriendRequest[]>([])
  const searchResults = ref<UserSearchResult[]>([])
  const onlineUserIds = ref<Set<number>>(new Set())

  // Sort with online friends first, then by last message time
  const sortedFriends = computed(() => {
    return [...friends.value].sort((a, b) => {
      if (a.is_online !== b.is_online) return a.is_online ? -1 : 1
      const aTime = a.last_message_time ? new Date(a.last_message_time).getTime() : 0
      const bTime = b.last_message_time ? new Date(b.last_message_time).getTime() : 0
      return bTime - aTime
    })
  })

  let fetchFriendsTimer: ReturnType<typeof setTimeout> | null = null
  let fetchFriendsPending: Promise<Friend[]> | null = null

  async function fetchFriends(immediate = false) {
    // Debounce: skip if called too frequently (unless immediate)
    if (!immediate) {
      if (fetchFriendsPending) return fetchFriendsPending
      if (fetchFriendsTimer) return Promise.resolve(friends.value)
      fetchFriendsTimer = setTimeout(() => { fetchFriendsTimer = null }, 1000)
    }
    try {
      fetchFriendsPending = friendsApi.getFriends()
      friends.value = await fetchFriendsPending
      return friends.value
    } finally {
      fetchFriendsPending = null
    }
  }

  async function searchUsers(query: string) {
    if (!query.trim()) {
      searchResults.value = []
      return
    }
    searchResults.value = await usersApi.searchUsers(query)
  }

  async function sendRequest(receiverId: number, message?: string) {
    const req = await friendsApi.sendFriendRequest(receiverId, message)
    await fetchSentRequests()
    return req
  }

  async function fetchPendingRequests() {
    pendingRequests.value = await friendsApi.getPendingRequests()
  }

  async function fetchSentRequests() {
    sentRequests.value = await friendsApi.getSentRequests()
  }

  async function acceptRequest(requestId: number) {
    await friendsApi.acceptRequest(requestId)
    await fetchPendingRequests()
    await fetchFriends()
  }

  async function rejectRequest(requestId: number) {
    await friendsApi.rejectRequest(requestId)
    await fetchPendingRequests()
  }

  async function removeFriend(friendId: number) {
    await friendsApi.removeFriend(friendId)
    friends.value = friends.value.filter((f) => f.id !== friendId)
    // Also clear chat messages for this friend
    const chatStore = useChatStore()
    chatStore.clearMessages(friendId)
    if (chatStore.activeFriendId === friendId) {
      chatStore.setActiveFriend(null)
    }
  }

  function setOnline(userId: number, online: boolean) {
    if (online) {
      onlineUserIds.value.add(userId)
    } else {
      onlineUserIds.value.delete(userId)
    }
    // Update friend entries
    const friend = friends.value.find((f) => f.id === userId)
    if (friend) {
      friend.is_online = online
    }
  }

  return {
    friends, sortedFriends, pendingRequests, sentRequests, searchResults, onlineUserIds,
    fetchFriends, searchUsers, sendRequest, fetchPendingRequests, fetchSentRequests,
    acceptRequest, rejectRequest, removeFriend, setOnline,
  }
})
