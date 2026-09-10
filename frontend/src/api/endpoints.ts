import { http } from './client'

export interface Me {
  id: number
  phone: string
  display_name: string | null
  email: string | null
  avatar_url: string | null
  timezone: string
  profile_completed: boolean
  birth_jyear: number | null
  birth_jmonth: number | null
  birth_jday: number | null
  birth_gregorian: string | null
}

export interface PublicUser {
  id: number
  display_name: string | null
  avatar_url: string | null
}

export interface OwnItem {
  id: number
  title: string
  description: string | null
  url: string | null
  image_url: string | null
  price: string | null
  position: number
}

export interface FriendItem extends OwnItem {
  is_claimed: boolean
  claimed_by_me: boolean
}

export interface FriendRequest {
  id: number
  status: string
  requester: PublicUser
}

export interface AppNotification {
  id: number
  type: string
  payload: Record<string, unknown>
  created_at: string
  read_at: string | null
}

export const authApi = {
  requestOtp: (phone: string) => http.post('/auth/otp/request', { phone }),
  verifyOtp: (phone: string, code: string) =>
    http.post<{ is_new: boolean; profile_completed: boolean }>('/auth/otp/verify', { phone, code }),
  logout: () => http.post('/auth/logout'),
  me: () => http.get<Me>('/auth/me'),
}

export const userApi = {
  updateProfile: (body: Record<string, unknown>) => http.patch<Me>('/users/me', body),
}

export const inviteApi = {
  mine: () => http.get<{ code: string; url: string }>('/invites/me'),
  regenerate: () => http.post<{ code: string; url: string }>('/invites/regenerate'),
  preview: (code: string) => http.get<{ inviter: PublicUser }>(`/i/${code}`),
  accept: (code: string) => http.post<{ status: string; inviter: PublicUser }>(`/invites/${code}/accept`),
}

export const friendApi = {
  list: () => http.get<PublicUser[]>('/friends'),
  requests: () => http.get<FriendRequest[]>('/friends/requests'),
  respond: (id: number, accept: boolean) =>
    http.post<FriendRequest>(`/friends/requests/${id}/respond`, { accept }),
  unfriend: (id: number) => http.delete(`/friends/${id}`),
}

export const wishlistApi = {
  mine: () => http.get<OwnItem[]>('/wishlists/me'),
  create: (body: Partial<OwnItem>) => http.post<OwnItem>('/wishlists/items', body),
  update: (id: number, body: Partial<OwnItem>) => http.patch<OwnItem>(`/wishlists/items/${id}`, body),
  remove: (id: number) => http.delete(`/wishlists/items/${id}`),
  ofFriend: (userId: number) => http.get<FriendItem[]>(`/wishlists/${userId}`),
  claim: (id: number) => http.post(`/wishlists/items/${id}/claim`),
  unclaim: (id: number) => http.delete(`/wishlists/items/${id}/claim`),
}

export const notifyApi = {
  list: () => http.get<AppNotification[]>('/notifications'),
  markRead: (id: number) => http.post(`/notifications/${id}/read`),
  getPrefs: () => http.get<{ web_push: boolean; email: boolean }>('/notifications/prefs'),
  setPrefs: (body: { web_push: boolean; email: boolean }) =>
    http.put('/notifications/prefs', body),
  subscribe: (sub: PushSubscriptionJSON) => http.post('/push/subscribe', sub),
  unsubscribe: (sub: PushSubscriptionJSON) => http.post('/push/unsubscribe', sub),
}
