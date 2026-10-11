import apiClient from "./client"
import type { Appeal } from "../types"

export function submitAppeal(username: string, password: string, reason: string): Promise<Appeal> {
  return apiClient.post("/appeals/submit", { username, password, reason }).then(r => r.data)
}

export function getMyAppeals(): Promise<Appeal[]> {
  return apiClient.get("/appeals/my").then(r => r.data)
}

export function getAdminAppeals(status?: string): Promise<Appeal[]> {
  return apiClient.get("/appeals/admin/all", { params: status ? { status } : {} }).then(r => r.data)
}

export function approveAppeal(appealId: number): Promise<Appeal> {
  return apiClient.patch(`/appeals/admin/${appealId}/approve`).then(r => r.data)
}

export function rejectAppeal(appealId: number, response: string): Promise<Appeal> {
  return apiClient.patch(`/appeals/admin/${appealId}/reject`, { response }).then(r => r.data)
}
