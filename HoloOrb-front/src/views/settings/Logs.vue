<template>
  <div class="logs">
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Notebook /></el-icon> 操作日志</span>
        <el-button size="small" plain><el-icon><Download /></el-icon> 导出日志</el-button>
      </div>

      <el-form :inline="true" class="filters" label-width="80px">
        <el-form-item label="用户">
          <el-input v-model="q.username" placeholder="输入用户名" clearable style="width: 150px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="操作">
          <el-input v-model="q.action" placeholder="输入操作" clearable style="width: 150px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker
            v-model="q.date"
            type="datetimerange"
            range-separator="~"
            start-placeholder="开始"
            end-placeholder="结束"
            style="width: 320px"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadLogs">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="logList" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="created_at" label="时间" width="180" sortable />
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="action" label="操作" width="140" />
        <el-table-column prop="detail" label="详细信息" min-width="280" show-overflow-tooltip />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag type="success" effect="dark" size="small">成功</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10,20,50,100]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @size-change="loadLogs"
        @current-change="loadLogs"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { listLogs } from '@/api/logs'

const loading = ref(false)
const logList = ref([])
const pagination = reactive({ page: 1, per_page: 10, total: 0 })

const q = reactive({ username: '', action: '', date: [] })

async function loadLogs() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      username: q.username,
      action: q.action,
      start: q.date[0] || '',
      end: q.date[1] || ''
    }
    const data = await listLogs(params)
    logList.value = data.items || data.data || []
    pagination.total = data.total || 0
  } catch (e) {
    console.error('Failed to load logs', e)
  } finally {
    loading.value = false
  }
}

function reset() {
  q.username = ''
  q.action = ''
  q.date = []
  pagination.page = 1
  loadLogs()
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.logs { width: 100%; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
.filters {
  padding: 10px 0 0;
  border-top: 1px solid #f2f3f5;
  margin-bottom: 12px;
}
.filters :deep(.el-form-item) { margin-bottom: 12px; }
</style>