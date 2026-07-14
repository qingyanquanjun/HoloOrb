<template>
  <div class="insight-report">
    <div class="head">
      <div>
        <h2>AI 智能分析报告</h2>
        <div class="sub">由 HoloOrb-Insight 模型基于近 30 天全量数据自动生成</div>
      </div>
      <div>
        <el-button type="primary" plain><el-icon><Refresh /></el-icon> 立即生成新报告</el-button>
        <el-button type="primary"><el-icon><Download /></el-icon> 导出 PDF</el-button>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="7">
        <div class="panel">
          <div class="panel-title">📋 报告列表</div>
          <el-scrollbar style="max-height: calc(100vh - 240px); min-height: 400px">
            <div
              v-for="(r, i) in reports"
              :key="r.id"
              class="report-item"
              :class="{ active: i === 0 }"
            >
              <div class="ri-title">{{ r.title }}</div>
              <div class="ri-meta">
                <el-tag size="small" :type="r.riskLevel === '高' ? 'danger' : r.riskLevel === '中' ? 'warning' : 'success'">风险 {{ r.riskLevel }}</el-tag>
                <span class="ri-time"><el-icon><Clock /></el-icon> {{ r.createdAt }}</span>
              </div>
              <div class="ri-tags">
                <el-tag size="small" type="info" effect="plain" v-for="t in r.tags" :key="t" style="margin-right: 4px">{{ t }}</el-tag>
              </div>
            </div>
          </el-scrollbar>
        </div>
      </el-col>

      <el-col :xs="24" :lg="17">
        <div class="panel">
          <div class="report-body" v-if="reports.length">
            <div class="rb-head">
              <div>
                <div class="rb-title">{{ reports[0].title }}</div>
                <div class="rb-meta">
                  <span>报告 ID：{{ reports[0].id }}</span>
                  <span>生成时间：{{ reports[0].createdAt }}</span>
                  <el-tag size="small" :type="reports[0].riskLevel === '高' ? 'danger' : 'warning'">风险等级：{{ reports[0].riskLevel }}</el-tag>
                </div>
              </div>
            </div>

            <el-divider />

            <div class="section">
              <h4><el-icon><DataAnalysis /></el-icon> 一、分析摘要</h4>
              <p>{{ reports[0].summary }}</p>
            </div>

            <div class="section">
              <h4><el-icon><TrendCharts /></el-icon> 二、关键趋势</h4>
              <BaseChart :option="trendOption" height="260px" />
            </div>

            <div class="section">
              <h4><el-icon><Warning /></el-icon> 三、发现的问题（按优先级）</h4>
              <el-table :data="issues" size="small" border>
                <el-table-column width="60" label="优先级">
                  <template #default="{ $index }">
                    <el-tag :type="['danger','warning','info'][$index % 3]" size="small">P{{ $index + 1 }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="title" label="问题" />
                <el-table-column prop="impact" label="影响范围" width="160" />
                <el-table-column prop="detail" label="详情说明" min-width="240" />
              </el-table>
            </div>

            <div class="section">
              <h4><el-icon><List /></el-icon> 四、处置建议</h4>
              <el-steps :active="4" finish-status="success" simple>
                <el-step title="紧急处置" description="24h 内处理 P0：Server-07、Storage-02" />
                <el-step title="专项排查" description="本周内完成 Switch-03/Firewall-01 根因定位" />
                <el-step title="结构优化" description="两周内完成 AP 扩容、链路权重调整" />
                <el-step title="长效机制" description="建立告警规则有效性周评审机制" />
              </el-steps>
            </div>

            <div class="section">
              <h4><el-icon><PieChart /></el-icon> 五、风险分布</h4>
              <el-row :gutter="16">
                <el-col :span="12"><BaseChart :option="riskPieOption" height="240px" /></el-col>
                <el-col :span="12">
                  <div class="risk-stat">
                    <div class="rs-item"><div class="rs-label">严重风险</div><div class="rs-value" style="color:#F56C6C">2</div></div>
                    <div class="rs-item"><div class="rs-label">中等风险</div><div class="rs-value" style="color:#E6A23C">4</div></div>
                    <div class="rs-item"><div class="rs-label">轻微风险</div><div class="rs-value" style="color:#67C23A">7</div></div>
                    <div class="rs-item"><div class="rs-label">观察项</div><div class="rs-value" style="color:#909399">11</div></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from '@/components/BaseChart.vue'
import { aiPresetReports, anomalyTrend } from '@/config/mock'

const reports = [...aiPresetReports]
const issues = [
  { title: 'Server-07 CPU 持续高负载', impact: '数据库集群', detail: '峰值 97.8% 超过阈值，期间 12 条慢查询耗时>3s' },
  { title: 'Storage-02 磁盘即将耗尽', impact: '存储层', detail: '增长率 6.1%/周，预计 15 天后达到告警阈值' },
  { title: 'Switch-03 GE-0/2 持续丢包', impact: '办公区网络', detail: '平均丢包 2.1%，峰值 5.7% 与广播风暴强相关' },
  { title: '防火墙会话接近上限', impact: '边界安全', detail: '会话表使用 86%，晚高峰期间短连接激增' }
]

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['CPU 均值', '异常数', '告警数'], right: 10, top: 0 },
  grid: { left: 40, right: 20, top: 30, bottom: 30 },
  xAxis: { type: 'category', data: anomalyTrend.days.slice(-14), axisLabel: { fontSize: 10, interval: 1 } },
  yAxis: [{ type: 'value', name: '%' }, { type: 'value', name: '次' }],
  series: [
    { name: 'CPU 均值', type: 'line', smooth: true, yAxisIndex: 0,
      data: anomalyTrend.days.slice(-14).map(() => +(35 + Math.random() * 20).toFixed(1)),
      itemStyle: { color: '#409EFF' }
    },
    { name: '异常数', type: 'bar', yAxisIndex: 1, barWidth: 10,
      data: anomalyTrend.anomalies.slice(-14),
      itemStyle: { color: '#E6A23C', borderRadius: [4,4,0,0] }
    },
    { name: '告警数', type: 'bar', yAxisIndex: 1, barWidth: 10,
      data: anomalyTrend.days.slice(-14).map(() => Math.floor(Math.random() * 10 + 5)),
      itemStyle: { color: '#F56C6C', borderRadius: [4,4,0,0] }
    }
  ]
}))

const riskPieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 项 ({d}%)' },
  color: ['#F56C6C', '#E6A23C', '#67C23A', '#909399'],
  legend: { bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8 },
  series: [{
    type: 'pie',
    radius: ['40%', '68%'],
    center: ['50%', '45%'],
    label: { formatter: '{b}\n{c} 项' },
    data: [
      { name: '严重风险', value: 2 },
      { name: '中等风险', value: 4 },
      { name: '轻微风险', value: 7 },
      { name: '观察项', value: 11 }
    ]
  }]
}))
</script>

<style scoped>
.insight-report { width: 100%; }
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #409EFF 0%, #2C7EFF 100%);
  color: #fff;
  border-radius: 10px;
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: 0 4px 14px rgba(64, 158, 255, 0.25);
}
.head h2 { margin: 0 0 4px; font-size: 20px; }
.head .sub { opacity: 0.88; font-size: 13px; }

.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.report-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.report-item:hover { border-color: #409EFF; }
.report-item.active {
  border-color: #409EFF;
  background: #ecf5ff;
}
.ri-title { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 6px; }
.ri-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 12px; color: #909399; }
.ri-time { display: inline-flex; align-items: center; gap: 4px; }
.ri-tags { line-height: 1.8; }

.rb-head { padding-bottom: 4px; }
.rb-title { font-size: 18px; font-weight: 600; color: #303133; }
.rb-meta { margin-top: 6px; display: flex; align-items: center; gap: 14px; font-size: 13px; color: #909399; }

.section { margin: 16px 0; }
.section h4 {
  font-size: 15px;
  color: #303133;
  margin: 0 0 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.section p { line-height: 1.8; color: #606266; }

.risk-stat {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  padding: 10px;
}
.rs-item {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 14px;
  text-align: center;
}
.rs-label { font-size: 13px; color: #909399; margin-bottom: 4px; }
.rs-value { font-size: 24px; font-weight: 700; }
</style>
