import api from './api'
import type { ChatResponse } from '../types'

export async function sendMessage(
  subject_id: string,
  message: string,
  conversation_id?: string,
): Promise<ChatResponse> {
  const res = await api.post<ChatResponse>('/chat', { subject_id, message, conversation_id })
  return res.data
}
