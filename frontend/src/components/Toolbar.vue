<template>
  <div class="toolbar" role="toolbar" aria-label="工具栏">
    <div class="toolbar-group">
      <button class="tool-btn" title="放大" @click="emit('zoomIn')" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          <line x1="11" y1="8" x2="11" y2="14"/>
          <line x1="8" y1="11" x2="14" y2="11"/>
        </svg>
      </button>
      <button class="tool-btn" title="缩小" @click="emit('zoomOut')" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          <line x1="8" y1="11" x2="14" y2="11"/>
        </svg>
      </button>
      <button class="tool-btn" title="重置视图" @click="emit('resetView')" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
          <path d="M3 3v5h5"/>
        </svg>
      </button>
      <button class="tool-btn" title="适应内容" @click="emit('fitContent')" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
        </svg>
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button class="tool-btn" title="导出为 PNG" @click="emit('exportPng')" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <polyline points="21 15 16 10 5 21"/>
        </svg>
        <span>PNG</span>
      </button>
      <button class="tool-btn" title="导出为 SVG" @click="emit('exportSvg')" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <text x="8" y="16" font-size="6" fill="currentColor" stroke="none">SVG</text>
        </svg>
        <span>SVG</span>
      </button>
      <button class="tool-btn" title="导出为 JSON" @click="emit('exportJson')" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="16 18 22 12 16 6"/>
          <polyline points="8 6 2 12 8 18"/>
        </svg>
        <span>JSON</span>
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button class="tool-btn danger" title="删除选中" @click="emit('deleteSelected')" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6"/>
          <path d="M10 11v6M14 11v6"/>
          <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
        </svg>
      </button>
      <button class="tool-btn" title="清空画布" @click="store.clearDiagram()" :disabled="!store.hasDiagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
        </svg>
      </button>
    </div>

    <div class="toolbar-spacer"></div>

    <div class="toolbar-info">
      <span v-if="store.hasDiagram" class="stat">
        <strong>{{ store.nodeCount }}</strong> 节点
      </span>
      <span v-if="store.hasDiagram && store.edgeCount > 0" class="stat">
        <strong>{{ store.edgeCount }}</strong> 连线
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDiagramStore } from '@/stores/diagram'

const store = useDiagramStore()

const emit = defineEmits<{
  zoomIn: []
  zoomOut: []
  resetView: []
  fitContent: []
  exportPng: []
  exportSvg: []
  exportJson: []
  deleteSelected: []
}>()
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #e0e0e0;
  margin: 0 4px;
}

.toolbar-spacer {
  flex: 1;
}

.tool-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.tool-btn:hover:not(:disabled) {
  background: #f5f7fa;
  color: #409eff;
}

.tool-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tool-btn.danger:hover:not(:disabled) {
  background: #fef0f0;
  color: #f56c6c;
}

.toolbar-info {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.stat strong {
  color: #303133;
  font-weight: 600;
}
</style>
