export function formatTime(iso?: string): string {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('zh-CN')
}

export function genNodeId(type: string): string {
  return `${type}_${Math.random().toString(36).slice(2, 8)}`
}

export function statusColor(status?: string): string {
  switch (status) {
    case 'succeeded': return '#52c41a'
    case 'failed': return '#ff4d4f'
    case 'running': return '#faad14'
    default: return '#d9d9d9'
  }
}
