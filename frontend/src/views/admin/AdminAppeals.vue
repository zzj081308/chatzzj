<script setup lang="ts">
import { ref, onMounted, computed, h } from "vue"
import { NDataTable, NButton, NInput, NTag, NText, NSpin, useMessage, NModal, NSpace, NSelect } from "naive-ui"
import * as adminApi from "../../api/appeal"
import type { Appeal } from "../../types"

const msg = useMessage()
const loading = ref(false); const appeals = ref<Appeal[]>([]); const statusFilter = ref("")
const showRejectModal = ref(false); const rejectReason = ref(""); const currentAppeal = ref<Appeal | null>(null)

async function fetch() {
  loading.value = true
  try { appeals.value = await adminApi.getAdminAppeals(statusFilter.value || undefined) }
  catch(e) { msg.error("加载失败") }
  finally { loading.value = false }
}

async function handleApprove(a: Appeal) {
  try { await adminApi.approveAppeal(a.id); msg.success("已解封用户 " + a.username); fetch() }
  catch(e: any) { msg.error(e.response?.data?.detail || "操作失败") }
}

function openReject(a: Appeal) {
  currentAppeal.value = a; rejectReason.value = ""; showRejectModal.value = true
}

async function handleReject() {
  if (!rejectReason.value.trim()) { msg.warning("请输入拒绝原因"); return }
  try {
    await adminApi.rejectAppeal(currentAppeal.value!.id, rejectReason.value)
    msg.success("已拒绝申诉"); showRejectModal.value = false; fetch()
  } catch(e: any) { msg.error(e.response?.data?.detail || "操作失败") }
}

const columns = computed(() => [
  { title: "ID", key: "id", width: 60 },
  { title: "用户名", key: "username", width: 100 },
  { title: "申诉理由", key: "reason", ellipsis: { tooltip: { width: 400 } } },
  {
    title: "状态", key: "status", width: 80,
    render: (r: Appeal) => {
      const m: Record<string, [string, string]> = { pending: ["warning", "待处理"], resolved: ["success", "已解封"], rejected: ["error", "已拒绝"] }
      const t = m[r.status] || ["default", r.status]
      return h(NTag, { type: t[0] as any, size: "small" }, { default: () => t[1] })
    }
  },
  { title: "管理员回复", key: "admin_response", ellipsis: { tooltip: true }, render: (r: Appeal) => r.admin_response || "-" },
  { title: "时间", key: "created_at", width: 150, render: (r: Appeal) => new Date(r.created_at).toLocaleString() },
  {
    title: "操作", key: "actions", width: 160,
    render: (r: Appeal) => {
      if (r.status !== "pending") return h(NText, { depth: 3 }, { default: () => "已处理" })
      return h(NSpace, {}, { default: () => [
        h(NButton, { size: "tiny", type: "primary", onClick: () => handleApprove(r) }, { default: () => "解封" }),
        h(NButton, { size: "tiny", type: "error", secondary: true, onClick: () => openReject(r) }, { default: () => "拒绝" }),
      ]})
    }
  },
]) as any

onMounted(fetch)
</script>

<template>
  <div class="aa"><div class="hr"><NText class="pt">申诉管理</NText><NSpace>
    <NSelect v-model:value="statusFilter" placeholder="全部状态" style="width:140px" clearable
      :options="[{label:'待处理',value:'pending'},{label:'已解封',value:'resolved'},{label:'已拒绝',value:'rejected'}]"
      @update:value="fetch" />
  </NSpace></div>
    <NSpin :show="loading"><NDataTable :columns="columns" :data="appeals" :bordered="true" size="small" style="margin-top:16px" /></NSpin>
    <NModal v-model:show="showRejectModal" title="拒绝申诉" preset="card" style="width:400px">
      <p style="margin-bottom:12px;color:#666">请填写拒绝原因：</p>
      <NInput type="textarea" v-model:value="rejectReason" placeholder="拒绝原因..." :rows="3" style="margin-bottom:12px" />
      <NSpace justify="end"><NButton @click="showRejectModal=false">取消</NButton><NButton type="error" @click="handleReject">确认拒绝</NButton></NSpace>
    </NModal>
  </div>
</template>
<style scoped>
.aa { max-width: 1200px; }
.hr { display: flex; justify-content: space-between; align-items: center; }
.pt { font-size: 22px; font-weight: 700; }
</style>

