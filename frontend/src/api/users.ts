import apiClient from './client'
import type { User, UserSearchResult } from '../types'

export function getMe(): Promise<User> {
  return apiClient.get('/users/me').then((r) => r.data)
}

export function searchUsers(q: string, limit = 20): Promise<UserSearchResult[]> {
  return apiClient.get('/users/search', { params: { q, limit } }).then((r) => r.data)
}
