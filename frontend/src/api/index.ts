/**
 * API调用层
 * 封装与后端的所有HTTP通信
 */
import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  GenerateRequest,
  GenerateResponse,
  DiagramData,
  ValidateResponse,
  DiagramTypeInfo
} from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

class ApiClient {
  private client: AxiosInstance

  constructor(baseURL: string = BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 120000, // 2分钟超时（LLM生成可能较慢）
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const message = error.response?.data 
          ? JSON.stringify(error.response.data) 
          : error.message
        console.error(`[API Error] ${error.config?.url}:`, message)
        return Promise.reject(error)
      }
    )
  }

  /**
   * 生成图表
   */
  async generateDiagram(request: GenerateRequest): Promise<GenerateResponse> {
    const response = await this.client.post<GenerateResponse>('/api/generate', request)
    return response.data
  }

  /**
   * 校验图数据
   */
  async validateDiagram(diagram: DiagramData): Promise<ValidateResponse> {
    const response = await this.client.post<ValidateResponse>('/api/validate', { diagram })
    return response.data
  }

  /**
   * 转换为Excalidraw元素
   */
  async convertToExcalidraw(diagram: DiagramData): Promise<{ success: boolean; elements: any[]; count: number }> {
    const response = await this.client.post('/api/convert', diagram)
    return response.data
  }

  /**
   * 获取支持的图表类型列表
   */
  async getDiagramTypes(): Promise<{ types: DiagramTypeInfo[] }> {
    const response = await this.client.get('/api/diagram-types')
    return response.data
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health')
    return response.data
  }
}

// 导出单例
export const api = new ApiClient()
export default api
