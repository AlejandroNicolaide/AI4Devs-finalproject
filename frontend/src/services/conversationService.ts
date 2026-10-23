import api from './api'
import type { Conversation, Message } from '../types'

export async function getConversations(subjectId?: string): Promise<Conversation[]> {
  const res = await api.get<Conversation[]>('/conversations', {
    params: subjectId ? { subject_id: subjectId } : undefined,
  })
  return res.data
}

export async function getMessages(conversationId: string): Promise<Message[]> {
  return (await api.get<Message[]>(`/conversations/${conversationId}/messages`)).data
}

export async function deleteConversation(conversationId: string): Promise<void> {
  await api.delete(`/conversations/${conversationId}`)
}
