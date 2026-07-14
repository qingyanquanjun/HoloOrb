<template>
  <div class="settings">
    <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px">
      <template #title>当前为演示数据，后端暂未提供数据采集任务管理API。</template>
    </el-alert>
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><Connection /></el-icon> 数据采集任务</span>
        <el-button type="primary" size="small" disabled><el-icon><Plus /></el-icon> 新建采集任务</el-button>
      </div>
      <el-table :data="list" stripe>
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="任务名称" min-width="200" />
        <el-table-column prop="target" label="采集目标" width="150" />
        <el-table-column prop="interval" label="采集周期" width="110" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-switch v-model="row.runningStatus" :active-value="true" :inactive-value="false" @change="(v)=>toggle(row,v)" />
            <span style="margin-left: 8px; font-size: 12px" :class="row.status === '运行中' ? 'on' : 'off'">{{ row.status }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastRun" label="最近执行" width="140" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" :disabled="row.status !== '运行中'">立即执行</el-button>
            <el-button link type="primary" size="small">日志</el-button>
            <el-button link type="primary" size="small">编辑</el-button>
            <el-button link type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head"><span class="panel-title">📊 近 7 天采集成功率</span></div>
      <BaseChart :option="succOption" height="260px" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import BaseChart from '@/components/BaseChart.vue'
import { collectionTasks } from '@/config/mock'
import dayjs from 'dayjs'

const list = ref(collectionTasks.map((t) => ({ ...t, runningStatus: t.status === '运行中' })))

function toggle(row, v) {
  row.status = v ? '运行中' : '已暂停'
  row.lastRun = v ? '刚刚' : row.lastRun
  ElMessage.success('任务已' + (v ? '启动' : '暂停'))
}

const succOption = computed(() => {
  const days = Array.from({ length: 7 }, (_, i) => dayjs().subtract(6 - i, 'day').format('MM-DD'))
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{
      type: 'bar',
      data: [99.2, 99.6, 98.7, 99.9, 99.4, 99.1, 99.7],
      itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top', formatter: '{c}%', fontSize: 11 }
    }]
  }
})
</script>

<style scoped>
.settings { width: 100%; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
.on { color: #67C23A; }
.off { color: #909399; }
</style>
