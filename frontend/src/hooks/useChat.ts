import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as chatService from '../services/chatService'
import * as conversationService from '../services/conversationService'

export function useSendMessage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (v: { subjectId: string; message: string; conversationId?: string }) =>
      chatService.sendMessage(v.subjectId, v.message, v.conversationId),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['conversations'] })
      // sin esto, la 2.ª pregunta de una conversación ya abierta no aparece (la clave no cambia, no hay refetch)
      qc.invalidateQueries({ queryKey: ['messages', res.conversation_id] })
    },
  })
}

export function useConversations() {
  return useQuery({
    queryKey: ['conversations'],
    queryFn: () => conversationService.getConversations(),
  })
}

export function useConversationMessages(conversationId: string | undefined) {
  return useQuery({
    queryKey: ['messages', conversationId],
    queryFn: () => conversationService.getMessages(conversationId!),
    enabled: !!conversationId,
  })
}

export function useDeleteConversation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: conversationService.deleteConversation,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['conversations'] }),
  })
}
