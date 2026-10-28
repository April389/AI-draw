<template>
  <div class="canvas-container">
    <!-- 空状态 -->
    <div v-if="!store.hasDiagram" class="empty-state">
      <div class="empty-icon">📊</div>
      <div class="empty-title">还没有图表</div>
      <div class="empty-desc">在左侧输入你的需求，AI 将为你生成专业图表</div>
    </div>

    <!-- 图表显示区 -->
    <div v-else class="diagram-wrapper" ref="diagramWrapper">
      <svg
        ref="svgRef"
        class="diagram-svg"
        :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`"
        :width="svgWidth"
        :height="svgHeight"
        @mousedown="onSvgMouseDown"
        @mousemove="onSvgMouseMove"
        @mouseup="onSvgMouseUp"
        @wheel.prevent="onWheel"
      >
        <!-- 背景 -->
        <rect
          :x="viewBox.x - 10000"
          :y="viewBox.y - 10000"
          :width="20000"
          :height="20000"
          fill="#fafbfc"
        />
        <!-- 网格 -->
        <g class="grid">
          <pattern id="smallGrid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e8eaed" stroke-width="0.5"/>
          </pattern>
          <rect :x="viewBox.x - 10000" :y="viewBox.y - 10000" :width="20000" :height="20000" fill="url(#smallGrid)"/>
        </g>

        <!-- 连线/箭头层 -->
        <g class="edges">
          <g
            v-for="edge in renderableEdges"
            :key="edge.id"
            class="edge"
          >
            <defs>
              <marker
                :id="'arrow-' + edge.id"
                viewBox="0 0 10 10"
                refX="8"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#1e1e1e" />
              </marker>
            </defs>
            <line
              :x1="edge.x1"
              :y1="edge.y1"
              :x2="edge.x2"
              :y2="edge.y2"
              :stroke="edge.strokeColor"
              :stroke-width="edge.strokeWidth"
              :stroke-dasharray="edge.dashArray"
              :marker-end="edge.hasEndArrow ? `url(#arrow-${edge.id})` : undefined"
              :marker-start="edge.hasStartArrow ? `url(#arrow-${edge.id})` : undefined"
              class="edge-line"
              :class="{ selected: selectedId === edge.id }"
              @mousedown.stop="selectElement(edge.id, $event)"
            />
            <!-- 连线标签 -->
            <text
              v-if="edge.label"
              :x="edge.labelX"
              :y="edge.labelY"
              text-anchor="middle"
              dominant-baseline="middle"
              font-size="14"
              fill="#606266"
              class="edge-label"
            >
              {{ edge.label }}
            </text>
          </g>
        </g>

        <!-- 节点层 -->
        <g class="nodes">
          <g
            v-for="node in renderableNodes"
            :key="node.id"
            class="node-group"
            transform="translate(0, 0)"
          >
            <!-- 选择框 -->
            <rect
              v-if="selectedId === node.id"
              :x="node.x - 4"
              :y="node.y - 4"
              :width="node.width + 8"
              :height="node.height + 8"
              fill="none"
              stroke="#409eff"
              stroke-width="1.5"
              stroke-dasharray="4,2"
              rx="4"
            />
            
            <!-- 节点形状 -->
            <rect
              v-if="node.shape === 'rectangle'"
              :x="node.x"
              :y="node.y"
              :width="node.width"
              :height="node.height"
              :fill="node.fill"
              :stroke="node.stroke"
              stroke-width="2"
              rx="6"
              ry="6"
              class="node-shape"
              :class="{ selected: selectedId === node.id }"
              @mousedown.stop="selectElement(node.id, $event)"
            />
            <ellipse
              v-else-if="node.shape === 'ellipse'"
              :cx="node.x + node.width / 2"
              :cy="node.y + node.height / 2"
              :rx="node.width / 2"
              :ry="node.height / 2"
              :fill="node.fill"
              :stroke="node.stroke"
              stroke-width="2"
              class="node-shape"
              :class="{ selected: selectedId === node.id }"
              @mousedown.stop="selectElement(node.id, $event)"
            />
            <polygon
              v-else-if="node.shape === 'diamond'"
              :points="node.diamondPoints"
              :fill="node.fill"
              :stroke="node.stroke"
              stroke-width="2"
              class="node-shape"
              :class="{ selected: selectedId === node.id }"
              @mousedown.stop="selectElement(node.id, $event)"
            />
            
            <!-- 节点文本 -->
            <text
              v-if="node.label"
              :x="node.x + node.width / 2"
              :y="node.y + node.height / 2"
              text-anchor="middle"
              dominant-baseline="middle"
              font-size="14"
              fill="#1e1e1e"
              class="node-label"
              pointer-events="none"
            >
              {{ node.label }}
            </text>
          </g>
        </g>
      </svg>

      <!-- 图表标题 -->
      <div v-if="store.currentDiagram?.title" class="diagram-title">
        {{ store.currentDiagram.title }}
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="store.isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">AI 生成中...</div>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <button @click="deleteSelected">删除选中</button>
      <button @click="copySelected">复制</button>
    </div>
  </div>
</template>

<script setup lang="ts">import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useDiagramStore } from '@/stores/diagram';
import { exportToPng, exportToSvg, exportToJson } from '@/utils/export';
const store = useDiagramStore();
// ==================== SVG相关 ====================
const svgRef = ref<SVGSVGElement | null>(null);
const diagramWrapper = ref<HTMLElement | null>(null);
// ==================== 视口控制 ====================
const viewBox = ref({ x: 0, y: 0, width: 1200, height: 800 });
const svgWidth = ref(1200);
const svgHeight = ref(800);
const selectedId = ref<string | null>(null);
// ==================== 拖拽状态 ====================
interface DragState {
 isDragging: boolean;
 isPanning: boolean;
 startX: number;
 startY: number;
 startViewX: number;
 startViewY: number;
 draggedNodeId: string | null;
 nodeOffsetX: number;
 nodeOffsetY: number;
}
const drag = ref<DragState>({
 isDragging: false,
 isPanning: false,
 startX: 0,
 startY: 0,
 startViewX: 0,
 startViewY: 0,
 draggedNodeId: null,
 nodeOffsetX: 0,
 nodeOffsetY: 0
});
// ==================== 渲染节点 ====================
interface RenderableNode {
 id: string;
 label: string;
 shape: string;
 x: number;
 y: number;
 width: number;
 height: number;
 fill: string;
 stroke: string;
 diamondPoints: string;
}
const NODE_SIZES: Record<string, [number, number]> = {
 rectangle: [140, 60],
 ellipse: [120, 60],
 diamond: [100, 100],
 parallelogram: [140, 60],
 cylinder: [100, 80],
 cloud: [160, 80],
 hexagon: [120, 80]
};
// 自动布局（如果节点没有指定坐标）
function ensureLayout() {
 if (!store.currentDiagram)
 return;
 const nodes = store.currentDiagram.nodes;
 const edges = store.currentDiagram.edges || [];
 const hasCoords = nodes.every(n => n.x != null && n.y != null);
 if (hasCoords)
 return;
 // 简单的分层布局
 const nodeMap = new Map(nodes.map(n => [n.id, { ...n }]));
 // 计算每个节点的层级
 const inDegree = new Map<string, number>();
 nodes.forEach(n => inDegree.set(n.id, 0));
 edges.forEach(e => {
 inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
 });
 // 找到根节点
 const roots = nodes.filter(n => (inDegree.get(n.id) || 0) === 0);
 if (roots.length === 0)
 roots.push(nodes[0]);
 // BFS分层
 const layers: string[][] = [];
 const visited = new Set<string>();
 const queue: [string, number][] = roots.map(r => [r.id, 0]);
 const nodeLayer = new Map<string, number>();
 while (queue.length > 0) {
 const [nid, layer] = queue.shift()!;
 if (visited.has(nid))
 continue;
 visited.add(nid);
 nodeLayer.set(nid, layer);
 if (!layers[layer])
 layers[layer] = [];
 layers[layer].push(nid);
 // 出边
 edges.filter(e => e.source === nid).forEach(e => {
 if (!visited.has(e.target)) {
 queue.push([e.target, layer + 1]);
 }
 });
 }
 // 孤立节点放最后
 nodes.forEach(n => {
 if (!visited.has(n.id)) {
 const lastLayer = layers.length;
 if (!layers[lastLayer])
 layers[lastLayer] = [];
 layers[lastLayer].push(n.id);
 }
 });
 // 分配坐标
 const H_GAP = 280;
 const V_GAP = 120;
 layers.forEach((layerNodes, layerIdx) => {
 layerNodes.forEach((nid, nodeIdx) => {
 const node = nodeMap.get(nid)!;
 if (node.x == null)
 node.x = 100 + layerIdx * H_GAP;
 if (node.y == null)
 node.y = 100 + nodeIdx * V_GAP;
 });
 });
 // 更新store中的节点（使用unref避免直接修改）
 store.currentDiagram.nodes = nodes.map(n => nodeMap.get(n.id) || n);
}
const renderableNodes = computed<RenderableNode[]>(() => {
 if (!store.currentDiagram)
 return [];
 ensureLayout();
 return store.currentDiagram.nodes.map(node => {
 const size = NODE_SIZES[node.type] || NODE_SIZES.rectangle;
 const width = node.width || size[0];
 const height = node.height || size[1];
 const x = node.x ?? 100;
 const y = node.y ?? 100;
 // 计算菱形点
 const cx = x + width / 2;
 const cy = y + height / 2;
 const diamondPoints = `${cx},${y} ${x + width},${cy} ${cx},${y + height} ${x},${cy}`;
 return {
 id: node.id,
 label: node.label,
 shape: node.type,
 x, y, width, height,
 fill: node.color || '#ffffff',
 stroke: node.stroke_color || '#1e1e1e',
 diamondPoints
 };
 });
});
// ==================== 渲染边 ====================
interface RenderableEdge {
 id: string;
 source: string;
 target: string;
 label: string | null;
 x1: number;
 y1: number;
 x2: number;
 y2: number;
 strokeColor: string;
 strokeWidth: number;
 dashArray: string;
 hasEndArrow: boolean;
 hasStartArrow: boolean;
 labelX: number;
 labelY: number;
}
function getBoundaryPoint(fromNode: RenderableNode, toNode: RenderableNode, isSource: boolean): [number, number] {
 // 计算从 from 到 to 方向上 from 的边界点
 const fx = fromNode.x + fromNode.width / 2;
 const fy = fromNode.y + fromNode.height / 2;
 const tx = toNode.x + toNode.width / 2;
 const ty = toNode.y + toNode.height / 2;
 const dx = tx - fx;
 const dy = ty - fy;
 const len = Math.sqrt(dx * dx + dy * dy);
 if (len === 0)
 return [fx, fy];
 const nx = dx / len;
 const ny = dy / len;
 // 判断从哪个边界出去
 const hw = fromNode.width / 2;
 const hh = fromNode.height / 2;
 // 菱形特殊处理
 if (fromNode.shape === 'diamond') {
 // 菱形边界更复杂，简单处理为缩一半距离
 return [fx + nx * len * 0.5, fy + ny * len * 0.5];
 }
 // 矩形/椭圆边界
 const scale = Math.min(Math.abs(hw / (nx || 0.0001)), Math.abs(hh / (ny || 0.0001)));
 return [fx + nx * scale, fy + ny * scale];
}
const renderableEdges = computed<RenderableEdge[]>(() => {
 if (!store.currentDiagram)
 return [];
 const edges = store.currentDiagram.edges || [];
 if (edges.length === 0)
 return [];
 const nodeMap = new Map(renderableNodes.value.map(n => [n.id, n]));
 return edges.map(edge => {
 const sourceNode = nodeMap.get(edge.source);
 const targetNode = nodeMap.get(edge.target);
 if (!sourceNode || !targetNode) {
 return {
 id: edge.id, source: edge.source, target: edge.target,
 label: edge.label || null,
 x1: 0, y1: 0, x2: 0, y2: 0,
 strokeColor: '#1e1e1e', strokeWidth: 2, dashArray: '',
 hasEndArrow: false, hasStartArrow: false, labelX: 0, labelY: 0
 };
 }
 const [x1, y1] = getBoundaryPoint(sourceNode, targetNode, true);
 const [x2, y2] = getBoundaryPoint(targetNode, sourceNode, false);
 const arrow = edge.arrow || 'end';
 const style = edge.style || 'solid';
 const dashArray = style === 'dashed' ? '8,4' : style === 'dotted' ? '2,4' : '';
 const labelX = (x1 + x2) / 2;
 const labelY = (y1 + y2) / 2 - 8;
 return {
 id: edge.id, source: edge.source, target: edge.target,
 label: edge.label || null,
 x1, y1, x2, y2,
 strokeColor: '#1e1e1e',
 strokeWidth: 2,
 dashArray,
 hasEndArrow: arrow === 'end' || arrow === 'both',
 hasStartArrow: arrow === 'start' || arrow === 'both',
 labelX, labelY
 };
 });
});
// ==================== 鼠标交互 ====================
function selectElement(id: string, event: MouseEvent) {
 selectedId.value = id;
 // 开始拖拽
 const node = store.currentDiagram?.nodes.find(n => n.id === id);
 if (node) {
 drag.value.isDragging = true;
 drag.value.draggedNodeId = id;
 drag.value.nodeOffsetX = getSvgX(event) - (node.x ?? 0);
 drag.value.nodeOffsetY = getSvgY(event) - (node.y ?? 0);
 }
}
function getSvgX(event: MouseEvent): number {
 if (!svgRef.value)
 return 0;
 const rect = svgRef.value.getBoundingClientRect();
 const scale = viewBox.value.width / rect.width;
 return (event.clientX - rect.left) * scale + viewBox.value.x;
}
function getSvgY(event: MouseEvent): number {
 if (!svgRef.value)
 return 0;
 const rect = svgRef.value.getBoundingClientRect();
 const scale = viewBox.value.height / rect.height;
 return (event.clientY - rect.top) * scale + viewBox.value.y;
}
function onSvgMouseDown(event: MouseEvent) {
 // 点击空白区域 - 开始平移
 if (event.target === svgRef.value ||
 (event.target as Element).classList?.contains('grid')) {
 drag.value.isPanning = true;
 drag.value.startX = event.clientX;
 drag.value.startY = event.clientY;
 drag.value.startViewX = viewBox.value.x;
 drag.value.startViewY = viewBox.value.y;
 selectedId.value = null;
 }
}
function onSvgMouseMove(event: MouseEvent) {
 if (drag.value.isPanning && svgRef.value) {
 const rect = svgRef.value.getBoundingClientRect();
 const scale = viewBox.value.width / rect.width;
 const dx = (event.clientX - drag.value.startX) * scale;
 const dy = (event.clientY - drag.value.startY) * scale;
 viewBox.value.x = drag.value.startViewX - dx;
 viewBox.value.y = drag.value.startViewY - dy;
 }
 if (drag.value.isDragging && drag.value.draggedNodeId && store.currentDiagram) {
 const node = store.currentDiagram.nodes.find(n => n.id === drag.value.draggedNodeId);
 if (node) {
 node.x = getSvgX(event) - drag.value.nodeOffsetX;
 node.y = getSvgY(event) - drag.value.nodeOffsetY;
 }
 }
}
function onSvgMouseUp() {
 drag.value.isDragging = false;
 drag.value.isPanning = false;
 drag.value.draggedNodeId = null;
}
function onWheel(event: WheelEvent) {
 const zoomFactor = event.deltaY > 0 ? 1.1 : 0.9;
 const rect = svgRef.value!.getBoundingClientRect();
 const mouseX = (event.clientX - rect.left) / rect.width * viewBox.value.width + viewBox.value.x;
 const mouseY = (event.clientY - rect.top) / rect.height * viewBox.value.height + viewBox.value.y;
 const newWidth = viewBox.value.width * zoomFactor;
 const newHeight = viewBox.value.height * zoomFactor;
 viewBox.value.x = mouseX - (mouseX - viewBox.value.x) * zoomFactor;
 viewBox.value.y = mouseY - (mouseY - viewBox.value.y) * zoomFactor;
 viewBox.value.width = newWidth;
 viewBox.value.height = newHeight;
}
// ==================== 操作 ====================
function deleteSelected() {
 if (!selectedId.value || !store.currentDiagram)
 return;
 store.currentDiagram.nodes = store.currentDiagram.nodes.filter(n => n.id !== selectedId.value);
 store.currentDiagram.edges = (store.currentDiagram.edges || []).filter(e => e.source !== selectedId.value && e.target !== selectedId.value);
 selectedId.value = null;
}
function copySelected() {
 // 简化实现：暂时不支持
}
// ==================== 初始化视口 ====================
function fitToContent() {
 if (!store.currentDiagram) {
 viewBox.value = { x: 0, y: 0, width: 1200, height: 800 };
 return;
 }
 // 确保有布局
 ensureLayout();
 const nodes = store.currentDiagram.nodes;
 if (nodes.length === 0)
 return;
 let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
 for (const n of nodes) {
 const x = n.x ?? 0;
 const y = n.y ?? 0;
 const size = NODE_SIZES[n.type] || NODE_SIZES.rectangle;
 minX = Math.min(minX, x);
 minY = Math.min(minY, y);
 maxX = Math.max(maxX, x + (n.width || size[0]));
 maxY = Math.max(maxY, y + (n.height || size[1]));
 }
 const padding = 60;
 viewBox.value = {
 x: minX - padding,
 y: minY - padding,
 width: maxX - minX + padding * 2,
 height: maxY - minY + padding * 2
 };
}
// 暴露给工具栏的方法
defineExpose({
 exportPng: () => {
 const svg = svgRef.value;
 if (svg) {
 exportToPng([], `${store.currentDiagram?.title || 'diagram'}.png`);
 }
 },
 exportSvg: () => {
 exportToSvg([], `${store.currentDiagram?.title || 'diagram'}.svg`);
 },
 exportJson: () => {
 exportToJson(store.currentDiagram, `${store.currentDiagram?.title || 'diagram'}.json`);
 },
 fitToContent,
 zoomIn: () => {
 viewBox.value.width /= 1.2;
 viewBox.value.height /= 1.2;
 },
 zoomOut: () => {
 viewBox.value.width *= 1.2;
 viewBox.value.height *= 1.2;
 },
 resetView: () => {
 fitToContent();
 },
 deleteSelected,
 clearSelection: () => { selectedId.value = null; }
});
// ==================== 生命周期 ====================
onMounted(async () => {
 await nextTick();
 window.addEventListener('mouseup', onSvgMouseUp);
 if (store.hasDiagram) {
 fitToContent();
 }
});
onUnmounted(() => {
 window.removeEventListener('mouseup', onSvgMouseUp);
});
// 监听图表变化自动适配视口
import { watch } from 'vue';
watch(() => store.currentDiagram, (val) => {
 if (val) {
 nextTick(() => fitToContent());
 }
}, { immediate: true });
// 监听窗口大小变化
onMounted(() => {
 const updateSize = () => {
 if (diagramWrapper.value) {
 svgWidth.value = diagramWrapper.value.clientWidth;
 svgHeight.value = diagramWrapper.value.clientHeight;
 }
 };
 updateSize();
 window.addEventListener('resize', updateSize);
 onUnmounted(() => {
 window.removeEventListener('resize', updateSize);
 });
});
// 右键菜单
const contextMenu = ref({ visible: false, x: 0, y: 0 });
</script>

