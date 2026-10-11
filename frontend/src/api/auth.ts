import apiClient from './client'
import type { AuthResponse, TokenResponse } from '../types'

export function login(username: string, password: string): Promise<AuthResponse> {
  return apiClient.post('/auth/login', { username, password }).then((r) => r.data)
}

export function register(username: string, email: string, password: string): Promise<AuthResponse> {
  return apiClient.post('/auth/register', { username, email, password }).then((r) => r.data)
}

export function refreshToken(token: string): Promise<TokenResponse> {
  return apiClient.post('/auth/refresh', { refresh_token: token }).then((r) => r.data)
}
