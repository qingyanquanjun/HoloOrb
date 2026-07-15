<template>
  <div class="ai-chat">
    <div class="panel chat-panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><ChatDotRound /></el-icon> AI 智能问答</span>
        <div>
          <el-tag size="small" type="success">模型：DeepSeek v4 Flash</el-tag>
          <el-button size="small" text style="margin-left: 10px" @click="clearChat">
            <el-icon><Delete /></el-icon> 清空对话
          </el-button>
          <el-button size="small" type="primary" style="margin-left: 10px" @click="showSaveDialog = true" :disabled="!hasAssistantReply">
            <el-icon><Document /></el-icon> 保存报告
          </el-button>
        </div>
      </div>

      <el-scrollbar class="chat-body" ref="chatBodyRef">
        <div v-if="!messages.length" class="empty-state">
          <el-icon class="empty-icon"><MagicStick /></el-icon>
          <div class="empty-title">你好，我是 HoloOrb 智能助手</div>
          <div class="empty-desc">可以向我询问任何设备、告警、网络相关的问题，或让我生成分析报告。</div>
          <div class="quick-list">
            <div v-for="q in quickQuestions" :key="q" class="quick-item" @click="sendQuick(q)">
              <el-icon><ChatLineRound /></el-icon> {{ q }}
            </div>
          </div>
        </div>
        <div v-else class="msg-list">
          <div v-for="(m, i) in messages" :key="i" class="msg-row" :class="m.role">
            <div class="avatar" :class="m.role">
              <el-icon v-if="m.role === 'user'"><User /></el-icon>
              <el-icon v-else><MagicStick /></el-icon>
            </div>
            <div class="bubble">
              <div v-if="m.role === 'assistant' && m.typing" class="typing">
                <span></span><span></span><span></span>
              </div>
              <div v-else v-html="m.content"></div>
            </div>
          </div>
        </div>
      </el-scrollbar>

      <div class="chat-input">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          placeholder="输入你的问题...  (Enter 发送，Shift+Enter 换行)"
          resize="none"
          @keydown.enter.exact.prevent="sendMsg"
        />
        <el-button type="primary" :disabled="!input.trim() || loading" @click="sendMsg">
          <el-icon><Promotion /></el-icon> 发送
        </el-button>
      </div>
    </div>

    <el-dialog v-model="showSaveDialog" title="保存为报告" width="500px" destroy-on-close>
      <el-form :model="reportForm" label-width="80px">
        <el-form-item label="报告标题">
          <el-input v-model="reportForm.title" placeholder="请输入报告标题" />
        </el-form-item>
        <el-form-item label="报告内容">
          <el-input v-model="reportForm.content" type="textarea" :rows="6" readonly />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSaveDialog = false">取消</el-button>
        <el-button type="primary" @click="saveAsReport" :disabled="!reportForm.title.trim()">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { chat, saveReport } from '@/api/insight'

const input = ref('')
const loading = ref(false)
const messages = ref([])
const chatBodyRef = ref(null)
const showSaveDialog = ref(false)
const reportForm = reactive({
  title: '',
  content: ''
})

const hasAssistantReply = computed(() => {
  return messages.value.some(m => m.role === 'assistant' && !m.typing && m.content)
})

watch(showSaveDialog, (val) => {
  if (val) {
    const assistantMsgs = messages.value.filter(m => m.role === 'assistant' && !m.typing && m.content)
    if (assistantMsgs.length > 0) {
      const lastMsg = assistantMsgs[assistantMsgs.length - 1]
      reportForm.content = lastMsg.content.replace(/<[^>]+>/g, '').replace(/<br\/>/g, '\n').trim()
      reportForm.title = ''
    }
  }
})

const quickQuestions = [
  '分析当前 CPU 占用最高的 3 台设备，并给出优化建议',
  '统计最近 7 天的告警分布趋势',
  '为什么网络健康度下降了？可能的根因有哪些？',
  '生成一份本周运维重点工作清单'
]

function scrollBottom() {
  nextTick(() => {
    const sb = chatBodyRef.value
    if (!sb) return
    const wrap = sb.$el?.querySelector('.el-scrollbar__wrap') || sb.$el
    if (wrap) wrap.scrollTop = wrap.scrollHeight
  })
}

