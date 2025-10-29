<template>
  <div class="ai-settings">
    <section class="page-hero">
      <div class="hero-copy">
        <div class="hero-label">智能学习助手</div>
        <h2>AI 助手配置中心</h2>
        <p>统一管理模型来源、参数与访问策略，让代码训练营拥有持续进化的智能助教。</p>
        <div class="hero-stats">
          <div v-for="stat in heroStats" :key="stat.label" class="stat-item">
            <span class="stat-label">{{ stat.label }}</span>
            <strong>{{ stat.value }}</strong>
          </div>
        </div>
      </div>
      <div class="hero-status">
        <el-tag :type="heroStatusTag" effect="dark" class="status-tag">{{ heroStatusText }}</el-tag>
        <p>当前服务商：{{ currentProviderMeta?.label || '未选择' }}</p>
        <p>接口端点：{{ form.api_endpoint }}</p>
      </div>
    </section>

    <section class="config-grid">
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <div>
              <h3>连接设置</h3>
              <small>配置模型来源、鉴权信息与推理参数</small>
            </div>
            <el-tag v-if="currentProviderMeta" type="info">{{ currentProviderMeta.label }}</el-tag>
          </div>
        </template>

        <el-alert
          v-if="currentProviderMeta?.description"
          :title="currentProviderMeta.description"
          type="info"
          :closable="false"
          show-icon
          class="provider-alert"
        />

        <el-form
          :model="form"
          label-position="top"
          @submit.prevent="saveConfig"
          class="config-form"
        >
          <el-row :gutter="20">
            <el-col :md="12" :sm="24">
              <el-form-item label="AI 服务商">
                <el-select v-model="form.provider" placeholder="选择 AI 服务商" class="w-full">
                  <el-option
                    v-for="option in providerOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :md="12" :sm="24">
              <el-form-item label="连接端点">
                <el-input
                  v-model="form.api_endpoint"
                  :placeholder="currentProviderMeta?.defaultEndpoint || 'https://api.example.com'"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20" v-if="requiresApiKey">
            <el-col :span="24">
              <el-form-item label="API 密钥">
                <el-input v-model="form.api_key" type="password" show-password placeholder="输入 API 密钥" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :md="12" :sm="24">
              <el-form-item label="模型名称">
                <template v-if="isOllamaProvider">
                  <el-select
                    v-model="form.model_name"
                    placeholder="选择本地 Ollama 模型"
                    class="w-full"
                    filterable
                    :loading="modelsLoading"
                    loading-text="同步模型列表..."
                    no-data-text="暂无可用模型"
                    @visible-change="handleModelDropdown"
                  >
                    <el-option
                      v-for="model in availableModels"
                      :key="model.name"
                      :label="model.display_name || model.name"
                      :value="model.name"
                    >
                      <div class="model-option">
                        <span class="option-name">{{ model.display_name || model.name }}</span>
                        <span v-if="model.size" class="option-extra">{{ model.size }}</span>
                      </div>
                    </el-option>
                  </el-select>
                  <p v-if="modelsError" class="form-tip error-tip">{{ modelsError }}</p>
                </template>
                <template v-else>
                  <el-input v-model="form.model_name" placeholder="llama3, gpt-4o-mini 等" />
                </template>
              </el-form-item>
            </el-col>
            <el-col :md="12" :sm="24">
              <el-form-item label="最大 Tokens">
                <el-input-number v-model="form.max_tokens" :min="100" :max="16000" :step="100" class="w-full" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :md="12" :sm="24">
              <el-form-item label="输出温度">
                <el-slider v-model="form.temperature" :min="0" :max="1.5" :step="0.1" show-stops />
                <span class="form-tip">值越高越有创造力，越低越稳定</span>
              </el-form-item>
            </el-col>
            <el-col :md="12" :sm="24">
              <el-form-item label="服务开关">
                <div class="switch-row">
                  <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <div class="form-actions">
          <div class="actions-left">
            <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
            <el-button @click="testConfig" :loading="testing">测试连通性</el-button>
          </div>
          <p class="autosave-tip">配置将同步保存至后端，可供团队协作共享</p>
        </div>
      </el-card>

      <div class="side-column">
        <el-card class="info-card">
          <template #header>
            <div class="card-header compact">
              <h3>诊断记录</h3>
              <small>最近 24 小时</small>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="item in diagnostics"
              :key="item.id"
              :type="timelineTypeMap[item.status]"
              :timestamp="item.time"
            >
              <h4>{{ item.title }}</h4>
              <p>{{ item.message }}</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <el-card class="tips-card">
          <template #header>
            <div class="card-header compact">
              <h3>最佳实践</h3>
            </div>
          </template>
          <ul class="tips-list">
            <li>优先使用本地 Ollama 调试，降低推理成本</li>
            <li>为生产环境配置速率限制与监控告警</li>
            <li>定期更新模型版本，保持回答质量领先</li>
          </ul>
        </el-card>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const providerOptions = [
  {
    label: 'Ollama 本地',
    value: 'ollama_local',
    defaultEndpoint: 'http://localhost:11434',
    description: '适合个人开发环境，离线推理性能优秀，建议搭配 GPU 环境使用。'
  },
  {
    label: 'Ollama 远程',
    value: 'ollama_remote',
    defaultEndpoint: 'https://api.ollama.yourdomain.com',
    description: '适合团队共享的内网模型集群，统一治理模型资源与权限。'
  },
  {
    label: 'DeepSeek',
    value: 'deepseek',
    defaultEndpoint: 'https://api.deepseek.com',
    description: '国产大模型代表，推理成本低，适合量大高频的内容生成类任务。'
  },
  {
    label: 'OpenAI',
    value: 'openai',
    defaultEndpoint: 'https://api.openai.com',
    description: '业界通用模型接口，生态成熟，适合需要多模态能力的高阶场景。'
  }
]

