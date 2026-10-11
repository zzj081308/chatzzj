<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useFriendsStore } from '../stores/friends'
import { useWebSocket } from '../composables/useWebSocket'
import AppLayout from '../components/layout/AppLayout.vue'

const friendsStore = useFriendsStore()
const ws = useWebSocket()

onMounted(async () => {
  await friendsStore.fetchFriends()
  await friendsStore.fetchPendingRequests()
  ws.connect()
})

onUnmounted(() => {
  ws.disconnect()
})
</script>

<template>
  <AppLayout />
</template>
