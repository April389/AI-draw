/**
 * Toolbar 组件测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent, cleanup } from '@testing-library/vue'
import { createPinia, setActivePinia } from 'pinia'
import Toolbar from '@/components/Toolbar.vue'

// Mock api
import { vi } from 'vitest'
vi.mock('@/api', () => ({
  api: { generateDiagram: vi.fn(), healthCheck: vi.fn() }
}))

beforeEach(() => {
  setActivePinia(createPinia())
  cleanup()
})

describe('Toolbar 组件', () => {
  it('渲染所有工具栏按钮', () => {
    render(Toolbar)
    
    // 缩放相关
    expect(screen.getByTitle('放大')).toBeTruthy()
    expect(screen.getByTitle('缩小')).toBeTruthy()
    expect(screen.getByTitle('重置视图')).toBeTruthy()
    expect(screen.getByTitle('适应内容')).toBeTruthy()
    
    // 导出相关
    expect(screen.getByTitle('导出为 PNG')).toBeTruthy()
    expect(screen.getByTitle('导出为 SVG')).toBeTruthy()
    expect(screen.getByTitle('导出为 JSON')).toBeTruthy()
    
    // 操作
    expect(screen.getByTitle('删除选中')).toBeTruthy()
    expect(screen.getByTitle('清空画布')).toBeTruthy()
  })

  it('点击导出按钮触发对应事件', () => {
    const { emitted } = render(Toolbar)
    
    fireEvent.click(screen.getByTitle('导出为 PNG'))
    expect(emitted().exportPng).toBeTruthy()
    
    fireEvent.click(screen.getByTitle('导出为 SVG'))
    expect(emitted().exportSvg).toBeTruthy()
    
    fireEvent.click(screen.getByTitle('导出为 JSON'))
    expect(emitted().exportJson).toBeTruthy()
  })

  it('点击缩放按钮触发对应事件', () => {
    const { emitted } = render(Toolbar)
    
    fireEvent.click(screen.getByTitle('放大'))
    expect(emitted().zoomIn).toBeTruthy()
    
    fireEvent.click(screen.getByTitle('缩小'))
    expect(emitted().zoomOut).toBeTruthy()
  })
})
