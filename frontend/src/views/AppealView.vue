<script setup lang="ts">
import { ref } from "vue"
import { NCard, NInput, NButton, NText, NTag, useMessage, NSpace } from "naive-ui"
import axios from "axios"
import { useRouter } from "vue-router"
import type { Appeal } from "../types"

const router = useRouter()
const msg = useMessage()

const username = ref("")
const password = ref("")
const reason = ref("")
const step = ref<"login" | "appeal" | "result">("login")
const appeals = ref<Appeal[]>([])
const loading = ref(false)
const submitting = ref(false)
const error = ref("")
const checkResult = ref("")

async function checkAccount() {
  if (!username.value || !password.value) { msg.warning("请输入账号和密码"); return }
  loading.value = true; error.value = ""
  try {
    const res = await axios.post("/api/v1/appeals/check", { username: username.value, password: password.value, reason: "" })
    if (res.data.banned) {
      step.value = "appeal"
      await loadAppeals()
    } else {
      checkResult.value = res.data.message || "账号状态正常"
      error.value = ""
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || "验证失败"
  } finally { loading.value = false }
}

async function loadAppeals() {
  try {
    const res = await axios.post("/api/v1/appeals/my-appeals", { username: username.value, password: password.value, reason: "" })
    appeals.value = res.data
  } catch (e) {
    appeals.value = []
  }
}

async function submitAppeal() {
  if (!reason.value.trim()) { msg.warning("请输入申诉理由"); return }
  submitting.value = true; error.value = ""
  try {
    await axios.post("/api/v1/appeals/submit", { username: username.value, password: password.value, reason: reason.value })
    msg.success("申诉已提交，请等待管理员处理")
    reason.value = ""
    await loadAppeals()
  } catch (err: any) {
    error.value = err.response?.data?.detail || "提交失败"
  } finally { submitting.value = false }
}

function goBack() { step.value = "login"; appeals.value = []; reason.value = ""; error.value = "" }
</script>

<template>
  <div class="appeal-page">
    <div class="appeal-card">
      <div class="appeal-header">
        <NText class="appeal-title">账号申诉</NText>
        <NButton text size="small" @click="router.push('/login')">返回登录</NButton>
      </div>

      <div v-if="step === 'login'">
        <p style="color:#666;margin-bottom:16px">输入被封禁的账号和密码</p>
        <NInput v-model:value="username" placeholder="用户名" style="margin-bottom:12px" />
        <NInput v-model:value="password" type="password" placeholder="密码" style="margin-bottom:12px" @keyup.enter="checkAccount" />
        <p v-if="checkResult" style="color:#52c41a;font-size:13px;margin-bottom:12px">{{ checkResult }}</p>
        <p v-if="error" style="color:#e74c3c;font-size:13px;margin-bottom:12px">{{ error }}</p>
        <NButton type="primary" block :loading="loading" @click="checkAccount">验证账号</NButton>
      </div>

      <div v-else-if="step === 'appeal'">
        <p style="margin-bottom:12px">账号 <strong>{{ username }}</strong> 已被封禁</p>

        <div v-if="appeals.length > 0" style="margin-bottom:16px">
          <NText depth="3" style="font-size:13px">历史申诉记录：</NText>
          <NCard v-for="a in appeals" :key="a.id" size="small" style="margin-top:8px">
            <div class="appeal-item">
              <NTag :type="a.status === 'resolved' ? 'success' : a.status === 'rejected' ? 'error' : 'warning'" size="small">
                {{ a.status === 'pending' ? '待处理' : a.status === 'resolved' ? '已解封' : '已拒绝' }}
              </NTag>
              <NText depth="3" style="font-size:12px">{{ new Date(a.created_at).toLocaleString() }}</NText>
            </div>
            <p style="margin:6px 0;font-size:13px">{{ a.reason }}</p>
            <p v-if="a.admin_response" style="margin:4px 0;font-size:12px;color:#e74c3c">回复：{{ a.admin_response }}</p>
          </NCard>
        </div>

        <p style="color:#666;margin-bottom:8px">提交新的申诉：</p>
        <NInput type="textarea" v-model:value="reason" placeholder="请说明申诉理由..." :rows="4" style="margin-bottom:12px" />
        <p v-if="error" style="color:#e74c3c;font-size:13px;margin-bottom:8px">{{ error }}</p>
        <NSpace>
          <NButton type="primary" :loading="submitting" @click="submitAppeal">提交申诉</NButton>
          <NButton @click="goBack">返回</NButton>
        </NSpace>
      </div>
    </div>
  </div>
</template>

<style scoped>
.appeal-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f5f6fa; }
.appeal-card { width: 460px; background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.appeal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.appeal-title { font-size: 20px; font-weight: 700; }
.appeal-item { display: flex; justify-content: space-between; align-items: center; }
</style>
