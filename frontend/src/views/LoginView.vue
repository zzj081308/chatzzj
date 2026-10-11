<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NInput, NButton, NModal, useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const animatedText = ref('')

const tagline = '随时随地，畅快聊天'
const subtitle = 'ChatZZJ · 连接每一刻'

onMounted(() => {
  // Typewriter effect for subtitle
  let i = 0
  const timer = setInterval(() => {
    if (i <= subtitle.length) {
      animatedText.value = subtitle.slice(0, i)
      i++
    } else {
      clearInterval(timer)
    }
  }, 80)
})

async function handleLogin() {
  if (!username.value || !password.value) {
    message.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    message.success('欢迎回来！')
    router.push('/chat')
  } catch (err: any) {
    message.error(err.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

// Appeal state
const showAppeal = ref(false)
const appealUsername = ref('')
const appealPassword = ref('')
const appealReason = ref('')
const appealStep = ref<'credentials' | 'reason' | 'result'>('credentials')
const appealStatus = ref('')
const appealError = ref('')
const appealSubmitting = ref(false)
const appealCheckLoading = ref(false)

function openAppeal() {
  showAppeal.value = true
  appealStep.value = 'credentials'
  appealUsername.value = ''
  appealPassword.value = ''
  appealReason.value = ''
  appealStatus.value = ''
  appealError.value = ''
}

async function checkAppealAccount() {
  if (!appealUsername.value || !appealPassword.value) {
    message.warning('请输入账号和密码')
    return
  }
  appealCheckLoading.value = true
  appealError.value = ''
  try {
    const res = await axios.post('/api/v1/appeals/check', {
      username: appealUsername.value,
      password: appealPassword.value,
      reason: '',
    })
    if (res.data.banned) {
      // Account is banned -> show reason form
      appealStep.value = 'reason'
    } else {
      appealError.value = res.data.message || '账号状态正常'
    }
  } catch (err: any) {
    appealError.value = err.response?.data?.detail || '验证失败'
  } finally {
    appealCheckLoading.value = false
  }
}

async function submitAppeal() {
  if (!appealReason.value.trim()) {
    message.warning('请输入申诉理由')
    return
  }
  appealSubmitting.value = true
  appealError.value = ''
  try {
    await axios.post('/api/v1/appeals/submit', {
      username: appealUsername.value,
      password: appealPassword.value,
      reason: appealReason.value,
    })
    appealStep.value = 'result'
    appealStatus.value = 'success'
    message.success('申诉已提交，请等待管理员处理')
    // Show result for 3 seconds then close
    setTimeout(() => { showAppeal.value = false }, 3000)
  } catch (err: any) {
    appealError.value = err.response?.data?.detail || '提交失败'
  } finally {
    appealSubmitting.value = false
  }
}

function resetAppeal() {
  appealStep.value = 'credentials'
  appealUsername.value = ''
  appealPassword.value = ''
  appealReason.value = ''
  appealError.value = ''
  appealStatus.value = ''
}

import axios from 'axios'
</script>

<template>
  <div class="auth-page">
    <!-- Animated background -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="shape shape-4"></div>
      <div class="shape shape-5"></div>
      <div class="shape shape-6"></div>
    </div>

    <!-- Main card -->
    <div class="auth-wrapper">
      <!-- Left: Brand panel -->
      <div class="brand-panel">
        <div class="brand-content">
          <div class="logo-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="48" height="48" rx="14" fill="url(#logo-grad)"/>
              <path d="M14 18a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-6a2 2 0 0 1-2-2V18z" fill="#fff" opacity="0.95"/>
              <path d="M24 22a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-6a2 2 0 0 1-2-2v-8z" fill="#fff" opacity="0.75"/>
              <circle cx="19" cy="20" r="1.5" fill="rgba(0,0,0,0.15)"/>
              <circle cx="31" cy="24" r="1.5" fill="rgba(0,0,0,0.15)"/>
              <defs>
                <linearGradient id="logo-grad" x1="0" y1="0" x2="48" y2="48">
                  <stop offset="0%" stop-color="#6366f1"/>
                  <stop offset="100%" stop-color="#8b5cf6"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="brand-name">ChatZZJ</h1>
          <p class="brand-tagline">{{ animatedText }}<span class="cursor">|</span></p>
          <p class="brand-desc">{{ tagline }}</p>
        </div>
        <div class="brand-dots">
          <span class="dot active"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>

      <!-- Right: Login form -->
      <div class="form-panel">
        <div class="form-header">
          <h2 class="form-title">欢迎登录</h2>
          <p class="form-subtitle">输入您的账号信息继续</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="input-group">
            <label class="input-label">用户名</label>
            <div class="input-icon-wrap">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
                </svg>
              </span>
              <NInput
                v-model:value="username"
                placeholder="请输入用户名"
                size="large"
                class="styled-input"
                :input-props="{ autocomplete: 'username' }"
              />
            </div>
          </div>

          <div class="input-group">
            <label class="input-label">密码</label>
            <div class="input-icon-wrap">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  <circle cx="12" cy="16" r="1"/>
                </svg>
              </span>
              <NInput
                v-model:value="password"
                type="password"
                placeholder="请输入密码"
                size="large"
                class="styled-input"
                :input-props="{ autocomplete: 'current-password' }"
                @keyup.enter="handleLogin"
              />
            </div>
          </div>

          <NButton
            type="primary"
            :loading="loading"
            block
            size="large"
            class="login-btn"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </NButton>

          <p style="text-align:center;margin-top:12px">
            <a @click="openAppeal" class="link" style="color:#e74c3c">申诉</a>
          </p>
          <p class="switch-link">
            还没有账号？
            <a @click="router.push('/register')" class="link">立即注册 →</a>
          </p>
        </form>
      </div>
    </div>
  </div>
  <!-- Appeal Modal -->
  <NModal v-model:show="showAppeal" title="账号申诉" preset="card" style="width:420px" :mask-closable="false">
    <div v-if="appealStep === 'credentials'">
      <p style="margin-bottom:16px;color:#666">请输入被封禁的账号和密码</p>
      <NInput v-model:value="appealUsername" placeholder="用户名" style="margin-bottom:12px" />
      <NInput v-model:value="appealPassword" type="password" placeholder="密码" style="margin-bottom:12px" @keyup.enter="checkAppealAccount" />
      <p v-if="appealError" style="color:#e74c3c;font-size:13px;margin-bottom:12px">{{ appealError }}</p>
      <NButton type="primary" block :loading="appealCheckLoading" @click="checkAppealAccount">验证账号</NButton>
    </div>
    <div v-else-if="appealStep === 'reason'">
      <p style="margin-bottom:16px;color:#666">请填写申诉理由，管理员会尽快处理</p>
      <NInput v-model:value="appealReason" type="textarea" placeholder="请说明被封禁的原因和申诉理由..." :rows="4" style="margin-bottom:12px" />
      <NButton type="primary" block :loading="appealSubmitting" @click="submitAppeal">提交申诉</NButton>
      <NButton text size="small" style="margin-top:8px" @click="resetAppeal">返回</NButton>
    </div>
    <div v-else-if="appealStep === 'result'">
      <p style="text-align:center;color:#52c41a;font-size:16px;margin:20px 0">申诉已提交</p>
      <p style="text-align:center;color:#666">请等待管理员处理，处理结果将通过申诉页面通知您</p>
    </div>
  </NModal>

</template>

<style scoped>
.auth-page {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 30%, #24243e 60%, #1a1a2e 100%);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ---- Animated background shapes ---- */
.bg-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.3;
  animation: float 12s ease-in-out infinite;
}
.shape-1 {
  width: 400px; height: 400px;
  background: #6366f1;
  top: -100px; left: -100px;
  animation-delay: 0s;
}
.shape-2 {
  width: 300px; height: 300px;
  background: #a855f7;
  bottom: -80px; right: -80px;
  animation-delay: -4s;
}
.shape-3 {
  width: 250px; height: 250px;
  background: #3b82f6;
  top: 40%; left: 60%;
  animation-delay: -8s;
}
.shape-4 {
  width: 200px; height: 200px;
  background: #ec4899;
  top: 10%; right: 20%;
  animation-delay: -2s;
}
.shape-5 {
  width: 180px; height: 180px;
  background: #14b8a6;
  bottom: 20%; left: 10%;
  animation-delay: -6s;
}
.shape-6 {
  width: 150px; height: 150px;
  background: #f59e0b;
  top: 30%; left: 30%;
  animation-delay: -10s;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.1); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(-30px, -10px) scale(1.05); }
}

/* ---- Card wrapper ---- */
.auth-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  width: 820px;
  min-height: 540px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

/* ---- Left brand panel ---- */
.brand-panel {
  flex: 0 0 380px;
  background: linear-gradient(160deg, rgba(99, 102, 241, 0.85) 0%, rgba(139, 92, 246, 0.9) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 50px 40px;
  position: relative;
  overflow: hidden;
}
.brand-panel::before {
  content: '';
  position: absolute;
  width: 300px; height: 300px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.1);
  top: -80px; right: -80px;
}
.brand-panel::after {
  content: '';
  position: absolute;
  width: 200px; height: 200px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.08);
  bottom: -60px; left: -60px;
}
.brand-content {
  text-align: center;
  color: #fff;
  position: relative;
  z-index: 1;
}
.logo-icon {
  margin-bottom: 24px;
  display: inline-block;
  filter: drop-shadow(0 8px 20px rgba(0,0,0,0.2));
}
.brand-name {
  font-size: 36px;
  font-weight: 800;
  margin: 0 0 12px;
  letter-spacing: 2px;
  text-shadow: 0 2px 10px rgba(0,0,0,0.15);
}
.brand-tagline {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 6px;
  min-height: 24px;
  letter-spacing: 1px;
}
.cursor {
  animation: blink-cursor 0.8s infinite;
  font-weight: 100;
}
@keyframes blink-cursor {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.brand-desc {
  font-size: 14px;
  opacity: 0.7;
  margin: 0;
}
.brand-dots {
  position: absolute;
  bottom: 30px;
  display: flex;
  gap: 8px;
}
.brand-dots .dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  transition: all 0.3s;
}
.brand-dots .dot.active {
  background: #fff;
  width: 24px;
  border-radius: 4px;
}

/* ---- Right form panel ---- */
.form-panel {
  flex: 1;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(20px);
  padding: 50px 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.form-header {
  margin-bottom: 36px;
}
.form-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px;
  color: #1a1a2e;
}
.form-subtitle {
  font-size: 14px;
  color: #888;
  margin: 0;
}
.login-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

/* ---- Input styling ---- */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.input-label {
  font-size: 13px;
  font-weight: 600;
  color: #444;
  margin-left: 2px;
}
.input-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 14px;
  z-index: 2;
  color: #999;
  display: flex;
  align-items: center;
  transition: color 0.2s;
  pointer-events: none;
}
.input-icon-wrap:focus-within .input-icon {
  color: #6366f1;
}
.styled-input {
  --n-padding-left: 42px !important;
  --n-border-radius: 10px !important;
  --n-border: 2px solid #e8e8e8 !important;
  transition: all 0.2s;
}
.styled-input :deep(.n-input:focus) {
  --n-border: 2px solid #6366f1 !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}
.styled-input :deep(.n-input-wrapper) {
  border-radius: 10px !important;
}

/* ---- Button ---- */
.login-btn {
  margin-top: 6px;
  height: 48px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  letter-spacing: 4px;
  border-radius: 10px !important;
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  border: none !important;
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35);
  transition: all 0.3s;
}
.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.45);
}
.login-btn:active {
  transform: translateY(0);
}

/* ---- Switch link ---- */
.switch-link {
  text-align: center;
  font-size: 14px;
  color: #999;
  margin: 0;
}
.link {
  color: #6366f1;
  cursor: pointer;
  font-weight: 600;
  transition: color 0.2s;
}
.link:hover {
  color: #4f46e5;
}

/* ---- Responsive ---- */
@media (max-width: 860px) {
  .auth-wrapper {
    flex-direction: column;
    width: 90%;
    min-height: auto;
  }
  .brand-panel {
    flex: 0 0 auto;
    padding: 36px 30px;
  }
  .brand-name { font-size: 28px; }
  .form-panel {
    padding: 36px 28px;
  }
}
</style>