const defaultForm = {
  provider: 'ollama_local',
  api_endpoint: 'http://localhost:11434',
  api_key: '',
  model_name: 'qwen3:8b',
  temperature: 0.7,
  max_tokens: 2000,
  is_active: true
}

const form = ref({ ...defaultForm })

const saving = ref(false)
const testing = ref(false)
const configId = ref(null)
const availableModels = ref([])
const modelsLoading = ref(false)
const modelsError = ref('')
const modelListLoadedOnce = ref(false)

const formatTimestamp = () =>
  new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date())

const diagnostics = ref([
  {
    id: Date.now(),
    title: '配置中心已初始化',
    message: '使用默认的本地 Ollama 配置，可立即开始调试。',
    status: 'info',
    time: formatTimestamp()
  }
])

const isOllamaProvider = computed(() => form.value.provider?.startsWith('ollama'))

const timelineTypeMap = {
  success: 'success',
  error: 'danger',
  info: 'info',
  warning: 'warning'
}

const currentProviderMeta = computed(() =>
  providerOptions.find((option) => option.value === form.value.provider)
)

const requiresApiKey = computed(() => ['deepseek', 'openai'].includes(form.value.provider))

const heroStats = computed(() => {
  const temperature = Number(form.value.temperature ?? 0)
  return [
    { label: '当前模型', value: form.value.model_name || '未设置' },
    { label: '温度', value: temperature.toFixed(1) },
    { label: '最大 Tokens', value: form.value.max_tokens ?? '—' }
  ]
})

const heroStatusText = computed(() => (form.value.is_active ? '服务已启用' : '服务未启用'))
const heroStatusTag = computed(() => (form.value.is_active ? 'success' : 'warning'))

const handleModelDropdown = (visible) => {
  if (visible && isOllamaProvider.value && (!availableModels.value.length || modelsError.value)) {
    fetchAvailableModels({ preferExisting: true })
  }
}

