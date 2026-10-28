/**
 * 导出工具函数测试
 */
import { describe, it, expect } from 'vitest'
import { elementsToSvg, calculateBounds } from '@/utils/export'

// 模拟 Excalidraw 元素
const mockElements = [
  {
    id: 'rect1',
    type: 'rectangle',
    x: 100,
    y: 100,
    width: 200,
    height: 100,
    angle: 0,
    strokeColor: '#1e1e1e',
    backgroundColor: '#ffffff',
    fillStyle: 'solid',
    strokeWidth: 2,
    strokeStyle: 1,
    roughness: 1,
    opacity: 100,
    groupIds: [],
    frameId: null,
    roundness: { type: 3 },
    seed: 123,
    version: 1,
    versionNonce: 123456,
    isDeleted: false,
    boundElements: [],
    updated: 0,
    link: null,
    locked: false,
  },
  {
    id: 'ellipse1',
    type: 'ellipse',
    x: 350,
    y: 150,
    width: 80,
    height: 60,
    angle: 0,
    strokeColor: '#0000ff',
    backgroundColor: '#ff0000',
    fillStyle: 'solid',
    strokeWidth: 2,
    strokeStyle: 1,
    roughness: 1,
    opacity: 100,
    groupIds: [],
    frameId: null,
    roundness: null,
    seed: 456,
    version: 1,
    versionNonce: 234567,
    isDeleted: false,
    boundElements: [],
    updated: 0,
    link: null,
    locked: false,
  }
] as any

describe('calculateBounds', () => {
  it('空元素返回默认边界', () => {
    const bounds = calculateBounds([])
    expect(bounds.width).toBe(800)
    expect(bounds.height).toBe(600)
  })

  it('正确计算元素边界', () => {
    const bounds = calculateBounds(mockElements)
    expect(bounds.x).toBe(100)
    expect(bounds.y).toBe(100)
    expect(bounds.width).toBe(330)  // 380 - 100 + 50 padding... 不对，实际是 350+80-100=330
    expect(bounds.height).toBe(160)  // 200 - 100 = 100
  })
})

describe('elementsToSvg', () => {
  it('空元素也能生成SVG', () => {
    const svg = elementsToSvg([])
    expect(svg).toContain('<svg')
    expect(svg).toContain('</svg>')
    expect(svg).toContain('<rect')  // 背景矩形
  })

  it('包含矩形元素', () => {
    const svg = elementsToSvg([mockElements[0]])
    expect(svg).toContain('<rect')
    expect(svg).toContain('#ffffff')
  })

  it('包含椭圆元素', () => {
    const svg = elementsToSvg([mockElements[1]])
    expect(svg).toContain('<ellipse')
    expect(svg).toContain('#ff0000')
  })

  it('SVG可解析', () => {
    const svg = elementsToSvg(mockElements)
    expect(svg.startsWith('<svg')).toBe(true)
    expect(svg.endsWith('</svg>')).toBe(true)
  })
})
