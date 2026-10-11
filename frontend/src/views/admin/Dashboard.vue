<script setup lang="ts">
import { ref, onMounted } from "vue"
import { NGrid, NGi, NCard, NStatistic, NNumberAnimation, NText, NTag, NSpin, useMessage } from "naive-ui"
import * as adminApi from "../../api/admin"
import type { AdminDashboard } from "../../types"
const msg = useMessage()
const loading = ref(true)
const dash = ref<AdminDashboard>({
  total_users: 0, total_messages: 0, online_users: 0,
  banned_users: 0, admin_users: 0, total_friendships: 0,
  pending_requests: 0, pending_appeals: 0, ai_enabled: true, messages_last_24h: 0, new_users_last_24h: 0,
})
onMounted(async () => {
  try { const data = await adminApi.getDashboard(); dash.value = data }
  catch (err: any) { msg.error(err.response?.data?.detail || err.message) }
  finally { loading.value = false }
})
</script>
<template>
  <NSpin :show="loading">
    <div class="dashboard">
      <NText class="page-title">控制台</NText>
      <NGrid :x-gap="16" :y-gap="16" :cols="2">
        <NGi :span="2">
          <NCard title="系统概览">
            <NGrid :x-gap="16" :y-gap="16" :cols="4">
              <NGi><NStatistic label="总用户数"><NNumberAnimation :from="0" :to="dash.total_users" /></NStatistic></NGi>
              <NGi><NStatistic label="在线用户"><NNumberAnimation :from="0" :to="dash.online_users" /></NStatistic></NGi>
              <NGi><NStatistic label="总消息数"><NNumberAnimation :from="0" :to="dash.total_messages" /></NStatistic></NGi>
              <NGi><NStatistic label="好友关系"><NNumberAnimation :from="0" :to="dash.total_friendships" /></NStatistic></NGi>
            </NGrid>
          </NCard>
        </NGi>
        <NGi><NCard title="用户统计">
          <div class="stat-row"><NText>管理员</NText><NTag type="warning" size="small">{{ dash.admin_users }}</NTag></div>
          <div class="stat-row"><NText>被封禁用户</NText><NTag type="error" size="small">{{ dash.banned_users }}</NTag></div>
          <div class="stat-row"><NText>待处理好友请求</NText><NTag type="info" size="small">{{ dash.pending_requests }}</NTag></div>
          <div class="stat-row"><NText>AI 助手</NText><NTag :type="dash.ai_enabled ? 'success' : 'default'" size="small">{{ dash.ai_enabled ? "已启用" : "已禁用" }}</NTag>
          </div>
          <div class="stat-row"><NText>待处理申诉</NText><NTag type="info" size="small">{{ dash.pending_appeals }}</NTag></div>
        </NCard></NGi>
        <NGi><NCard title="24 小时动态">
          <div class="stat-row"><NText>新增用户</NText><NTag type="success" size="small">{{ dash.new_users_last_24h }}</NTag></div>
          <div class="stat-row"><NText>新消息</NText><NTag type="info" size="small">{{ dash.messages_last_24h }}</NTag></div>
        </NCard></NGi>
      </NGrid>
    </div>
  </NSpin>
</template>
<style scoped>
.dashboard { max-width: 1000px; }
.page-title { font-size: 22px; font-weight: 700; display: block; margin-bottom: 20px; }
.stat-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.stat-row:last-child { border-bottom: none; }
</style>
