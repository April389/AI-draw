/**
 * 导出工具函数
 * 支持 PNG / SVG / JSON 格式导出
 */
import type { ExcalidrawElement } from '@/types'

/**
 * 导出为PNG图片
 */
export function exportToPng(elements: ExcalidrawElement[], filename: string = 'diagram.png'): void {
  const svg = elementsToSvg(elements)
  const svgBlob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svgBlob)
  
  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    const padding = 40
    
    // 计算边界
    const bounds = calculateBounds(elements)
    canvas.width = bounds.width + padding * 2
    canvas.height = bounds.height + padding * 2
    
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, padding, padding, bounds.width, bounds.height)
    
    canvas.toBlob((blob) => {
      if (blob) {
        downloadBlob(blob, filename)
      }
      URL.revokeObjectURL(url)
    }, 'image/png')
  }
  img.onerror = () => {
    // 如果canvas方式失败，直接下载SVG
    const svgBlob = new Blob([svg], { type: 'image/svg+xml' })
    downloadBlob(svgBlob, filename.replace('.png', '.svg'))
    URL.revokeObjectURL(url)
  }
  img.src = url
}

/**
 * 导出为SVG文件
 */
export function exportToSvg(elements: ExcalidrawElement[], filename: string = 'diagram.svg'): void {
  const svg = elementsToSvg(elements)
  const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' })
  downloadBlob(blob, filename)
}

/**
 * 导出为JSON数据
 */
export function exportToJson(data: any, filename: string = 'diagram.json'): void {
  const json = JSON.stringify(data, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  downloadBlob(blob, filename)
}

/**
 * 将Excalidraw元素转换为SVG字符串
 */
export function elementsToSvg(elements: ExcalidrawElement[]): string {
  const bounds = calculateBounds(elements)
  const padding = 20
  
  let svgContent = `<svg xmlns="http://www.w3.org/2000/svg" width="${bounds.width + padding * 2}" height="${bounds.height + padding * 2}" viewBox="${bounds.x - padding} ${bounds.y - padding} ${bounds.width + padding * 2} ${bounds.height + padding * 2}">`
  svgContent += `<rect x="${bounds.x - padding}" y="${bounds.y - padding}" width="${bounds.width + padding * 2}" height="${bounds.height + padding * 2}" fill="#ffffff"/>`
  
  for (const el of elements) {
    svgContent += elementToSvg(el)
  }
  
  svgContent += '</svg>'
  return svgContent
}

/**
 * 单个元素转SVG
 */
function elementToSvg(el: ExcalidrawElement): string {
  const cx = el.x + el.width / 2
  const cy = el.y + el.height / 2
  
  const baseStyle = `fill="${el.backgroundColor}" stroke="${el.strokeColor}" stroke-width="${el.strokeWidth}"`
  
  switch (el.type) {
    case 'rectangle':
      return `<rect x="${el.x}" y="${el.y}" width="${el.width}" height="${el.height}" rx="6" ry="6" ${baseStyle}/>`
    
    case 'ellipse':
      return `<ellipse cx="${cx}" cy="${cy}" rx="${el.width / 2}" ry="${el.height / 2}" ${baseStyle}/>`
    
    case 'diamond':
      const points = [
        [cx, el.y],
        [el.x + el.width, cy],
        [cx, el.y + el.height],
        [el.x, cy]
      ].map(p => p.join(',')).join(' ')
      return `<polygon points="${points}" ${baseStyle}/>`
    
    case 'arrow':
      if (el.points && el.points.length >= 2) {
        const pathD = el.points.map((p, i) => 
          `${i === 0 ? 'M' : 'L'} ${p[0]} ${p[1]}`
        ).join(' ')
        return `<path d="${pathD}" fill="none" stroke="${el.strokeColor}" stroke-width="${el.strokeWidth}" marker-end="url(#arrowhead)"/>`
      }
      return ''
    
    case 'text':
      if (el.text) {
        return `<text x="${el.x}" y="${el.y + (el.fontSize || 20)}" font-family="sans-serif" font-size="${el.fontSize || 20}" fill="${el.strokeColor}">${escapeXml(el.text)}</text>`
      }
      return ''
    
    default:
      return `<rect x="${el.x}" y="${el.y}" width="${el.width}" height="${el.height}" ${baseStyle}/>`
  }
}

/**
 * 计算所有元素的边界框
 */
function calculateBounds(elements: ExcalidrawElement[]): { x: number; y: number; width: number; height: number } {
  if (elements.length === 0) {
    return { x: 0, y: 0, width: 800, height: 600 }
  }
  
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
  
  for (const el of elements) {
    minX = Math.min(minX, el.x)
    minY = Math.min(minY, el.y)
    
    if (el.type === 'arrow' && el.points) {
      // 箭头需要遍历所有端点
      for (const [px, py] of el.points) {
        const absX = el.x + px
        const absY = el.y + py
        minX = Math.min(minX, absX)
        minY = Math.min(minY, absY)
        maxX = Math.max(maxX, absX)
        maxY = Math.max(maxY, absY)
      }
    } else {
      maxX = Math.max(maxX, el.x + el.width)
      maxY = Math.max(maxY, el.y + el.height)
    }
  }
  
  return {
    x: Math.floor(minX),
    y: Math.floor(minY),
    width: Math.ceil(maxX - minX),
    height: Math.ceil(maxY - minY)
  }
}

/**
 * 下载Blob
 */
function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/**
 * XML转义
 */
function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}
