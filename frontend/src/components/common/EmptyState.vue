<script setup lang="ts">
defineProps<{
  message: string
}>()
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">💬</div>
    <div class="empty-message">{{ message }}</div>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
}
.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}
.empty-message {
  font-size: 16px;
}
</style>
