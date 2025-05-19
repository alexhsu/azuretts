<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { Download } from '@element-plus/icons-vue'

const text = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)
const audioFiles = ref([])
const batchId = ref('')

const handleSubmit = async () => {
  error.value = ''
  success.value = false
  audioFiles.value = []
  if (!text.value.trim()) {
    error.value = '请输入文本内容'
    return
  }
  loading.value = true
  try {
    const res = await axios.post('/api/tts', { text: text.value })
    if (res.data && res.data.success && res.data.files) {
      audioFiles.value = res.data.files.map(file => ({
        ...file,
        audioUrl: `/api/audio/${file.file_path.split('/').pop()}`
      }))
      batchId.value = res.data.batch_id
      success.value = true
    } else {
      error.value = res.data.error || '生成失败'
    }
  } catch (e) {
    error.value = e?.response?.data?.error || e.message || '请求失败'
  }
  loading.value = false
}
</script>

<template>
  <div class="app-container">
    <el-container>
      <el-main>
        <div class="content-wrapper">
          <el-card class="main-card" :body-style="{ padding: '30px' }">
            <div class="header">
              <h1 class="title">文本转语音</h1>
              <p class="subtitle">将您的文本转换为自然流畅的语音</p>
            </div>
            
            <el-form @submit.prevent="handleSubmit" class="form-container">
              <el-form-item>
                <el-input
                  type="textarea"
                  v-model="text"
                  :rows="8"
                  placeholder="请输入要转换的文本内容，每行将生成一个音频文件..."
                  class="text-input"
                  resize="none"
                />
              </el-form-item>
              
              <el-form-item class="button-container">
                <el-button 
                  type="primary" 
                  :loading="loading" 
                  @click="handleSubmit"
                  class="submit-button"
                  size="large"
                >
                  {{ loading ? '生成中...' : '生成语音' }}
                </el-button>
              </el-form-item>
            </el-form>

            <transition name="fade">
              <el-alert
                v-if="error"
                :title="error"
                type="error"
                show-icon
                class="alert-message"
              />
            </transition>

            <transition name="fade">
              <el-alert
                v-if="success"
                :title="`成功生成 ${audioFiles.length} 个音频文件`"
                type="success"
                show-icon
                class="alert-message"
              />
            </transition>

            <transition name="slide-fade">
              <div v-if="audioFiles.length > 0" class="audio-container">
                <div class="audio-header-actions">
                  <a 
                    :href="`/api/download-all/${batchId}`" 
                    class="download-all-link"
                  >
                    <el-button 
                      type="primary" 
                      class="download-all-button"
                      size="small"
                    >
                      <el-icon><Download /></el-icon>
                      下载全部音频
                    </el-button>
                  </a>
                </div>
                <div v-for="file in audioFiles" :key="file.line_number" class="audio-item">
                  <div class="audio-header">
                    <span class="line-number">第 {{ file.line_number }} 行</span>
                    <span class="line-text">{{ file.text }}</span>
                  </div>
                  <div class="audio-player">
                    <audio :src="file.audioUrl" controls class="audio-element" />
                  </div>
                  <a 
                    :href="file.audioUrl" 
                    download
                    class="download-link"
                  >
                    <el-button 
                      type="success" 
                      class="download-button"
                      size="small"
                    >
                      <el-icon><Download /></el-icon>
                      下载音频
                    </el-button>
                  </a>
                </div>
              </div>
            </transition>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<style>
body {
  margin: 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  overflow-x: hidden;
  min-width: 1280px;
}

.app-container {
  min-height: 100vh;
  width: 100%;
  min-width: 1280px;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  overflow-x: hidden;
}

.el-container {
  width: 100%;
  min-width: 1280px;
  min-height: 100vh;
  overflow-x: hidden;
}

.el-main {
  padding: 0;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  overflow-x: hidden;
  min-width: 1280px;
}

.content-wrapper {
  width: 100%;
  min-width: 1280px;
  height: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

.main-card {
  flex: 1;
  border-radius: 0;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  margin: 0;
  overflow-x: hidden;
  min-width: 1280px;
}

.main-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: clamp(20px, 5vw, 50px);
  overflow-x: hidden;
  min-width: 1280px;
}

