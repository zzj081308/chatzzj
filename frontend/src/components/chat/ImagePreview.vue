<script setup lang="ts">
import { NModal, NImage } from 'naive-ui'

const props = defineProps<{
  show: boolean
  url: string | null
}>()
const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <NModal :show="show" @update:show="emit('close')">
    <div class="preview-container" @click="emit('close')">
      <NImage v-if="url" :src="url" class="preview-image" />
    </div>
  </NModal>
</template>

<style scoped>
.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 300px;
  min-height: 300px;
}
.preview-image {
  max-width: 80vw;
  max-height: 80vh;
}
</style>
