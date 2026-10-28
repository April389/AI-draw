/**
 * Vue应用入口
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)

// 状态管理
app.use(createPinia())

app.mount('#app')
