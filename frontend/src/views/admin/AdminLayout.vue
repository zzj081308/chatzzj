<script setup lang="ts">
import { h, ref, computed } from "vue"
import { useRouter, useRoute } from "vue-router"
import { useAuthStore } from "../../stores/auth"
import { NLayout, NLayoutSider, NLayoutHeader, NLayoutContent, NMenu, NButton, NText, NAvatar } from "naive-ui"
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)
const menuOptions = [
  { label: "控制台", key: "/admin", icon: () => h("span", { style: "font-size:18px" }, "#1") },
  { label: "用户管理", key: "/admin/users", icon: () => h("span", { style: "font-size:18px" }, "#2") },
  { label: "消息管理", key: "/admin/messages", icon: () => h("span", { style: "font-size:18px" }, "#3") },
  { label: "系统设置", key: "/admin/settings", icon: () => h("span", { style: "font-size:18px" }, "#4") },
  { label: "申诉管理", key: "/admin/appeals", icon: () => h("span", { style: "font-size:18px" }, "#5") },
]
const activeKey = computed(() => {
  for (const opt of menuOptions) { if (route.path.startsWith(opt.key)) return opt.key }
  return "/admin"
})
function handleMenuUpdate(key: string) { router.push(key) }
</script>
<template>
  <NLayout class="admin-layout" has-sider>
    <NLayoutSider bordered :collapsed="collapsed" collapse-mode="width" :collapsed-width="64" :width="220" class="admin-sider">
      <div class="admin-sider-header"><NText strong>Chatzzj 管理</NText></div>
      <NMenu :value="activeKey" :collapsed="collapsed" :collapsed-width="64" :collapsed-icon-size="22" :options="menuOptions" @update:value="handleMenuUpdate" />
      <div class="admin-sider-footer"><NButton text size="small" @click="router.push('/chat')">&larr; 返回聊天</NButton></div>
    </NLayoutSider>
    <NLayout>
      <NLayoutHeader bordered class="admin-header">
        <div class="header-left"><NButton text @click="collapsed = !collapsed" class="toggle-btn">☰</NButton><NText depth="3">{{ route.path }}</NText></div>
        <div class="header-right"><NAvatar :size="28" round :src="authStore.user?.avatar_url || undefined">{{ authStore.user?.username?.[0]?.toUpperCase() }}</NAvatar><NText depth="3">{{ authStore.user?.username }}</NText></div>
      </NLayoutHeader>
      <NLayoutContent class="admin-content"><router-view /></NLayoutContent>
    </NLayout>
  </NLayout>
</template>
<style scoped>
.admin-layout { height: 100vh; }
.admin-sider { height: 100vh; display: flex; flex-direction: column; }
.admin-sider-header { padding: 16px; border-bottom: 1px solid var(--n-border-color); }
.admin-sider-footer { padding: 12px 16px; border-top: 1px solid var(--n-border-color); margin-top: auto; }
.admin-header { height: 50px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; }
.header-left, .header-right { display: flex; align-items: center; gap: 12px; }
.toggle-btn { font-size: 18px; }
.admin-content { padding: 24px; background: #f5f6fa; height: calc(100vh - 50px); overflow-y: auto; }
</style>
