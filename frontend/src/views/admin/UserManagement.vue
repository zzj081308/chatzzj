<script setup lang="ts">
import { ref, onMounted, computed, h } from "vue"
import { NDataTable, NButton, NInput, NSpace, NTag, NText, NSpin, useMessage, useDialog, NPagination } from "naive-ui"
import * as adminApi from "../../api/admin"
import { useAuthStore } from "../../stores/auth"
import type { AdminUser } from "../../types"
const msg = useMessage(); const dialog = useDialog(); const authStore = useAuthStore()
const loading = ref(false); const users = ref<AdminUser[]>([]); const total = ref(0); const page = ref(1); const pageSize = ref(20); const search = ref("")
let st: ReturnType<typeof setTimeout> | null = null
function onSearchInput() {
  if (st) clearTimeout(st)
  st = setTimeout(() => { page.value = 1; fetch() }, 400)
}
async function fetch() {
  loading.value = true
  try { const r = await adminApi.listUsers(page.value, pageSize.value, search.value || undefined); users.value = r.users; total.value = r.total }
  catch(e) { msg.error("加载失败") } finally { loading.value = false }
}
const columns = computed(() => [
  { title: "ID", key: "id", width: 70 },
  { title: "用户名", key: "username", width: 130 },
  { title: "邮箱", key: "email", ellipsis: { tooltip: true } },
  { title: "状态", key: "is_online", width: 70, render: (r: AdminUser) => r.is_online ? h(NTag, { type: "success", size: "small" }, { default: () => "在线" }) : h(NTag, { type: "default", size: "small" }, { default: () => "离线" }) },
  { title: "AI", key: "is_ai", width: 50, render: (r: AdminUser) => r.is_ai ? h(NTag, { type: "info", size: "small" }, { default: () => "AI" }) : "" },
  { title: "管理员", key: "is_admin", width: 80, render: (r: AdminUser) => r.is_admin ? h(NTag, { type: "warning", size: "small" }, { default: () => "管理员" }) : "" },
  { title: "封禁", key: "is_banned", width: 70, render: (r: AdminUser) => r.is_banned ? h(NTag, { type: "error", size: "small" }, { default: () => "已封" }) : h(NTag, { type: "success", size: "small" }, { default: () => "正常" }) },
  { title: "注册时间", key: "created_at", width: 160, render: (r: AdminUser) => new Date(r.created_at).toLocaleString() },
  { title: "操作", key: "actions", width: 250, render: (r: AdminUser) => {
    if (r.id === authStore.user?.id) return h(NText, { depth: 3 }, "当前用户")
    if (r.is_ai) return h(NText, { depth: 3 }, "AI 角色")
    return h(NSpace, {}, { default: () => [
      r.is_banned
        ? h(NButton, { size: "tiny", type: "primary", onClick: () => unban(r) }, { default: () => "解封" })
        : h(NButton, { size: "tiny", type: "warning", onClick: () => ban(r) }, { default: () => "封禁" }),
      h(NButton, { size: "tiny", secondary: true, onClick: () => toggle(r) }, { default: () => r.is_admin ? "取消管理员" : "设为管理员" }),
      h(NButton, { size: "tiny", type: "error", secondary: true, onClick: () => confirmDel(r) }, { default: () => "删除" }),
    ]})
  }},
]) as any
async function ban(u: AdminUser) { try { await adminApi.banUser(u.id); msg.success("ok"); fetch() } catch(e: any) { msg.error(e.response?.data?.detail || "fail") } }
async function unban(u: AdminUser) { try { await adminApi.unbanUser(u.id); msg.success("ok"); fetch() } catch(e: any) { msg.error(e.response?.data?.detail || "fail") } }
async function toggle(u: AdminUser) { try { await adminApi.toggleAdmin(u.id); msg.success("ok"); fetch() } catch(e: any) { msg.error(e.response?.data?.detail || "fail") } }
function confirmDel(u: AdminUser) {
  dialog.warning({ title: "确认删除", content: "确定删除用户 " + u.username + " ？", positiveText: "删除", negativeText: "取消",
    onPositiveClick: async () => { try { await adminApi.deleteUser(u.id); msg.success("ok"); fetch() } catch(e: any) { msg.error(e.response?.data?.detail || "fail") } }
  })
}
onMounted(fetch)
</script>
<template>
  <div class="um"><div class="hr"><NText class="pt">用户管理</NText><NInput v-model:value="search" placeholder="搜索..." clearable style="width:240px" @input="onSearchInput" /></div>
    <NSpin :show="loading"><NDataTable :columns="columns" :data="users" :bordered="true" size="small" style="margin-top:16px" /></NSpin>
    <div class="pr" v-if="total > pageSize"><NPagination v-model:page="page" :page-size="pageSize" :item-count="total" @update:page="fetch" /></div>
  </div>
</template>
<style scoped>
.um { max-width: 1200px; }
.hr { display: flex; justify-content: space-between; align-items: center; }
.pt { font-size: 22px; font-weight: 700; }
.pr { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
