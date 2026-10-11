import apiClient from './client'
import type { Message, MessageHistoryResponse } from '../types'

export function getMessageHistory(
  friendId: number,
  cursor?: number,
  limit = 50
): Promise<MessageHistoryResponse> {
  return apiClient
    .get(`/messages/${friendId}`, { params: cursor ? { cursor, limit } : { limit } })
    .then((r) => r.data)
}

export function sendMessageRest(
  receiver_id: number,
  message_type: string,
  content?: string,
  image_url?: string,
  file_url?: string,
  file_name?: string,
): Promise<Message> {
  return apiClient
    .post('/messages/send', { receiver_id, message_type, content, image_url, file_url, file_name })
    .then((r) => r.data)
}

export function deleteMessages(friendId: number): Promise<{ ok: boolean; deleted_count: number }> {
  return apiClient.delete(`/messages/${friendId}`).then((r) => r.data)
}
