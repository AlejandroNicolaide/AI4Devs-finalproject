export type Role = 'teacher' | 'student'

export interface User {
  id: string
  email: string
  role: Role
}

export interface Subject {
  id: string
  name: string
  description: string | null
  teacher_id: string
}

export interface Document {
  id: string
  filename: string
  created_at: string
}

export interface UploadedDocument {
  id: string
  filename: string
  chunks_created: number
}

export interface Conversation {
  id: string
  subject_id: string
  created_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
  sources?: Source[]
}

export interface Source {
  chunk_id: string
  document_id: string
  filename: string
  fragment: string
}

export interface ChatResponse {
  conversation_id: string
  answer: string
  sources: Source[]
}
