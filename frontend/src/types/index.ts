/**
 * 图表数据类型定义
 * 与后端schemas.py保持一致
 */

export type DiagramType = 'flowchart' | 'architecture' | 'sequence' | 'mindmap' | 'state' | 'class' | 'generic'

export interface Node {
  id: string
  label: string
  type: string  // rectangle/ellipse/diamond/cylinder/parallelogram/cloud/hexagon
  x?: number | null
  y?: number | null
  width?: number | null
  height?: number | null
  color?: string | null
  stroke_color?: string | null
}

export interface Edge {
  id: string
  source: string
  target: string
  label?: string | null
  style?: 'solid' | 'dashed' | 'dotted'
  arrow?: 'none' | 'start' | 'end' | 'both'
}

export interface DiagramData {
  diagram_type: DiagramType
  title?: string | null
  nodes: Node[]
  edges?: Edge[]
  metadata?: Record<string, any> | null
}

export interface ExcalidrawElement {
  id: string
  type: string
  x: number
  y: number
  width: number
  height: number
  angle: number
  strokeColor: string
  backgroundColor: string
  fillStyle: string
  strokeWidth: number
  strokeStyle: number
  roughness: number
  opacity: number
  groupIds: string[]
  frameId: string | null
  roundness: any
  seed: number
  version: number
  versionNonce: number
  isDeleted: boolean
  boundElements: any
  updated: number
  link: string | null
  locked: boolean
  // 箭头特有
  points?: [number, number][]
  startArrowhead?: string | null
  endArrowhead?: string | null
  // 文本特有
  text?: string
  fontSize?: number
  fontFamily?: number
  textAlign?: string
  verticalAlign?: string
  baseline?: number
  containerId?: string | null
  originalText?: string
  lineHeight?: number
}

export interface GenerateRequest {
  prompt: string
  diagram_type?: DiagramType | null
  stream?: boolean
}

export interface GenerateResponse {
  success: boolean
  diagram?: DiagramData | null
  excalidraw_elements?: ExcalidrawElement[] | null
  error?: string | null
}

export interface ValidateResponse {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export interface DiagramTypeInfo {
  value: DiagramType
  label: string
  description: string
}

export const DIAGRAM_TYPES: DiagramTypeInfo[] = [
  { value: 'flowchart', label: '流程图', description: '步骤、决策、分支的有序流程' },
  { value: 'architecture', label: '架构图', description: '系统组件及其关系' },
  { value: 'sequence', label: '时序图', description: '对象间的消息交互时序' },
  { value: 'mindmap', label: '思维导图', description: '层级化的概念结构' },
  { value: 'state', label: '状态图', description: '对象的状态转换' },
  { value: 'class', label: '类图', description: '面向对象的类结构' },
  { value: 'generic', label: '通用图', description: '不受类型限制的自由图表' }
]
