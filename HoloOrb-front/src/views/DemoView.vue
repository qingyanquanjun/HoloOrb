<script setup>
import { ref, onMounted } from 'vue'
import { sayHello, echoData, healthCheck } from '@/api/example'

const name = ref('HoloOrb')
const helloResult = ref('')
const helloError = ref('')
const helloLoading = ref(false)

const inputData = ref('{\n  "key": "value",\n  "count": 42\n}')
const echoResult = ref('')
const echoError = ref('')
const echoLoading = ref(false)

const healthInfo = ref(null)

async function handleHello() {
  helloLoading.value = true
  helloError.value = ''
  helloResult.value = ''
  try {
    const data = await sayHello(name.value)
    helloResult.value = JSON.stringify(data, null, 2)
  } catch (e) {
    helloError.value = e.message || '请求失败'
  } finally {
    helloLoading.value = false
  }
}

async function handleEcho() {
  echoLoading.value = true
  echoError.value = ''
  echoResult.value = ''
  try {
    const parsed = JSON.parse(inputData.value)
    const data = await echoData(parsed)
    echoResult.value = JSON.stringify(data, null, 2)
  } catch (e) {
    if (e instanceof SyntaxError) {
      echoError.value = 'JSON 格式错误：' + e.message
    } else {
      echoError.value = e.message || '请求失败'
    }
  } finally {
    echoLoading.value = false
  }
}

onMounted(async () => {
  try {
    healthInfo.value = await healthCheck()
  } catch (e) {}
})
</script>

<template>
  <div class="demo">
    <h1>接口演示</h1>
    <p class="tip">本页面演示与 Flask 后端 API 的交互，确保后端运行在 <code>http://localhost:5000</code>。</p>

    <section class="panel">
      <h2>GET /api/hello</h2>
      <div class="row">
        <label>Name 参数</label>
        <input v-model="name" type="text" placeholder="输入名称" />
        <button :disabled="helloLoading" @click="handleHello">
          {{ helloLoading ? '请求中...' : '发送请求' }}
        </button>
      </div>
      <pre v-if="helloResult" class="result success">{{ helloResult }}</pre>
      <div v-if="helloError" class="result error">{{ helloError }}</div>
    </section>

    <section class="panel">
      <h2>POST /api/echo</h2>
      <div class="row column">
        <label>请求体（JSON）</label>
        <textarea v-model="inputData" rows="6" placeholder='{"key": "value"}'></textarea>
        <button :disabled="echoLoading" @click="handleEcho">
          {{ echoLoading ? '请求中...' : '发送请求' }}
        </button>
      </div>
      <pre v-if="echoResult" class="result success">{{ echoResult }}</pre>
      <div v-if="echoError" class="result error">{{ echoError }}</div>
    </section>

    <section class="panel" v-if="healthInfo">
      <h2>健康检查</h2>
      <pre class="result success">{{ JSON.stringify(healthInfo, null, 2) }}</pre>
    </section>
  </div>
</template>

<style scoped>
.demo {
  max-width: 860px;
}
h1 {
  font-size: 30px;
  color: #1f2937;
  margin: 0 0 8px;
}
.tip {
  color: #6b7280;
  margin: 0 0 24px;
  font-size: 14px;
}
.tip code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  color: #4f46e5;
}
.panel {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
}
.panel h2 {
  font-size: 18px;
  color: #1f2937;
  margin: 0 0 16px;
}
.row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.row.column {
  flex-direction: column;
  align-items: stretch;
}
.row label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}
input, textarea {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s ease;
}
input:focus, textarea:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}
textarea {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  resize: vertical;
}
button {
  padding: 10px 20px;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
button:hover:not(:disabled) {
  background: #4338ca;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.result {
  margin: 16px 0 0;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
}
.result.success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #86efac;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
.result.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}
</style>
