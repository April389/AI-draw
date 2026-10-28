/**
 * Pinia Store 测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useDiagramStore } from '@/stores/diagram'
import type { DiagramData, ExcalidrawElement } from '@/types'

// Mock api 模块
vi.mock('@/api', () => ({
  api: {
    generateDiagram: vi.fn(),
    healthCheck: vi.fn()
  }
}))

import { api } from '@/api'

const mockDiagram: DiagramData = {
  diagram_type: 'flowchart',
  title: '测试图',
  nodes: [
    { id: 'n1', label: '节点1' },
    { id: 'n2', label: '节点2' }
  ],
  edges: [
    { id: 'e1', source: 'n1', target: 'n2' }
  ]
}

const mockElements: ExcalidrawElement[] = [
  { id: 'el1', type: 'rectangle', x: 100, y: 100, width: 140, height: 60 } as any
]

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
})

describe('useDiagramStore', () => {
  it('初始状态正确', () => {
    const store = useDiagramStore()
    expect(store.currentDiagram).toBeNull()
    expect(store.excalidrawElements).toEqual([])
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.hasDiagram).toBe(false)
    expect(store.nodeCount).toBe(0)
    expect(store.edgeCount).toBe(0)
  })

  it('成功生成图表', async () => {
    const store = useDiagramStore()
    ;(api.generateDiagram as any).mockResolvedValue({
      success: true,
      diagram: mockDiagram,
      excalidraw_elements: mockElements
    })

    await store.generate('创建流程图')

    expect(store.isLoading).toBe(false)
    expect(store.currentDiagram).toEqual(mockDiagram)
    expect(store.excalidrawElements).toEqual(mockElements)
    expect(store.hasDiagram).toBe(true)
    expect(store.nodeCount).toBe(2)
    expect(store.edgeCount).toBe(1)
    expect(store.error).toBeNull()
  })

  it('空prompt不生成', async () => {
    const store = useDiagramStore()
    const result = await store.generate('')

    expect(result).toBeNull()
    expect(store.error).toBe('请输入图表描述')
    expect(api.generateDiagram).not.toHaveBeenCalled()
  })

  it('API失败时设置错误', async () => {
    const store = useDiagramStore()
    ;(api.generateDiagram as any).mockResolvedValue({
      success: false,
      error: 'LLM调用失败',
      diagram: null,
      excalidraw_elements: null
    })

    await store.generate('测试')

    expect(store.error).toBe('LLM调用失败')
    expect(store.currentDiagram).toBeNull()
  })

  it('网络异常时设置错误', async () => {
    const store = useDiagramStore()
    ;(api.generateDiagram as any).mockRejectedValue(new Error('Network Error'))

    await store.generate('测试')

    expect(store.error).toBe('Network Error')
    expect(store.isLoading).toBe(false)
  })

  it('清空图表', async () => {
    const store = useDiagramStore()
    ;(api.generateDiagram as any).mockResolvedValue({
      success: true,
      diagram: mockDiagram,
      excalidraw_elements: mockElements
    })
    await store.generate('测试')

    store.clearDiagram()
    expect(store.currentDiagram).toBeNull()
    expect(store.excalidrawElements).toEqual([])
    expect(store.error).toBeNull()
  })

  it('记录生成历史', async () => {
    const store = useDiagramStore()
    ;(api.generateDiagram as any).mockResolvedValue({
      success: true,
      diagram: mockDiagram,
      excalidraw_elements: mockElements
    })

    await store.generate('第一次')
    await store.generate('第二次')

    expect(store.generationHistory.length).toBe(2)
    expect(store.generationHistory[0].prompt).toBe('第二次')
    expect(store.generationHistory[1].prompt).toBe('第一次')
  })

  it('历史记录不超过10条', async () => {
    const store = useDiagramStore()
    ;(api.generateDiagram as any).mockResolvedValue({
      success: true,
      diagram: mockDiagram,
      excalidraw_elements: mockElements
    })

    for (let i = 0; i < 12; i++) {
      await store.generate(`第${i}次`)
    }

    expect(store.generationHistory.length).toBe(10)
  })

  it('从历史恢复', async () => {
    const store = useDiagramStore()
    ;(api.generateDiagram as any).mockResolvedValue({
      success: true,
      diagram: mockDiagram,
      excalidraw_elements: mockElements
    })
    await store.generate('测试')

    const entry = store.generationHistory[0]
    store.clearDiagram()
    expect(store.currentDiagram).toBeNull()

    store.restoreFromHistory(entry)
    expect(store.currentDiagram).toEqual(mockDiagram)
    expect(store.excalidrawElements).toEqual(mockElements)
    expect(store.currentPrompt).toBe('测试')
  })
})
