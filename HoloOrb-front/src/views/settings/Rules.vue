<template>
  <div class="rules">
    <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px">
      <template #title>当前为演示数据，后端暂未提供告警规则管理API。</template>
    </el-alert>
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title"><el-icon><AlarmClock /></el-icon> 告警规则列表</span>
        <el-button type="primary" size="small" disabled><el-icon><Plus /></el-icon> 新建规则</el-button>
      </div>
      <el-table :data="list" stripe>
        <el-table-column type="index" width="60" label="#" />
        <el-table-column prop="name" label="规则名称" min-width="220" />
        <el-table-column width="90" label="级别">
          <template #default="{ row }">
            <el-tag :type="levelTag(row.level)" effect="dark" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="适用范围" width="150" />
        <el-table-column label="通知方式" min-width="220">
          <template #default="{ row }">
            <el-tag size="small" v-for="n in row.notify" :key="n" style="margin-right: 6px">{{ n }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="启用" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="(v)=>onToggle(row,v)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small">匹配日志</el-button>
            <el-button link type="primary" size="small">编辑</el-button>
            <el-button link type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="panel" style="margin-top: 16px">
      <div class="panel-head"><span class="panel-title">📝 规则模板</span></div>
      <el-descriptions :column="2" border size="default">
        <el-descriptions-item label="CPU 阈值模板">
          <code>cpu.usage > {X}% for {N}min</code>
          <el-button link type="primary" size="small" style="margin-left: 8px">使用此模板</el-button>
        </el-descriptions-item>
        <el-descriptions-item label="磁盘阈值模板">
          <code>disk.free_pct < {X}%</code>
          <el-button link type="primary" size="small" style="margin-left: 8px">使用此模板</el-button>
        </el-descriptions-item>
        <el-descriptions-item label="设备离线模板">
          <code>device.online = false for {N}min</code>
          <el-button link type="primary" size="small" style="margin-left: 8px">使用此模板</el-button>
        </el-descriptions-item>
        <el-descriptions-item label="网络丢包模板">
          <code>iface.loss_pct > {X}%</code>
          <el-button link type="primary" size="small" style="margin-left: 8px">使用此模板</el-button>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { alarmRules } from '@/config/mock'

const list = ref([...alarmRules])
function levelTag(l) {
  return { 严重: 'danger', 警告: 'warning', 提示: 'info' }[l] || 'info'
}
function onToggle(row, v) {
  ElMessage.success(`规则「${row.name}」已${v ? '启用' : '禁用'}`)
}
</script>

<style scoped>
.rules { width: 100%; }
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title { font-size: 15px; font-weight: 600; color: #303133; display: flex; align-items: center; gap: 6px; }
code {
  background: #f2f3f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  color: #409EFF;
  font-family: Consolas, Monaco, monospace;
}
</style>