function markdownToHtml(text) {
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  html = html.replace(/^### (.*$)/gim, '<h4 style="margin:8px 0 4px;color:#303133;font-weight:600">$1</h4>')
  html = html.replace(/^## (.*$)/gim, '<h3 style="margin:10px 0 5px;color:#303133;font-weight:600">$1</h3>')
  html = html.replace(/^# (.*$)/gim, '<h2 style="margin:12px 0 6px;color:#303133;font-weight:600">$1</h2>')

  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')

  html = html.replace(/`([^`]+)`/g, '<code style="background:#f2f3f5;padding:1px 5px;border-radius:4px;font-size:12px;color:#E6A23C">$1</code>')

  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre style="background:#f2f3f5;padding:10px;border-radius:6px;font-size:12px;overflow-x:auto"><code>$2</code></pre>')

  html = html.replace(/^\- (.*$)/gim, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>')
  html = html.replace(/<\/ul>\s*<ul>/g, '')

  html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>')

  html = html.replace(/\|(.+)\|/g, (match) => {
    const cells = match.split('|').filter(c => c.trim())
    if (cells.length > 0) {
      return '<tr>' + cells.map(c => `<td style="border:1px solid #ebeef5;padding:4px 8px">${c.trim()}</td>`).join('') + '</tr>'
    }
    return match
  })
  html = html.replace(/(<tr>.*<\/tr>)/g, '<table style="width:100%;border-collapse:collapse;margin:6px 0;font-size:13px">$1</table>')
  html = html.replace(/<\/table>\s*<table>/g, '')

  html = html.replace(/\n/g, '<br/>')

  return html
}

function addMsg(role, content, typing = false) {
  const msg = { role, content, typing }
  messages.value.push(msg)
  scrollBottom()
  return msg
}

async function sendMsg() {
  const text = input.value.trim()
  if (!text) return
  if (loading.value) return
  addMsg('user', text.replace(/\n/g, '<br/>'))
  input.value = ''
  loading.value = true

  addMsg('assistant', '', true)
  const replyIndex = messages.value.length - 1

  const history = messages.value.slice(0, -1).map(m => ({
    role: m.role,
    content: m.content.replace(/<br\/>/g, '\n').replace(/<[^>]+>/g, '')
  }))

  try {
    const res = await chat({ message: text, history })
    messages.value[replyIndex].typing = false
    messages.value[replyIndex].content = markdownToHtml(res.content)
  } catch (error) {
    messages.value[replyIndex].typing = false
    messages.value[replyIndex].content = `<span style="color:#F56C6C">AI 服务调用失败：${error.message || '未知错误'}</span>`
    ElMessage.error('AI 服务调用失败')
  }

  scrollBottom()
  loading.value = false
}

function sendQuick(q) {
  input.value = q
  sendMsg()
}

function clearChat() {
  if (!messages.value.length) return
  messages.value = []
  ElMessage.info('对话已清空')
}

async function saveAsReport() {
  if (!reportForm.title.trim()) {
    ElMessage.warning('请输入报告标题')
    return
  }
  try {
    await saveReport({
      title: reportForm.title.trim(),
      content: reportForm.content
    })
    ElMessage.success('报告保存成功')
    showSaveDialog.value = false
  } catch (error) {
    ElMessage.error('保存失败')
  }
}
</script>

<style scoped>
.ai-chat {
  width: 100%;
  display: flex;
}
.chat-panel {
  width: 100%;
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  min-height: 560px;
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }

.chat-body {
  flex: 1;
  background: #f7f8fa;
  border-radius: 8px;
  padding: 18px;
  min-height: 200px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}
.empty-icon { font-size: 56px; color: #409EFF; }
.empty-title { font-size: 18px; font-weight: 600; color: #303133; margin-top: 12px; }
.empty-desc { font-size: 13px; color: #909399; margin-top: 6px; }
.quick-list {
  max-width: 640px;
  margin: 24px auto 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.quick-item {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px 14px;
  text-align: left;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.quick-item:hover {
  border-color: #409EFF;
  color: #409EFF;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
}

.msg-list { display: flex; flex-direction: column; gap: 16px; }
.msg-row { display: flex; gap: 10px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }
.avatar {
  width: 36px; height: 36px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
}
.avatar.user { background: #409EFF; }
.avatar.assistant { background: linear-gradient(135deg, #67C23A, #409EFF); }
.bubble {
  max-width: 70%;
  background: #fff;
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.7;
  color: #303133;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  word-break: break-word;
}
.msg-row.user .bubble {
  background: #409EFF;
  color: #fff;
}
.bubble :deep(h4) {
  display: block;
  margin: 8px 0 4px;
  color: #303133 !important;
  font-size: 15px;
}
.bubble :deep(table) { width: 100%; border-collapse: collapse; margin: 6px 0; font-size: 13px; }
.bubble :deep(td), .bubble :deep(th) { border: 1px solid #ebeef5; padding: 4px 8px; }
.bubble :deep(code) { background: #f2f3f5; padding: 1px 5px; border-radius: 4px; font-size: 12px; color: #E6A23C; }
.msg-row.user .bubble :deep(code) { background: rgba(255,255,255,0.2); color: #fff; }

.typing { display: inline-flex; gap: 4px; padding: 4px 0; }
.typing span {
  width: 7px; height: 7px; background: #409EFF; border-radius: 50%;
  animation: blink 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%,60%,100% { opacity: 0.3; transform: translateY(0); } 30% { opacity: 1; transform: translateY(-3px); } }

.chat-input {
  display: flex;
  gap: 12px;
  margin-top: 14px;
  align-items: flex-end;
}
.chat-input .el-textarea { flex: 1; }
</style>
