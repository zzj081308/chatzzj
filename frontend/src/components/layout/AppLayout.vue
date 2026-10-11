<script setup lang="ts">
import { useChatStore } from '../../stores/chat'
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
import ChatWindow from '../chat/ChatWindow.vue'
import MessageInput from '../chat/MessageInput.vue'
import EmptyState from '../common/EmptyState.vue'
import { NLayout, NLayoutSider, NLayoutContent, NLayoutHeader } from 'naive-ui'

const chatStore = useChatStore()
</script>

<template>
  <NLayout class="app-layout" has-sider>
    <NLayoutSider width="320" bordered class="sidebar">
      <Sidebar />
    </NLayoutSider>

    <NLayoutContent>
      <template v-if="chatStore.activeFriendId">
        <NLayoutHeader bordered class="chat-header">
          <TopBar />
        </NLayoutHeader>
        <div class="chat-body">
          <ChatWindow />
          <MessageInput />
        </div>
      </template>
      <template v-else>
        <EmptyState message="选择一位好友开始聊天" />
      </template>
    </NLayoutContent>
  </NLayout>
</template>

<style scoped>
.app-layout {
  height: 100vh;
}
.sidebar {
  height: 100vh;
  overflow: hidden;
}
.chat-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
}
.chat-body {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
}
</style>
