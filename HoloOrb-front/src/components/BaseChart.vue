<template>
  <div ref="chartEl" :style="{ width, height }"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, shallowRef } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  width: { type: String, default: '100%' },
  height: { type: String, default: '300px' }
})

const chartEl = ref(null)
const chartInstance = shallowRef(null)

function resizeHandler() {
  chartInstance.value?.resize()
}

function render() {
  if (!chartInstance.value || !chartEl.value) return
  chartInstance.value.setOption(props.option, true)
}

onMounted(() => {
  if (!chartEl.value) return
  chartInstance.value = echarts.init(chartEl.value)
  render()
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler)
  chartInstance.value?.dispose()
  chartInstance.value = null
})

watch(
  () => props.option,
  () => {
    render()
  },
  { deep: true }
)

defineExpose({
  getInstance: () => chartInstance.value,
  resize: resizeHandler
})
</script>
