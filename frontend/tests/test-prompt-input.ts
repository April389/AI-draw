/**
 * PromptInput 组件测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent, cleanup } from '@testing-library/vue'
import { createPinia, setActivePinia } from 'pinia'
import PromptInput from '@/components/PromptInput.vue'

// Mock api
import { vi } from 'vitest'
vi.mock('@/api', () => ({
  api: { generateDiagram: vi.fn().mockResolvedValue({ success: false }) }
}))

beforeEach(() => {
  setActivePinia(createPinia())
  cleanup()
})

describe('PromptInput 组件', () => {
  it('渲染输入框和按钮', () => {
    render(PromptInput)
    
    expect(screen.getByLabelText('图表描述输入')).toBeTruthy()
    expect(screen.getByRole('button', { name: /生成图表/ })).toBeTruthy()
    expect(screen.getByRole('button', { name: /清空/ })).toBeTruthy()
  })

  it('默认时生成按钮禁用', () => {
    render(PromptInput)
    
    const btn = screen.getByRole('button', { name: /生成图表/ }) as HTMLButtonElement
    expect(btn.disabled).toBe(true)
  })

  it('输入内容后启用生成按钮', () => {
    render(PromptInput)
    
    const textarea = screen.getByLabelText('图表描述输入')
    fireEvent.update(textarea, '创建一个流程图')
    
    const btn = screen.getByRole('button', { name: /生成图表/ }) as HTMLButtonElement
    expect(btn.disabled).toBe(false)
  })

  it('点击清空按钮清空输入', () => {
    render(PromptInput)
    
    const textarea = screen.getByLabelText('图表描述输入')
    fireEvent.update(textarea, '测试内容')
    expect((textarea as HTMLTextAreaElement).value).toBe('测试内容')
    
    fireEvent.click(screen.getByRole('button', { name: /清空/ }))
    expect((textarea as HTMLTextAreaElement).value).toBe('')
  })

  it('渲染快捷建议按钮', () => {
    render(PromptInput)
    
    expect(screen.getByText('登录流程')).toBeTruthy()
    expect(screen.getByText('微服务架构')).toBeTruthy()
    expect(screen.getByText('时序交互')).toBeTruthy()
    expect(screen.getByText('思维导图')).toBeTruthy()
  })

  it('点击建议填充输入框', () => {
    render(PromptInput)
    
    fireEvent.click(screen.getByText('登录流程'))
    
    const textarea = screen.getByLabelText('图表描述输入') as HTMLTextAreaElement
    expect(textarea.value).toContain('登录')
  })

  it('图表类型选择器包含正确选项', () => {
    render(PromptInput)
    
    const select = screen.getByLabelText('图表类型') as HTMLSelectElement
    expect(select.value).toBe('')
    
    fireEvent.change(select, { target: { value: 'flowchart' } })
    expect(select.value).toBe('flowchart')
  })
})
