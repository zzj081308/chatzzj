import apiClient from './client'
import type { Friend, FriendRequest } from '../types'

export function getFriends(): Promise<Friend[]> {
  return apiClient.get('/friends').then((r) => r.data)
}

export function sendFriendRequest(receiver_id: number, message?: string): Promise<FriendRequest> {
  return apiClient.post('/friends/requests', { receiver_id, message }).then((r) => r.data)
}

export function getPendingRequests(): Promise<FriendRequest[]> {
  return apiClient.get('/friends/requests/pending').then((r) => r.data)
}

export function getSentRequests(): Promise<FriendRequest[]> {
  return apiClient.get('/friends/requests/sent').then((r) => r.data)
}

export function acceptRequest(requestId: number): Promise<FriendRequest> {
  return apiClient.patch(`/friends/requests/${requestId}/accept`).then((r) => r.data)
}

export function rejectRequest(requestId: number): Promise<FriendRequest> {
  return apiClient.patch(`/friends/requests/${requestId}/reject`).then((r) => r.data)
}

export function removeFriend(friendId: number): Promise<void> {
  return apiClient.delete(`/friends/${friendId}`)
}
