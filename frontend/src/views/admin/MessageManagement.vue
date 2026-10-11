<script setup lang="ts">
import { ref, onMounted, computed, h } from "vue"
import { NDataTable, NButton, NInput, NTag, NText, NSpin, useMessage, useDialog, NPagination, NImage } from "naive-ui"
import * as adminApi from "../../api/admin"
import type { AdminMessage } from "../../types"
const msg = useMessage(); const dialog = useDialog()
const loading = ref(false); const messages = ref<AdminMessage[]>([]); const total = ref(0); const page = ref(1); const pageSize = ref(20); const search = ref(""); const senderFilter = ref(""); const receiverFilter = ref("")
let st: any = null
async function fetch() {
  loading.value = true
  try { const r = await adminApi.listMessages(page.value, pageSize.value, search.value || undefined, senderFilter.value || undefined, receiverFilter.value || undefined); messages.value = r.messages; total.value = r.total }
  catch(e) { msg.error("加载失败") } finally { loading.value = false }
}
function searchNow() { page.value = 1; clearTimeout(st); fetch() }
const columns = computed(() => [
  { title: "ID", key: "id", width: 70 },
  { title: "发送者", key: "sender_username", width: 100 },
  { title: "接收者", key: "receiver_username", width: 100 },
  { title: "类型", key: "message_type", width: 70, render: (r: AdminMessage) => {
    const m: Record<string, [string, string]> = { text: ["info", "文本"], image: ["success", "图片"], file: ["warning", "文件"] }
    const t = m[r.message_type] || ["default", r.message_type]
    return h(NTag, { type: t[0] as any, size: "small" }, { default: () => t[1] })
  }},
  { title: "内容", key: "content", ellipsis: { tooltip: { width: 400 } }, render: (r: AdminMessage) => {
    if (r.message_type === "image" && r.image_url) return h(NImage, { src: r.image_url, width: 60, height: 60, style: "border-radius:4px;object-fit:cover" })
    if (r.message_type === "file") return h(NText, { depth: 3 }, { default: () => r.file_name || "文件" })
    return r.content || "-"
  }},
  { title: "已读", key: "is_read", width: 60, render: (r: AdminMessage) => r.is_read ? h(NTag, { type: "success", size: "small" }, { default: () => "是" }) : h(NTag, { type: "default", size: "small" }, { default: () => "否" }) },
  { title: "时间", key: "created_at", width: 160, render: (r: AdminMessage) => new Date(r.created_at).toLocaleString() },
  { title: "操作", key: "actions", width: 80, render: (r: AdminMessage) => h(NButton, { size: "tiny", type: "error", secondary: true, onClick: () => confirmDel(r) }, { default: () => "删除" }) },
]) as any
function confirmDel(m: AdminMessage) {
  dialog.warning({ title: "确认删除", content: "确定删除消息 #" + m.id + " ？", positiveText: "删除", negativeText: "取消",
    onPositiveClick: async () => { try { await adminApi.deleteMessage(m.id); msg.success("ok"); fetch() } catch(e: any) { msg.error(e.response?.data?.detail || "fail") } }
  })
}
onMounted(fetch)
</script>
<template>
  <div class="mm">
    <div class="hr">
      <NText class="pt">消息管理</NText>
      <div style="display:flex;gap:8px;align-items:center">
        <NInput v-model:value="search" placeholder="搜索内容..." clearable size="small" style="width:130px" @keyup.enter="searchNow" />
        <NInput v-model:value="senderFilter" placeholder="发送者" clearable size="small" style="width:100px" @keyup.enter="searchNow" />
        <NInput v-model:value="receiverFilter" placeholder="接收者" clearable size="small" style="width:100px" @keyup.enter="searchNow" />
        <NButton size="small" type="primary" @click="searchNow">搜索</NButton>
      </div>
    </div>
    <NSpin :show="loading">
      <NDataTable :columns="columns" :data="messages" :bordered="false" striped size="small" style="margin-top:12px" />
    </NSpin>
    <div class="pr" v-if="total > pageSize">
      <NPagination v-model:page="page" :page-size="pageSize" :item-count="total" @update:page="fetch" />
    </div>
  </div>
</template>
<style scoped>
.mm { max-width: 1200px; }
.hr { display: flex; justify-content: space-between; align-items: center; }
.pt { font-size: 22px; font-weight: 700; }
.pr { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