const fetchAvailableModels = async ({ preferExisting = true, silent = false } = {}) => {
  if (!isOllamaProvider.value) {
    availableModels.value = []
    modelsError.value = ''
    return
  }

  modelsLoading.value = true
  modelsError.value = ''

  try {
    const params = {
      provider: form.value.provider,
      api_endpoint: form.value.api_endpoint
    }
    const res = await axios.get('/api/courses/ai-config/models/', { params })
    const rawItems = res.data?.models || []
    const warningMessage = res.data?.warning
    const items = rawItems.map((item) =>
      typeof item === 'string'
        ? { name: item, display_name: item }
        : { ...item, name: item.name || item.model || item.id }
    ).filter((item) => item.name)

    availableModels.value = items

    const currentName = form.value.model_name
    const preferred = items.find((item) => item.name === currentName)

    if (!preferred || !preferExisting) {
      const defaultPick = items.find((item) => item.name === 'qwen3:8b') || items[0]
      if (defaultPick) {
        form.value.model_name = defaultPick.name
      }
    }

    if (items.length) {
      modelListLoadedOnce.value = true
    }

    if (!silent && items.length && !warningMessage) {
      pushDiagnostic({
        title: '模型列表已同步',
        message: `检测到 ${items.length} 个可用模型。`,
        status: 'success'
      })
    }

    if (!silent && warningMessage) {
      pushDiagnostic({
        title: '使用默认模型列表',
        message: `${warningMessage} (共 ${items.length} 个默认选项)`,
        status: 'warning'
      })
    }
  } catch (error) {
    const message = error.response?.data?.detail || error.message || '无法获取模型列表'
    modelsError.value = message
    if (!silent) {
      pushDiagnostic({
        title: '获取模型失败',
        message,
        status: 'error'
      })
    }
  } finally {
    modelsLoading.value = false
  }
}

const pushDiagnostic = (entry) => {
  diagnostics.value = [
    {
      id: Date.now(),
      time: formatTimestamp(),
      ...entry
    },
    ...diagnostics.value
  ].slice(0, 6)
}

onMounted(() => {
  loadConfig()
})

watch(
  () => [form.value.provider, form.value.api_endpoint],
  () => {
    const wasLoaded = modelListLoadedOnce.value
    modelListLoadedOnce.value = false
    if (isOllamaProvider.value) {
      fetchAvailableModels({ preferExisting: true, silent: wasLoaded })
    } else {
      availableModels.value = []
      modelsError.value = ''
    }
  }
)

const loadConfig = async () => {
  try {
    const res = await axios.get('/api/courses/ai-config/current/')
    form.value = { ...defaultForm, ...res.data }
    configId.value = res.data.id
    pushDiagnostic({
      title: '已加载云端配置',
      message: `成功同步 ${res.data.provider} 的配置项。`,
      status: 'success'
    })
    if (!res.data.model_name && res.data.provider?.startsWith('ollama')) {
      form.value.model_name = 'qwen3:8b'
    }
  } catch (error) {
    pushDiagnostic({
      title: '使用默认配置',
      message: '未检测到历史记录，已回退为默认本地推理。',
      status: 'info'
    })
  } finally {
    fetchAvailableModels({ preferExisting: true, silent: true })
  }
}

