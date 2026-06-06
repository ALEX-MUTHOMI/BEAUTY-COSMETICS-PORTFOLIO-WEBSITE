<template>
  <span class="status-chip" :data-tone="tone">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { friendlyStatus } from './statusCopy'

const props = defineProps<{
  status: string
}>()

const label = computed(() => friendlyStatus(props.status))
const tone = computed(() => {
  const status = props.status.toLowerCase()
  if (status.includes('success') || status.includes('paid') || status.includes('confirmed') || status.includes('completed')) {
    return 'good'
  }
  if (status.includes('failed') || status.includes('no_show')) {
    return 'bad'
  }
  if (status.includes('review') || status.includes('pending') || status.includes('held')) {
    return 'watch'
  }
  return 'neutral'
})
</script>

<style scoped>
.status-chip {
  display: inline-flex;
  align-items: center;
  width: max-content;
  min-height: 1.8rem;
  padding: 0 0.7rem;
  border-radius: 999px;
  font: 850 0.78rem/1 ui-sans-serif, system-ui, sans-serif;
}

.status-chip[data-tone='good'] {
  color: #17452b;
  background: #dff4e7;
}

.status-chip[data-tone='bad'] {
  color: #762515;
  background: #ffe1d8;
}

.status-chip[data-tone='watch'] {
  color: #70450c;
  background: #ffecc7;
}

.status-chip[data-tone='neutral'] {
  color: #50382b;
  background: #efe3d7;
}
</style>
