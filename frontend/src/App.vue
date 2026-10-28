<template>
  <div class="app">
    <!-- 顶部导航 -->
    <header class="app-header">
      <div class="logo">
        <span class="logo-icon">🧠</span>
        <span class="logo-text">AI 智能绘图系统</span>
      </div>
      <nav class="nav">
        <a href="#" class="nav-link active">绘图</a>
        <a href="#" class="nav-link">历史</a>
        <a href="#" class="nav-link">帮助</a>
      </nav>
      <div class="header-right">
        <span class="status-dot" :class="{ ok: backendOnline, error: !backendOnline }"></span>
        <span class="status-text">{{ backendOnline ? '后端已连接' : '后端离线' }}</span>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="app-main">
      <!-- 左侧：Prompt输入 -->
      <aside class="sidebar">
        <PromptInput />

        <!-- 历史记录 -->
        <div v-if="store.generationHistory.length > 0" class="history-section">
          <div class="history-header">
            <h4>最近生成</h4>
            <span class="history-count">{{ store.generationHistory.length }}</span>
          </div>
          <div class="history-list">
            <button
              v-for="entry in store.generationHistory"
              :key="entry.timestamp"
              class="history-item"
              @click="store.restoreFromHistory(entry)"
            >
              <div class="history-prompt">{{ entry.prompt.slice(0, 50) }}{{ entry.prompt.length > 50 ? '...' : '' }}</div>
              <div class="history-meta">
                <span>{{ entry.diagram.diagram_type }}</span>
                <span>{{ formatTime(entry.timestamp) }}</span>
              </div>
            </button>
          </div>
        </div>
      </aside>

      <!-- 右侧：画布 -->
      <section class="canvas-area">
        <Toolbar
          @zoom-in="canvasRef?.zoomIn()"
          @zoom-out="canvasRef?.zoomOut()"
          @reset-view="canvasRef?.resetView()"
          @fit-content="canvasRef?.fitToContent()"
          @export-png="canvasRef?.exportPng()"
          @export-svg="canvasRef?.exportSvg()"
          @export-json="canvasRef?.exportJson()"
          @delete-selected="canvasRef?.deleteSelected()"
        />
        <DiagramCanvas ref="canvasRef" />
      </section>
    </main>

    <!-- 底部 -->
    <footer class="app-footer">
      <span>基于 LLM 的智能矢量图表生成系统</span>
      <span class="footer-divider">·</span>
      <span>支持流程图 / 架构图 / 时序图 / 思维导图 / 状态图 / 类图</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PromptInput from './components/PromptInput.vue'
import Toolbar from './components/Toolbar.vue'
import DiagramCanvas from './components/DiagramCanvas.vue'
import { useDiagramStore } from './stores/diagram'
import { api } from './api'

const store = useDiagramStore()
const canvasRef = ref<InstanceType<typeof DiagramCanvas> | null>(null)
const backendOnline = ref(false)

function formatTime(ts: number): string {
  const date = new Date(ts)
  const now = new Date()
  const diff = now.getTime() - ts
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  
  return date.toLocaleString('zh-CN', { 
    month: 'numeric', 
    day: 'numeric', 
    hour: 'numeric', 
    minute: 'numeric' 
  })
}

async function checkBackend() {
  try {
    await api.healthCheck()
    backendOnline.value = true
  } catch {
    backendOnline.value = false
  }
}

onMounted(() => {
  checkBackend()
  // 每30秒检查一次
  setInterval(checkBackend, 30000)
})
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
}

/* 顶部导航 */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.logo-icon {
  font-size: 24px;
}

.nav {
  display: flex;
  gap: 24px;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 14px;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.nav-link:hover, .nav-link.active {
  color: white;
  border-bottom-color: white;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.15);
  padding: 4px 12px;
  border-radius: 16px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.ok {
  background: #52c41a;
  box-shadow: 0 0 6px #52c41a;
}

.status-dot.error {
  background: #ff4d4f;
  box-shadow: 0 0 6px #ff4d4f;
}

/* 主内容 */
.app-main {
  flex: 1;
  display: flex;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.sidebar {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.canvas-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

/* 历史记录 */
.history-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-header h4 {
  font-size: 14px;
  color: #303133;
  margin: 0;
}

.history-count {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 10px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafbfc;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.history-prompt {
  font-size: 13px;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1.4;
}

.history-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #909399;
}

/* 底部 */
.app-footer {
  padding: 10px 24px;
  background: #ffffff;
  border-top: 1px solid #e0e0e0;
  text-align: center;
  font-size: 12px;
  color: #909399;
}

.footer-divider {
  margin: 0 8px;
  color: #dcdfe6;
}
</style>