const saveConfig = async () => {
  saving.value = true

  try {
    if (configId.value) {
      await axios.put(`/api/courses/ai-config/${configId.value}/`, form.value)
      ElMessage.success('配置更新成功')
      pushDiagnostic({
        title: '配置已更新',
        message: `已应用 ${form.value.provider} 的最新设置。`,
        status: 'success'
      })
    } else {
      const res = await axios.post('/api/courses/ai-config/', form.value)
      configId.value = res.data.id
      ElMessage.success('配置保存成功')
      pushDiagnostic({
        title: '配置已保存',
        message: '首次保存成功，建议立即执行连通性测试。',
        status: 'success'
      })
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
    pushDiagnostic({
      title: '保存失败',
      message: error.response?.data?.detail || error.message,
      status: 'error'
    })
  } finally {
    saving.value = false
  }
}

const testConfig = async () => {
  if (!configId.value) {
    ElMessage.warning('请先保存配置')
    pushDiagnostic({
      title: '测试未执行',
      message: '请先保存配置后再进行连通性测试。',
      status: 'info'
    })
    return
  }

  testing.value = true

  try {
    const res = await axios.post(`/api/courses/ai-config/${configId.value}/test/`)
    ElMessage.success('连接成功！')
    const snippet = String(res.data?.response || '接口响应正常').slice(0, 60)
    pushDiagnostic({
      title: '连通性测试成功',
      message: snippet,
      status: 'success'
    })
  } catch (error) {
    ElMessage.error('连接失败: ' + (error.response?.data?.error || error.message))
    pushDiagnostic({
      title: '连通性测试失败',
      message: error.response?.data?.error || error.message,
      status: 'error'
    })
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.ai-settings {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.page-hero {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 20px;
  padding: 32px 36px;
  border-radius: 26px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.14), rgba(56, 189, 248, 0.16), rgba(236, 72, 153, 0.18));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 30px 60px rgba(79, 70, 229, 0.18);
  position: relative;
  overflow: hidden;
}

.page-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% -10%, rgba(255, 255, 255, 0.45), transparent 45%);
  pointer-events: none;
}

.hero-copy {
  max-width: 540px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: #0f172a;
  position: relative;
  z-index: 1;
}

.hero-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  font-weight: 600;
  color: #1e293b;
  width: fit-content;
}

.hero-label::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: linear-gradient(135deg, #38bdf8, #ec4899);
}

.hero-copy h2 {
  font-size: 30px;
  font-weight: 700;
  margin: 0;
}

.hero-copy p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: rgba(15, 23, 42, 0.78);
}

.hero-stats {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
}

.stat-item {
  backdrop-filter: blur(14px);
  background: rgba(255, 255, 255, 0.78);
  border-radius: 18px;
  padding: 14px 18px;
  min-width: 120px;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.12);
}

.stat-label {
  display: block;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.55);
  margin-bottom: 6px;
}

.stat-item strong {
  font-size: 20px;
  color: #1e293b;
}

.hero-status {
  min-width: 240px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
  position: relative;
  z-index: 1;
  color: rgba(15, 23, 42, 0.82);
}

.status-tag {
  border-radius: 999px;
  padding: 0 12px;
  height: 32px;
}

.config-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}

@media (max-width: 1100px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
}

.form-card,
.info-card,
.tips-card {
  border-radius: 24px;
  border: none;
  box-shadow: 0 30px 60px rgba(15, 23, 42, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #0f172a;
}

.card-header small {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  color: #64748b;
}

.card-header.compact {
  flex-direction: column;
  align-items: flex-start;
}

.provider-alert {
  margin-bottom: 18px;
  border-radius: 16px;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.w-full {
  width: 100%;
}

.switch-row {
  display: flex;
  align-items: center;
  height: 48px;
}

.form-tip {
  font-size: 12px;
  color: #64748b;
  margin-top: 8px;
}

.error-tip {
  color: #ef4444;
}

.form-actions {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.actions-left {
  display: flex;
  gap: 12px;
}

.autosave-tip {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.side-column {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #475569;
}

.tips-list li::before {
  content: '•';
  color: #6366f1;
  margin-right: 8px;
}

.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.option-name {
  font-size: 14px;
  color: #0f172a;
}

.option-extra {
  font-size: 12px;
  color: #94a3b8;
}

.info-card :deep(.el-timeline-item__content h4) {
  margin: 0 0 6px;
  font-size: 14px;
  color: #0f172a;
}

.info-card :deep(.el-timeline-item__content p) {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}
</style>
