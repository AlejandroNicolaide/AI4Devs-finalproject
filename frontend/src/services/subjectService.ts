import api from './api'
import type { Document, Subject, UploadedDocument } from '../types'

export async function getSubjects(): Promise<Subject[]> {
  return (await api.get<Subject[]>('/subjects')).data
}

export async function getSubject(id: string): Promise<Subject> {
  return (await api.get<Subject>(`/subjects/${id}`)).data
}

export async function createSubject(data: { name: string; description?: string }): Promise<Subject> {
  return (await api.post<Subject>('/subjects', data)).data
}

export async function getDocuments(subjectId: string): Promise<Document[]> {
  return (await api.get<Document[]>(`/subjects/${subjectId}/documents`)).data
}

export async function uploadDocument(subjectId: string, file: File): Promise<UploadedDocument> {
  const form = new FormData()
  form.append('file', file)
  return (await api.post<UploadedDocument>(`/subjects/${subjectId}/documents`, form)).data
}
