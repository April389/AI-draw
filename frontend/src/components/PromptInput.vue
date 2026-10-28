<template>
  <div class="prompt-input">
    <div class="input-header">
      <h3>描述你的图表</h3>
      <select v-model="selectedType" class="type-select" aria-label="图表类型">
        <option :value="null">自动推断</option>
        <option v-for="t in diagramTypes" :key="t.value" :value="t.value">
          {{ t.label }}
        </option>
      </select>
    </div>

    <textarea
      v-model="prompt"
      placeholder="例如：创建一个用户从注册到登录的完整流程图..."
      rows="4"
      :disabled="store.isLoading"
      @keydown.ctrl.enter="handleGenerate"
      aria-label="图表描述输入"
      class="prompt-textarea"
    ></textarea>

    <div class="input-footer">
      <div class="quick-suggestions">
        <button 
          v-for="suggestion in suggestions" 
          :key="suggestion.label"
          type="button"
          class="suggestion-btn"
          @click="prompt = suggestion.text"
          :disabled="store.isLoading"
        >
          {{ suggestion.label }}
        </button>
      </div>
      
      <div class="action-buttons">
        <button 
          type="button"
          class="clear-btn"
          @click="clear"
          :disabled="!prompt || store.isLoading"
        >
          清空
        </button>
        <button 
          type="button"
          class="generate-btn"
          @click="handleGenerate"
          :disabled="!prompt.trim() || store.isLoading"
        >
          <span v-if="store.isLoading" class="spinner"></span>
          {{ store.isLoading ? '生成中...' : '生成图表' }}
        </button>
      </div>
    </div>

    <div v-if="store.error" class="error-message" role="alert">
      {{ store.error }}
    </div>
    <div v-if="store.isLoading" class="loading-tip">
      AI 正在思考并生成图表，请稍候...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDiagramStore } from '@/stores/diagram'
import { DIAGRAM_TYPES } from '@/types'
import type { DiagramType } from '@/types'

const store = useDiagramStore()

const prompt = ref('')
const selectedType = ref<DiagramType | null>(null)
const diagramTypes = DIAGRAM_TYPES

const suggestions = [
  { label: '登录流程', text: '创建一个用户登录流程图，包含输入账号密码、验证信息、登录成功和登录失败等步骤' },
  { label: '微服务架构', text: '创建一个微服务架构图，包含客户端、Nginx、API网关、微服务集群、Redis和MySQL' },
  { label: '时序交互', text: '描述用户在电商平台下单的完整时序，涉及用户、前端、订单服务、支付服务、库存服务' },
  { label: '思维导图', text: '创建人工智能学习路径的思维导图，从基础数学开始到深度学习应用' },
]

async function handleGenerate() {
  if (!prompt.value.trim()) return
  await store.generate(prompt.value, selectedType.value)
}

function clear() {
  prompt.value = ''
  store.clearDiagram()
}
</script>

<style scoped>
.prompt-input {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.input-header h3 {
  font-size: 16px;
  color: #1e1e1e;
  margin: 0;
}

.type-select {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
}

.prompt-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
}

.prompt-textarea:focus {
  outline: none;
  border-color: #409eff;
}

.prompt-textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.input-footer {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-btn {
  padding: 4px 10px;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  background: #f5f7fa;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-btn:hover:not(:disabled) {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.clear-btn, .generate-btn {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn {
  background: #fff;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.clear-btn:hover:not(:disabled) {
  color: #409eff;
  border-color: #c6e2ff;
}

.generate-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.generate-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  margin-top: 12px;
  padding: 10px 14px;
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 6px;
  color: #f56c6c;
  font-size: 13px;
}

.loading-tip {
  margin-top: 12px;
  padding: 10px 14px;
  background: #ecf5ff;
  border-radius: 6px;
  color: #409eff;
  font-size: 13px;
}
</style>
