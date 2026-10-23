import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as subjectService from '../services/subjectService'

export function useSubjects() {
  return useQuery({ queryKey: ['subjects'], queryFn: subjectService.getSubjects })
}

export function useSubject(id: string) {
  return useQuery({ queryKey: ['subjects', id], queryFn: () => subjectService.getSubject(id) })
}

export function useCreateSubject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: subjectService.createSubject,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['subjects'] }),
  })
}

export function useDocuments(subjectId: string, enabled = true) {
  return useQuery({
    queryKey: ['documents', subjectId],
    queryFn: () => subjectService.getDocuments(subjectId),
    enabled,
  })
}

export function useUploadDocument(subjectId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => subjectService.uploadDocument(subjectId, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', subjectId] }),
  })
}