<style scoped>
.canvas-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-title {
  font-size: 18px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
}

/* SVG容器 */
.diagram-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.diagram-svg {
  display: block;
  cursor: grab;
}

.diagram-svg:active {
  cursor: grabbing;
}

/* 节点样式 */
.node-shape {
  cursor: pointer;
  transition: filter 0.15s;
}

.node-shape:hover {
  filter: brightness(0.95);
}

.node-shape.selected {
  stroke: #409eff !important;
  stroke-width: 3px;
}

.node-label {
  pointer-events: none;
  user-select: none;
}

/* 连线样式 */
.edge-line {
  cursor: pointer;
  transition: stroke-width 0.15s;
}

.edge-line:hover {
  stroke-width: 3 !important;
}

.edge-line.selected {
  stroke: #409eff !important;
}

.edge-label {
  pointer-events: none;
  user-select: none;
}

/* 标题 */
.diagram-title {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 18px;
  font-weight: 600;
  color: #1e1e1e;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 20px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 加载遮罩 */
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

.loading-text {
  color: #606266;
  font-size: 14px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 4px 0;
  z-index: 1000;
}

.context-menu button {
  display: block;
  width: 100%;
  padding: 8px 16px;
  border: none;
  background: transparent;
  text-align: left;
  font-size: 13px;
  cursor: pointer;
  color: #606266;
}

.context-menu button:hover {
  background: #f5f7fa;
  color: #409eff;
}
</style>
