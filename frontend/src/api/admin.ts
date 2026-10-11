import apiClient from "./client"
import type { AdminDashboard, AdminUser, AdminSettings, AdminUserListResponse, AdminMessageListResponse } from "../types"

export function getDashboard(): Promise<AdminDashboard> {
  return apiClient.get("/admin/dashboard").then(r => r.data)
}
export function listUsers(page = 1, pageSize = 20, search?: string): Promise<AdminUserListResponse> {
  return apiClient.get("/admin/users", { params: { page, page_size: pageSize, search } }).then(r => r.data)
}
export function banUser(userId: number): Promise<AdminUser> {
  return apiClient.patch(`/admin/users/${userId}/ban`).then(r => r.data)
}
export function unbanUser(userId: number): Promise<AdminUser> {
  return apiClient.patch(`/admin/users/${userId}/unban`).then(r => r.data)
}
export function toggleAdmin(userId: number): Promise<AdminUser> {
  return apiClient.patch(`/admin/users/${userId}/toggle-admin`).then(r => r.data)
}
export function deleteUser(userId: number): Promise<{ ok: boolean }> {
  return apiClient.delete(`/admin/users/${userId}`).then(r => r.data)
}
export function listMessages(page = 1, pageSize = 20, search?: string, sender?: string, receiver?: string): Promise<AdminMessageListResponse> {
  return apiClient.get("/admin/messages", { params: { page, page_size: pageSize, search, sender, receiver } }).then(r => r.data)
}
export function deleteMessage(messageId: number): Promise<{ ok: boolean }> {
  return apiClient.delete(`/admin/messages/${messageId}`).then(r => r.data)
}
export function getSettings(): Promise<AdminSettings> {
  return apiClient.get("/admin/settings").then(r => r.data)
}
export function updateSettings(data: Partial<AdminSettings>): Promise<AdminSettings> {
  return apiClient.patch("/admin/settings", data).then(r => r.data)
}

