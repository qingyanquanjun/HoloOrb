<template>
  <div class="report-list-page">
    <div class="alert">
      <el-alert type="info" :closable="false" show-icon>
        <template #title>
          本页展示所有报表记录。若要查看「本周趋势」图表，请切换到左侧菜单 报表中心 → 本周趋势。
        </template>
      </el-alert>
    </div>

    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Files /></el-icon> 全部报表</span>
        <div>
          <el-button type="primary" size="small" @click="handleAdd"><el-icon><DocumentAdd /></el-icon> 新建报表</el-button>
        </div>
      </div>

      <el-row :gutter="16" style="margin-bottom: 16px">
        <el-col :xs="12" :sm="6" v-for="(c, i) in counts" :key="i">
          <div class="r-card" :style="{ borderTop: `3px solid ${c.color}` }">
            <div class="r-label">{{ c.label }}</div>
            <div class="r-value" :style="{ color: c.color }">{{ c.value }}</div>
          </div>
        </el-col>
      </el-row>

      <el-table :data="reportList" stripe v-loading="loading">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="title" label="报表名称" min-width="320" show-overflow-tooltip />
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="generated_at" label="生成时间" width="180" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '生成中' ? 'warning' : 'success'" effect="dark" size="small">
              {{ row.status === 'generated' ? '已完成' : row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small">预览</el-button>
            <el-button link type="primary" size="small">下载</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @size-change="loadReports"
        @current-change="loadReports"
      />
    </div>

    <el-dialog v-model="dialogVisible" title="新建报表" width="500px" destroy-on-close>
      <el-form :model="form" label-width="100px" size="default">
        <el-form-item label="报表类型" required>
          <el-select v-model="form.type" placeholder="请选择" style="width: 100%">
            <el-option label="日报" value="日报" />
            <el-option label="周报" value="周报" />
            <el-option label="月报" value="月报" />
          </el-select>
        </el-form-item>
        <el-form-item label="报表标题" required>
          <el-input v-model="form.title" placeholder="请输入报表标题" />
        </el-form-item>
        <el-form-item label="报表内容">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请输入报表内容（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listReports, createReport, deleteReport } from '@/api/reports'

const loading = ref(false)
const reportList = ref([])
const pagination = reactive({ page: 1, per_page: 10, total: 0 })

const dialogVisible = ref(false)
const form = reactive({ type: '', title: '', content: '' })

const counts = computed(() => [
  { label: '日报', value: reportList.value.filter((r) => r.type === '日报').length, color: '#67C23A' },
  { label: '周报', value: reportList.value.filter((r) => r.type === '周报').length, color: '#409EFF' },
  { label: '月报', value: reportList.value.filter((r) => r.type === '月报').length, color: '#E6A23C' },
  { label: '总计', value: reportList.value.length, color: '#F56C6C' }
])

async function loadReports() {
  loading.value = true
  try {
    const data = await listReports({ page: pagination.page, per_page: pagination.per_page })
    reportList.value = data.items || data.data || []
    pagination.total = data.total || 0
  } catch (e) {
    console.error('Failed to load reports', e)
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  Object.assign(form, { type: '', title: '', content: '' })
  dialogVisible.value = true
}

async function submitForm() {
  if (!form.type || !form.title) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    await createReport(form)
    ElMessage.success('报表创建成功')
    dialogVisible.value = false
    loadReports()
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定删除报表「${row.title}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteReport(row.id)
        ElMessage.success('删除成功')
        loadReports()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.report-list-page { width: 100%; }
.alert { margin-bottom: 16px; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
.r-card {
  background: #fafbfc;
  padding: 14px;
  border-radius: 8px;
}
.r-label { font-size: 13px; color: #909399; }
.r-value { font-size: 22px; font-weight: 700; margin-top: 4px; }
</style>