.header {
  text-align: center;
  margin-bottom: clamp(30px, 6vw, 60px);
  width: 100%;
}

.title {
  color: #2c3e50;
  font-size: clamp(2.2em, 5vw, 3.2em);
  margin: 0 0 15px 0;
  font-weight: 600;
  word-break: break-word;
}

.subtitle {
  color: #606266;
  font-size: clamp(1.1em, 2.5vw, 1.4em);
  margin: 0;
  word-break: break-word;
}

.form-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-top: clamp(25px, 4vw, 40px);
  width: 100%;
}

.text-input {
  flex: 1;
  font-size: clamp(1.2em, 2.5vw, 1.5em);
  width: 100%;
}

.text-input :deep(.el-textarea__inner) {
  height: 100%;
  border-radius: clamp(8px, 2vw, 12px);
  padding: clamp(16px, 3vw, 24px);
  font-size: clamp(1.2em, 2.5vw, 1.5em);
  line-height: 1.6;
  min-height: clamp(200px, 40vh, 400px);
  transition: all 0.3s ease;
  width: 100%;
  box-sizing: border-box;
}

.text-input :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: clamp(25px, 4vw, 40px);
  width: 100%;
}

.submit-button {
  padding: clamp(12px, 3vw, 16px) clamp(36px, 6vw, 48px);
  font-size: clamp(1.2em, 2.5vw, 1.4em);
  border-radius: clamp(8px, 2vw, 12px);
  transition: all 0.3s ease;
  white-space: nowrap;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.alert-message {
  margin-top: clamp(25px, 4vw, 40px);
  border-radius: clamp(8px, 2vw, 12px);
  font-size: clamp(1.1em, 2.2vw, 1.3em);
  width: 100%;
  box-sizing: border-box;
}

.audio-container {
  margin-top: clamp(30px, 5vw, 50px);
  padding: clamp(20px, 4vw, 40px);
  background: #f8f9fa;
  border-radius: clamp(12px, 3vw, 24px);
  flex: 1;
  overflow-y: auto;
  width: 100%;
  box-sizing: border-box;
}

.audio-header-actions {
  margin-bottom: clamp(20px, 4vw, 40px);
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.download-all-link {
  text-decoration: none;
}

.download-all-button {
  padding: clamp(10px, 2vw, 12px) clamp(20px, 3vw, 24px);
  font-size: clamp(1.1em, 2.2vw, 1.3em);
  border-radius: clamp(8px, 2vw, 12px);
  transition: all 0.3s ease;
  white-space: nowrap;
}

.download-all-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.audio-item {
  margin-bottom: clamp(20px, 4vw, 40px);
  padding: clamp(16px, 3vw, 24px);
  background: white;
  border-radius: clamp(8px, 2vw, 12px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  width: 100%;
  box-sizing: border-box;
}

.audio-item:last-child {
  margin-bottom: 0;
}

.audio-header {
  margin-bottom: clamp(12px, 2vw, 16px);
  display: flex;
  align-items: center;
  gap: clamp(12px, 2vw, 16px);
  width: 100%;
  flex-wrap: wrap;
}

.line-number {
  background: #409eff;
  color: white;
  padding: clamp(4px, 1vw, 6px) clamp(10px, 2vw, 12px);
  border-radius: clamp(4px, 1vw, 6px);
  font-size: clamp(1em, 2vw, 1.2em);
  white-space: nowrap;
}

.line-text {
  color: #606266;
  font-size: clamp(1.1em, 2.2vw, 1.3em);
  word-break: break-word;
  flex: 1;
}

.audio-player {
  margin-bottom: clamp(12px, 2vw, 16px);
  width: 100%;
}

.audio-element {
  width: 100%;
  border-radius: clamp(8px, 2vw, 12px);
}

.download-link {
  text-decoration: none;
  display: block;
  width: 100%;
}

.download-button {
  width: 100%;
  padding: clamp(10px, 2vw, 12px);
  font-size: clamp(1.1em, 2.2vw, 1.3em);
  border-radius: clamp(8px, 2vw, 12px);
  transition: all 0.3s ease;
}

.download-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* 响应式布局调整 */
@media screen and (max-width: 768px) {
  .content-wrapper {
    width: 100%;
  }
  
  .audio-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .line-number {
    margin-bottom: 12px;
  }
}
</style>
