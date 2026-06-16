/**
 * AgentFlow 设计系统 —— 唯一 Source of Truth（与 global.css 的 :root 变量保持一致）。
 * - afTheme：注入 Ant Design Vue 的 <a-config-provider :theme>。
 * - NODE_META：节点类型 → 强调色 + 图标，供 NodePanel / 各 Node 卡片复用。
 */
import type { Component } from 'vue'
import {
  PlayCircleOutlined,
  StopOutlined,
  RobotOutlined,
  BookOutlined,
  ToolOutlined,
  CodeOutlined,
  GlobalOutlined,
  BranchesOutlined,
  RetweetOutlined,
  FileTextOutlined,
  MergeCellsOutlined,
  ApiOutlined,
} from '@ant-design/icons-vue'

/** 设计 token —— 颜色（与 global.css :root 镜像） */
export const TOKENS = {
  primary: '#6366F1',
  primaryHover: '#818CF8',
  primaryActive: '#4F46E5',
  success: '#22C55E',
  warning: '#F59E0B',
  danger: '#EF4444',
  text: '#0F172A',
  textSecondary: '#475569',
  textTertiary: '#94A3B8',
  border: '#E2E8F0',
  bg: '#F8FAFC',
  surface: '#FFFFFF',
  radius: 8,
} as const

/** Ant Design Vue 主题 token —— 镜像设计系统 */
export const afTheme = {
  token: {
    colorPrimary: TOKENS.primary,
    colorSuccess: TOKENS.success,
    colorWarning: TOKENS.warning,
    colorError: TOKENS.danger,
    colorInfo: TOKENS.primary,
    colorText: TOKENS.text,
    colorTextSecondary: TOKENS.textSecondary,
    colorBorder: TOKENS.border,
    colorBgLayout: TOKENS.bg,
    borderRadius: TOKENS.radius,
    borderRadiusLG: 12,
    borderRadiusSM: 6,
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif",
    fontSize: 14,
    controlHeight: 36,
    wireframe: false,
  },
  components: {
    Menu: {
      itemBorderRadius: 8,
      itemSelectedBg: '#EEF2FF',
      itemSelectedColor: TOKENS.primary,
      itemHeight: 42,
    },
    Button: { primaryShadow: '0 1px 2px rgba(99,102,241,.25)' },
    Card: { borderRadiusLG: 12 },
    Table: { headerBg: '#F8FAFC', headerColor: TOKENS.textSecondary, rowHoverBg: '#F8FAFC' },
  },
}

/** 节点类型元信息：强调色（画布头部/色条/图标）+ 图标组件 */
export interface NodeMeta {
  color: string
  icon: Component
}

export const NODE_META: Record<string, NodeMeta> = {
  start: { color: '#22C55E', icon: PlayCircleOutlined },
  end: { color: '#64748B', icon: StopOutlined },
  llm: { color: '#6366F1', icon: RobotOutlined },
  knowledge_retrieval: { color: '#06B6D4', icon: BookOutlined },
  tool: { color: '#F59E0B', icon: ToolOutlined },
  code: { color: '#EC4899', icon: CodeOutlined },
  http_request: { color: '#3B82F6', icon: GlobalOutlined },
  if_else: { color: '#A855F7', icon: BranchesOutlined },
  iteration: { color: '#14B8A6', icon: RetweetOutlined },
  template: { color: '#8B5CF6', icon: FileTextOutlined },
  aggregator: { color: '#F97316', icon: MergeCellsOutlined },
}

const FALLBACK_META: NodeMeta = { color: TOKENS.primary, icon: ApiOutlined }

/** 安全取节点元信息（未知类型回退到主色 + 通用图标） */
export function nodeMeta(type?: string): NodeMeta {
  return (type && NODE_META[type]) || FALLBACK_META
}
