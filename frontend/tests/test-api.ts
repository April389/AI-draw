/**
 * API客户端测试（使用Mock）
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock axios
vi.mock('axios', () => {
  return {
    default: {
      create: () => ({
        post: vi.fn(),
        get: vi.fn(),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      })
    }
  }
})

import { api } from '@/api'

describe('API客户端结构', () => {
  it('包含所有必要方法', () => {
    expect(api.generateDiagram).toBeDefined()
    expect(api.validateDiagram).toBeDefined()
    expect(api.convertToExcalidraw).toBeDefined()
    expect(api.getDiagramTypes).toBeDefined()
    expect(api.healthCheck).toBeDefined()
  })

  it('generateDiagram接受prompt和diagram_type', async () => {
    const mockClient = (api as any).client
    mockClient.post.mockResolvedValue({
      data: { success: true, diagram: null }
    })

    await api.generateDiagram({
      prompt: '创建流程图',
      diagram_type: 'flowchart'
    })

    expect(mockClient.post).toHaveBeenCalledWith(
      '/api/generate',
      { prompt: '创建流程图', diagram_type: 'flowchart', stream: undefined }
    )
  })

  it('healthCheck返回status和version', async () => {
    const mockClient = (api as any).client
    mockClient.get.mockResolvedValue({
      data: { status: 'ok', version: '1.0.0' }
    })

    const result = await api.healthCheck()
    expect(result.status).toBe('ok')
    expect(result.version).toBe('1.0.0')
  })
})
