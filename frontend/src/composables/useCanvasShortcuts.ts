import { useVueFlow } from '@vue-flow/core'
import { message } from 'ant-design-vue'
import { useWorkflowStore } from '@/stores/workflow'
import { genNodeId } from '@/utils/format'

// Nodes that must always exist in a workflow — never deletable via shortcuts.
const PROTECTED_TYPES = new Set(['start', 'end'])
const MAX_HISTORY = 50
const PASTE_OFFSET = 32

type Snapshot = { nodes: any[]; edges: any[] }

const clone = <T>(v: T): T => JSON.parse(JSON.stringify(v))

/**
 * Keyboard shortcuts for the workflow canvas:
 *   Delete/Backspace  delete selected nodes + edges (start/end protected)
 *   Ctrl/Cmd+C / +V   copy / paste nodes
 *   Ctrl/Cmd+D        duplicate selected nodes
 *   Ctrl/Cmd+A        select all nodes        Esc  deselect / close config panel
 *   Ctrl/Cmd+Z        undo    Ctrl/Cmd+Shift+Z / Ctrl+Y  redo
 *
 * Undo/redo is snapshot-based: call `snapshot()` BEFORE any structural change
 * (delete / paste / drag-stop / connect / add) and the stack handles the rest.
 */
export function useCanvasShortcuts() {
  const store = useWorkflowStore()
  const {
    getSelectedNodes,
    getSelectedEdges,
    getNodes,
    removeNodes,
    removeEdges,
    addNodes,
    addSelectedNodes,
    removeSelectedElements,
  } = useVueFlow()

  let clipboard: any[] = []
  const undoStack: Snapshot[] = []
  const redoStack: Snapshot[] = []

  function currentSnapshot(): Snapshot {
    return { nodes: clone(store.nodes), edges: clone(store.edges) }
  }

  /** Push the current graph onto the undo stack (call before a mutation). */
  function snapshot() {
    undoStack.push(currentSnapshot())
    if (undoStack.length > MAX_HISTORY) undoStack.shift()
    redoStack.length = 0
  }

  function restore(snap: Snapshot) {
    store.nodes = clone(snap.nodes)
    store.edges = clone(snap.edges)
    // Drop selection state pointing at a node that may no longer exist.
    if (store.selectedNodeId && !store.nodes.some((n) => n.id === store.selectedNodeId)) {
      store.selectNode(null)
    }
  }

  function undo() {
    const snap = undoStack.pop()
    if (!snap) return
    redoStack.push(currentSnapshot())
    restore(snap)
  }

  function redo() {
    const snap = redoStack.pop()
    if (!snap) return
    undoStack.push(currentSnapshot())
    restore(snap)
  }

  // ---- operations ----
  function deleteSelection() {
    const sel = getSelectedNodes.value
    const edges = getSelectedEdges.value
    const deletable = sel.filter((n) => !PROTECTED_TYPES.has(n.type as string))
    const blocked = sel.length - deletable.length

    if (!deletable.length && !edges.length) {
      if (blocked) message.info('开始/结束节点不可删除')
      return
    }
    snapshot()
    if (deletable.length) removeNodes(deletable, true) // also removes connected edges
    if (edges.length) removeEdges(edges)
    if (blocked) message.info(`已删除选中节点；开始/结束节点不可删除`)

    if (store.selectedNodeId && !store.nodes.some((n) => n.id === store.selectedNodeId)) {
      store.selectNode(null)
    }
  }

  function copySelection() {
    const sel = getSelectedNodes.value.filter((n) => !PROTECTED_TYPES.has(n.type as string))
    clipboard = sel.map((n) => clone({ type: n.type, position: n.position, data: n.data }))
  }

  function pasteNodes(source?: any[]) {
    const src = source ?? clipboard
    if (!src.length) return
    snapshot()
    const created = src.map((n) => {
      const { _status, ...data } = n.data || {}
      return {
        id: genNodeId(n.type),
        type: n.type,
        position: { x: (n.position?.x ?? 0) + PASTE_OFFSET, y: (n.position?.y ?? 0) + PASTE_OFFSET },
        data: clone(data),
      }
    })
    addNodes(created)
    // Select the freshly pasted nodes.
    removeSelectedElements()
    addSelectedNodes(created as any)
    if (created.length === 1) store.selectNode(created[0].id)
  }

  function duplicateSelection() {
    const sel = getSelectedNodes.value.filter((n) => !PROTECTED_TYPES.has(n.type as string))
    if (!sel.length) return
    pasteNodes(sel.map((n) => clone({ type: n.type, position: n.position, data: n.data })))
  }

  function selectAll() {
    addSelectedNodes(getNodes.value as any)
  }

  function deselect() {
    removeSelectedElements()
    store.selectNode(null)
  }

  // ---- key handling ----
  function isEditableTarget(t: EventTarget | null): boolean {
    const el = t as HTMLElement | null
    if (!el || !el.closest) return false
    return !!el.closest(
      'input, textarea, select, [contenteditable], [contenteditable="true"], .ant-select, .monaco-editor, .cm-editor',
    )
  }

  function onKeyDown(e: KeyboardEvent) {
    // Never hijack typing inside form controls / code editors.
    if (isEditableTarget(e.target)) return

    const mod = e.ctrlKey || e.metaKey
    const key = e.key

    // Delete / Backspace
    if (!mod && (key === 'Delete' || key === 'Backspace')) {
      e.preventDefault()
      deleteSelection()
      return
    }
    // Esc
    if (!mod && key === 'Escape') {
      deselect()
      return
    }
    if (!mod) return

    const lower = key.toLowerCase()
    switch (lower) {
      case 'c':
        copySelection()
        break
      case 'v':
        e.preventDefault()
        pasteNodes()
        break
      case 'd':
        e.preventDefault()
        duplicateSelection()
        break
      case 'a':
        e.preventDefault()
        selectAll()
        break
      case 'z':
        e.preventDefault()
        if (e.shiftKey) redo()
        else undo()
        break
      case 'y':
        e.preventDefault()
        redo()
        break
      default:
        break
    }
  }

  function register() {
    window.addEventListener('keydown', onKeyDown)
  }
  function unregister() {
    window.removeEventListener('keydown', onKeyDown)
  }

  return { register, unregister, snapshot }
}
