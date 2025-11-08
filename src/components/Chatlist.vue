<template>
    <div class="chat-list">
      <div class="chat-header">
        <h3>聊天会话</h3>
        <el-button type="primary" size="small" @click="createNewChat">
          <el-icon><Plus /></el-icon>
          新建聊天
        </el-button>
      </div>
  
      <div class="search-area">
        <el-input
          v-model="searchText"
          placeholder="搜索会话..."
          prefix-icon="Search"
          size="small"
        />
      </div>
  
      <div class="sessions-list">
        <div
          v-for="session in filteredSessions"
          :key="session.sessionId"
          :class="['session-item', { active: activeSession?.sessionId === session.sessionId }]"
          @click="selectSession(session)"
        >
          <el-avatar :size="40" :src="session.avatar"></el-avatar>
          <div class="session-info">
            <div class="session-title">{{ session.title }}</div>
            <div class="session-preview">{{ session.lastMessage || '暂无消息' }}</div>
          </div>
          <div class="session-time">{{ formatTime(session.lastMessageTime) }}</div>
        </div>
  
        <div v-if="filteredSessions.length === 0" class="empty-state">
          <el-icon><ChatLineRound /></el-icon>
          <p>暂无聊天会话</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { ChatStorage } from '@/utils/chatStorage'
  import { Plus, Search, ChatLineRound } from '@element-plus/icons-vue'
  
  const emit = defineEmits(['select-session', 'new-chat'])
  
  const sessions = ref([])
  const searchText = ref('')
  const activeSession = ref(null)
  
  // 加载会话列表
  const loadSessions = () => {
    sessions.value = ChatStorage.getChatSessions()
  }
  
  // 过滤会话
  const filteredSessions = computed(() => {
    if (!searchText.value) return sessions.value
    return sessions.value.filter(session => 
      session.title.toLowerCase().includes(searchText.value.toLowerCase())
    )
  })
  
  // 选择会话
  const selectSession = (session) => {
    activeSession.value = session
    emit('select-session', session)
  }
  
  // 创建新聊天
  const createNewChat = () => {
    emit('new-chat')
  }
  
  // 格式化时间
  const formatTime = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    if (diff < 60 * 60 * 1000) { // 1小时内
      return Math.floor(diff / (60 * 1000)) + '分钟前'
    } else if (diff < 24 * 60 * 60 * 1000) { // 1天内
      return Math.floor(diff / (60 * 60 * 1000)) + '小时前'
    } else {
      return date.toLocaleDateString('zh-CN')
    }
  }
  
  onMounted(() => {
    ChatStorage.initChatStorage()
    loadSessions()
  })
  </script>
  
  <style scoped>
  .chat-list {
    width: 300px;
    height: 100%;
    border-right: 1px solid #e4e7ed;
    background: white;
    display: flex;
    flex-direction: column;
  }
  
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .chat-header h3 {
    margin: 0;
    font-size: 16px;
  }
  
  .search-area {
    padding: 16px;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .sessions-list {
    flex: 1;
    overflow-y: auto;
  }
  
  .session-item {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
    transition: background-color 0.2s;
  }
  
  .session-item:hover {
    background: #f5f7fa;
  }
  
  .session-item.active {
    background: #e6f7ff;
    border-right: 3px solid #409eff;
  }
  
  .session-info {
    flex: 1;
    margin-left: 12px;
    min-width: 0;
  }
  
  .session-title {
    font-weight: 500;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .session-preview {
    font-size: 12px;
    color: #999;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .session-time {
    font-size: 12px;
    color: #999;
    white-space: nowrap;
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #999;
  }
  
  .empty-state .el-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  </style>