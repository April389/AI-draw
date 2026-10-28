/**
 * 类型定义测试
 */
import { describe, it, expect } from 'vitest'
import { DIAGRAM_TYPES } from '@/types'

describe('DIAGRAM_TYPES常量', () => {
  it('包含所有7种图表类型', () => {
    expect(DIAGRAM_TYPES).toHaveLength(7)
  })

  it('包含正确的类型值', () => {
    const values = DIAGRAM_TYPES.map(t => t.value)
    expect(values).toContain('flowchart')
    expect(values).toContain('architecture')
    expect(values).toContain('sequence')
    expect(values).toContain('mindmap')
    expect(values).toContain('state')
    expect(values).toContain('class')
    expect(values).toContain('generic')
  })

  it('每个类型都有中文标签和描述', () => {
    for (const t of DIAGRAM_TYPES) {
      expect(t.label).toBeTruthy()
      expect(t.description).toBeTruthy()
    }
  })
})
