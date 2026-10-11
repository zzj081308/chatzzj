export interface User {
  id: number
  username: string
  email: string
  avatar_url: string | null
  is_online: boolean
  is_admin: boolean
  is_banned: boolean
  last_seen_at: string | null
  created_at: string
}

export interface UserSearchResult {
  id: number
  username: string
  avatar_url: string | null
  is_online: boolean
}

export interface Message {
  id: number
  sender_id: number
  receiver_id: number
  message_type: 'text' | 'image' | 'file'
  content: string | null
  image_url: string | null
  file_url: string | null
  file_name: string | null
  is_read: boolean
  created_at: string
  client_msg_id?: string
  pending?: boolean
  failed?: boolean
}

export interface FriendRequest {
  id: number
  sender_id: number
  receiver_id: number
  status: 'pending' | 'accepted' | 'rejected'
  message: string | null
  sender?: UserSearchResult
  receiver?: UserSearchResult
  created_at: string
  updated_at: string
}

export interface Friend {
  id: number
  username: string
  avatar_url: string | null
  is_online: boolean
  last_message: string | null
  last_message_time: string | null
  unread_count: number
  is_ai?: boolean
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface MessageHistoryResponse {
  messages: Message[]
  has_more: boolean
  next_cursor: number | null
}

// WebSocket message types
export interface WsMessage {
  type: string
  [key: string]: any
}

export interface AdminDashboard {
  total_users: number; total_messages: number; online_users: number
  banned_users: number; admin_users: number; total_friendships: number
  pending_requests: number; pending_appeals: number; ai_enabled: boolean
  messages_last_24h: number; new_users_last_24h: number
}

export interface AdminUser {
  id: number; username: string; email: string
  avatar_url: string | null; is_online: boolean; is_ai: boolean
  is_admin: boolean; is_banned: boolean
  last_seen_at: string | null; created_at: string
}

export interface AdminMessage {
  id: number; sender_id: number; receiver_id: number
  message_type: string; content: string | null
  image_url: string | null; file_url: string | null
  file_name: string | null; is_read: boolean; created_at: string
  sender_username: string | null; receiver_username: string | null
}

export interface AdminSettings {
  ai_assistant_enabled: boolean; ai_assistant_username: string
  ai_model: string; ai_system_prompt: string; app_name: string
  access_token_expire_minutes: number; refresh_token_expire_days: number
  max_upload_size: number; max_file_size: number
}

export interface AdminUserListResponse {
  users: AdminUser[]; total: number; page: number; page_size: number
}

export interface AdminMessageListResponse {
  messages: AdminMessage[]; total: number; page: number; page_size: number
}
export interface Appeal {
  id: number
  user_id: number
  username: string
  email: string
  reason: string
  status: string
  admin_response: string | null
  admin_id: number | null
  created_at: string
  updated_at: string
}
