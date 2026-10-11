<script setup lang="ts">
import { NText } from 'naive-ui'
</script>

<template>
  <div class="typing-indicator">
    <NText depth="3" class="typing-text">
      <span class="dots">
        <span class="dot">●</span>
        <span class="dot">●</span>
        <span class="dot">●</span>
      </span>
      对方正在输入...
    </NText>
  </div>
</template>

<style scoped>
.typing-indicator {
  padding: 4px 8px;
}
.typing-text {
  font-size: 12px;
  font-style: italic;
}
.dots {
  display: inline-flex;
  gap: 3px;
}
.dot {
  font-size: 6px;
  animation: blink 1.4s infinite both;
}
.dot:nth-child(2) {
  animation-delay: 0.2s;
}
.dot:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes blink {
  0%, 80%, 100% { opacity: 0; }
  40% { opacity: 1; }
}
</style>
