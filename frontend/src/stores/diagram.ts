/**
 * 图表状态管理（Pinia Store）
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  DiagramData,
  ExcalidrawElement,
  GenerateResponse,
  DiagramType
} from '@/types'
import { api } from '@/api'

export interface HistoryEntry {
  timestamp: number
  prompt: string
  diagram: DiagramData
  excalidrawElements: ExcalidrawElement[]
}

export const useDiagramStore = defineStore('diagram', () => {
  // 状态
  const currentPrompt = ref('')
  const currentDiagram = ref<DiagramData | null>(null)
  const excalidrawElements = ref<ExcalidrawElement[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastGeneratedAt = ref<number | null>(null)
  const generationHistory = ref<HistoryEntry[]>([])
  const selectedDiagramType = ref<DiagramType | null>(null)

  // 计算属性
  const hasDiagram = computed(() => currentDiagram.value !== null)
  const nodeCount = computed(() => currentDiagram.value?.nodes.length ?? 0)
  const edgeCount = computed(() => currentDiagram.value?.edges?.length ?? 0)

  // 操作
  async function generate(prompt: string, diagramType?: DiagramType | null): Promise<GenerateResponse | null> {
    if (!prompt.trim()) {
      error.value = '请输入图表描述'
      return null
    }

    currentPrompt.value = prompt
    if (diagramType !== undefined) {
      selectedDiagramType.value = diagramType
    }
    isLoading.value = true
    error.value = null

    try {
      const response = await api.generateDiagram({
        prompt,
        diagram_type: diagramType ?? null
      })

      if (response.success && response.diagram) {
        currentDiagram.value = response.diagram
        excalidrawElements.value = response.excalidraw_elements || []
        lastGeneratedAt.value = Date.now()

        // 添加到历史
        generationHistory.value.unshift({
          timestamp: Date.now(),
          prompt,
          diagram: response.diagram,
          excalidrawElements: response.excalidraw_elements || []
        })
        // 只保留最近10条
        if (generationHistory.value.length > 10) {
          generationHistory.value = generationHistory.value.slice(0, 10)
        }
      } else {
        error.value = response.error || '生成失败'
      }

      return response
    } catch (e: any) {
      error.value = e?.message || '请求失败，请检查后端服务是否可用'
      return null
    } finally {
      isLoading.value = false
    }
  }

  function clearDiagram() {
    currentDiagram.value = null
    excalidrawElements.value = []
    error.value = null
  }

  function restoreFromHistory(entry: HistoryEntry) {
    currentDiagram.value = entry.diagram
    excalidrawElements.value = entry.excalidrawElements
    currentPrompt.value = entry.prompt
    lastGeneratedAt.value = entry.timestamp
  }

  function updateElements(elements: ExcalidrawElement[]) {
    excalidrawElements.value = elements
  }

  return {
    // 状态
    currentPrompt,
    currentDiagram,
    excalidrawElements,
    isLoading,
    error,
    lastGeneratedAt,
    generationHistory,
    selectedDiagramType,
    // 计算属性
    hasDiagram,
    nodeCount,
    edgeCount,
    // 操作
    generate,
    clearDiagram,
    restoreFromHistory,
    updateElements
  }
})
