<script setup lang="ts">
import { NSpin } from 'naive-ui'
</script>

<template>
  <div class="loading-container">
    <NSpin size="medium" />
    <slot>加载中...</slot>
  </div>
</template>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  height: 100%;
  color: #999;
}
</style>
