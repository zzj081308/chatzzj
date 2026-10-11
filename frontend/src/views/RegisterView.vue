<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NInput, NButton, useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!username.value || !email.value || !password.value) {
    message.warning('请填写所有字段')
    return
  }
  if (password.value !== confirmPassword.value) {
    message.warning('两次输入的密码不一致')
    return
  }
  if (password.value.length < 6) {
    message.warning('密码长度至少6个字符')
    return
  }
  loading.value = true
  try {
    await authStore.register(username.value, email.value, password.value)
    message.success('注册成功，欢迎加入！')
    router.push('/chat')
  } catch (err: any) {
    message.error(err.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
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
                  <stop offset="0%" stop-color="#f59e0b"/>
                  <stop offset="100%" stop-color="#ef4444"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="brand-name">Join Us</h1>
          <p class="brand-desc">创建一个新账号</p>
          <p class="brand-desc">开始你的聊天之旅</p>
        </div>
      </div>

      <!-- Right: Register form -->
      <div class="form-panel">
        <div class="form-header">
          <h2 class="form-title">创建账号</h2>
          <p class="form-subtitle">填写以下信息完成注册</p>
        </div>

        <form class="register-form" @submit.prevent="handleRegister">
          <div class="input-group">
            <label class="input-label">用户名</label>
            <div class="input-icon-wrap">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
                </svg>
              </span>
              <NInput v-model:value="username" placeholder="请输入用户名" size="large" class="styled-input" />
            </div>
          </div>

          <div class="input-group">
            <label class="input-label">邮箱</label>
            <div class="input-icon-wrap">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <rect x="2" y="4" width="20" height="16" rx="3"/>
                  <path d="M22 4L12 13 2 4"/>
                </svg>
              </span>
              <NInput v-model:value="email" placeholder="请输入邮箱地址" size="large" class="styled-input" />
            </div>
          </div>

          <div class="input-group">
            <label class="input-label">密码</label>
            <div class="input-icon-wrap">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              <NInput v-model:value="password" type="password" placeholder="至少6个字符" size="large" class="styled-input" />
            </div>
          </div>

          <div class="input-group">
            <label class="input-label">确认密码</label>
            <div class="input-icon-wrap">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <path d="M20 6L9 17l-5-5"/>
                </svg>
              </span>
              <NInput
                v-model:value="confirmPassword"
                type="password"
                placeholder="再次输入密码"
                size="large"
                class="styled-input"
                @keyup.enter="handleRegister"
              />
            </div>
          </div>

          <NButton
            type="primary"
            :loading="loading"
            block
            size="large"
            class="register-btn"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '注 册' }}
          </NButton>

          <p class="switch-link">
            已有账号？
            <a @click="router.push('/login')" class="link">立即登录 →</a>
          </p>
        </form>
      </div>
    </div>
  </div>
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
  background: #f59e0b;
  top: -100px; right: -80px;
  animation-delay: 0s;
}
.shape-2 {
  width: 300px; height: 300px;
  background: #ef4444;
  bottom: -80px; left: -80px;
  animation-delay: -4s;
}
.shape-3 {
  width: 250px; height: 250px;
  background: #10b981;
  top: 40%; left: 60%;
  animation-delay: -8s;
}
.shape-4 {
  width: 200px; height: 200px;
  background: #3b82f6;
  top: 10%; left: 15%;
  animation-delay: -2s;
}
.shape-5 {
  width: 180px; height: 180px;
  background: #ec4899;
  bottom: 20%; right: 10%;
  animation-delay: -6s;
}
.shape-6 {
  width: 150px; height: 150px;
  background: #6366f1;
  top: 50%; left: 40%;
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
  width: 860px;
  min-height: 620px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

/* ---- Left brand panel ---- */
.brand-panel {
  flex: 0 0 380px;
  background: linear-gradient(160deg, rgba(245, 158, 11, 0.85) 0%, rgba(239, 68, 68, 0.9) 100%);
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
  bottom: -80px; right: -80px;
}
.brand-panel::after {
  content: '';
  position: absolute;
  width: 200px; height: 200px;
  border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.08);
  top: -60px; left: -60px;
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
.brand-desc {
  font-size: 15px;
  opacity: 0.85;
  margin: 0 0 6px;
  letter-spacing: 1px;
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
.register-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
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
  color: #f59e0b;
}
.styled-input {
  --n-padding-left: 42px !important;
  --n-border-radius: 10px !important;
  --n-border: 2px solid #e8e8e8 !important;
  transition: all 0.2s;
}
.styled-input :deep(.n-input:focus) {
  --n-border: 2px solid #f59e0b !important;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}
.styled-input :deep(.n-input-wrapper) {
  border-radius: 10px !important;
}

/* ---- Button ---- */
.register-btn {
  margin-top: 6px;
  height: 48px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  letter-spacing: 4px;
  border-radius: 10px !important;
  background: linear-gradient(135deg, #f59e0b, #ef4444) !important;
  border: none !important;
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.35);
  transition: all 0.3s;
}
.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(245, 158, 11, 0.45);
}
.register-btn:active {
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
  color: #f59e0b;
  cursor: pointer;
  font-weight: 600;
  transition: color 0.2s;
}
.link:hover {
  color: #ef4444;
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
