<script setup lang="ts">
import { ref, onMounted } from "vue"
import { NForm, NFormItem, NInput, NButton, NSwitch, NCard, NText, NSpin, useMessage, NSpace } from "naive-ui"
import * as adminApi from "../../api/admin"
import type { AdminSettings } from "../../types"
const msg = useMessage(); const loading = ref(true); const saving = ref(false)
const form = ref<AdminSettings>({
  ai_assistant_enabled: true, ai_assistant_username: "AI助手", ai_model: "deepseek-chat",
  ai_system_prompt: "", app_name: "Chat Room", access_token_expire_minutes: 30,
  refresh_token_expire_days: 7, max_upload_size: 10485760, max_file_size: 104857600,
})
onMounted(async () => {
  try { form.value = await adminApi.getSettings() }
  catch(e) { msg.error("获取失败") } finally { loading.value = false }
})
async function handleSave() {
  saving.value = true
  try {
    const r = await adminApi.updateSettings({
      ai_assistant_enabled: form.value.ai_assistant_enabled, ai_system_prompt: form.value.ai_system_prompt,
      ai_model: form.value.ai_model, app_name: form.value.app_name,
    }); form.value = r; msg.success("保存成功")
  } catch(e: any) { msg.error(e.response?.data?.detail || "保存失败") } finally { saving.value = false }
}
</script>
<template>
  <NSpin :show="loading">
    <div class="s"><NText class="pt">系统设置</NText>
      <NCard title="AI 助手设置" style="max-width:700px;margin-top:16px">
        <NForm label-placement="left" label-width="160">
          <NFormItem label="启用 AI"><NSwitch v-model:value="form.ai_assistant_enabled" /></NFormItem>
          <NFormItem label="AI 名称"><NInput v-model:value="form.ai_assistant_username" disabled /></NFormItem>
          <NFormItem label="模型"><NInput v-model:value="form.ai_model" placeholder="deepseek-chat" /></NFormItem>
          <NFormItem label="系统提示词"><NInput v-model:value="form.ai_system_prompt" type="textarea" :rows="4" /></NFormItem>
        </NForm>
      </NCard>
      <NCard title="应用设置" style="max-width:700px;margin-top:16px">
        <NForm label-placement="left" label-width="160">
          <NFormItem label="应用名称"><NInput v-model:value="form.app_name" /></NFormItem>
        </NForm>
      </NCard>
      <NSpace style="margin-top:20px">
        <NButton type="primary" :loading="saving" @click="handleSave">保存</NButton>
      </NSpace>
    </div>
  </NSpin>
</template>
<style scoped>
.s { max-width: 700px; }
.pt { font-size: 22px; font-weight: 700; display: block; }
</style>
