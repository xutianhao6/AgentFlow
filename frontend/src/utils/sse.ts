// SSE streaming via fetch (supports POST body, which EventSource cannot).
import { API_BASE } from '@/api/request'

export interface SSEEvent {
  event: string
  data: any
}

export async function postSSE(
  path: string,
  body: any,
  onEvent: (evt: SSEEvent) => void,
): Promise<void> {
  const userId = localStorage.getItem('user_id') || 'default'
  const resp = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-User-Id': userId },
    body: JSON.stringify(body),
  })
  if (!resp.body) return
  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() || ''
    for (const block of blocks) {
      let event = 'message'
      let data = ''
      for (const line of block.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim()
        else if (line.startsWith('data:')) data += line.slice(5).trim()
      }
      if (data) {
        try {
          onEvent({ event, data: JSON.parse(data) })
        } catch {
          onEvent({ event, data })
        }
      }
    }
  }
}
