<template>
    <div class="chat-window">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="chat-info">
          <el-avatar :size="40" :src="currentSession?.avatar"></el-avatar>
          <div class="chat-title">
            <h4>{{ currentSession?.title }}</h4>
            <span class="status">{{ currentSession?.status }}</span>
          </div>
        </div>
        <el-button type="text" @click="closeChat">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
  
      <!-- 消息区域 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-for="(message, index) in messages" :key="index" 
             :class="['message', message.sender === userStore.userInfo?.id ? 'own' : 'other']">
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>
  
      <!-- 输入区域 -->
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          placeholder="输入消息..."
          @keyup.enter="sendMessage"
          :disabled="!currentSession"
        >
          <template #append>
            <el-button :disabled="!inputMessage.trim()" @click="sendMessage">
              <el-icon><Promotion /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch, nextTick, onMounted } from 'vue'
  import { useUserStore } from '@/store/user'
  import { ChatStorage } from '@/utils/chatStorage'
  import { Close, Promotion } from '@element-plus/icons-vue'
  
  const props = defineProps({
    session: Object
  })
  
  const userStore = useUserStore()
  const messages = ref([])
  const inputMessage = ref('')
  const messagesContainer = ref(null)
  const currentSession = ref(props.session)
  
  // 加载聊天记录
  const loadMessages = () => {
    if (currentSession.value) {
      messages.value = ChatStorage.getChatMessages(currentSession.value.sessionId)
      scrollToBottom()
    }
  }
  
  // 发送消息
  const sendMessage = () => {
    if (!inputMessage.value.trim() || !currentSession.value) return
  
    const message = {
      id: Date.now(),
      content: inputMessage.value.trim(),
      sender: userStore.userInfo?.id,
      senderName: userStore.userName,
      timestamp: new Date().toISOString(),
      type: 'text'
    }
  
    ChatStorage.saveChatMessage(currentSession.value.sessionId, message)
    messages.value.push(message)
    inputMessage.value = ''
    
    nextTick(() => {
      scrollToBottom()
    })
  }
  
  // 滚动到底部
  const scrollToBottom = () => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }
  
  // 格式化时间
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // 关闭聊天
  const closeChat = () => {
    emit('close')
  }
  
  watch(() => props.session, (newSession) => {
    currentSession.value = newSession
    loadMessages()
  })
  
  onMounted(() => {
    ChatStorage.initChatStorage()
    loadMessages()
  })
  </script>
  
  <style scoped>
  .chat-window {
    display: flex;
    flex-direction: column;
    height: 100%;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    background: white;
  }
  
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #e4e7ed;
    background: #f5f7fa;
  }
  
  .chat-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .chat-title h4 {
    margin: 0;
    font-size: 16px;
  }
  
  .status {
    font-size: 12px;
    color: #67c23a;
  }
  
  .messages-container {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    background: #f9f9f9;
  }
  
  .message {
    display: flex;
    margin-bottom: 16px;
  }
  
  .message.own {
    justify-content: flex-end;
  }
  
  .message-content {
    max-width: 70%;
    padding: 12px;
    border-radius: 8px;
    position: relative;
  }
  
  .message.own .message-content {
    background: #409eff;
    color: white;
  }
  
  .message.other .message-content {
    background: white;
    border: 1px solid #e4e7ed;
  }
  
  .message-time {
    font-size: 12px;
    color: #999;
    margin-top: 4px;
    text-align: right;
  }
  
  .input-area {
    padding: 16px;
    border-top: 1px solid #e4e7ed;
  }
  </style>