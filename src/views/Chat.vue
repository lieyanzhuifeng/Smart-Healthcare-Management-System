<template>
    <div class="chat-container">
      <!-- 聊天侧边栏 -->
      <ChatList 
        @select-session="handleSelectSession"
        @new-chat="handleNewChat"
      />
      
      <!-- 聊天主窗口 -->
      <div class="chat-main">
        <div v-if="currentSession" class="chat-window-wrapper">
          <ChatWindow 
            :session="currentSession"
            @close="currentSession = null"
          />
        </div>
        
        <div v-else class="welcome-screen">
          <el-icon :size="64"><ChatLineRound /></el-icon>
          <h3>欢迎使用在线咨询</h3>
          <p>选择一个会话开始聊天，或创建新的咨询</p>
          <el-button type="primary" @click="handleNewChat">
            开始新的咨询
          </el-button>
        </div>
      </div>
  
      <!-- 新建聊天对话框 -->
      <el-dialog
        v-model="showNewChatDialog"
        title="新建咨询"
        width="400px"
      >
        <el-form :model="newChatForm" label-width="80px">
          <el-form-item label="咨询对象">
            <el-select v-model="newChatForm.targetType" placeholder="请选择">
              <el-option label="医生" value="doctor" />
              <el-option label="药师" value="pharmacy" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="选择医生" v-if="newChatForm.targetType === 'doctor'">
            <el-select v-model="newChatForm.doctorId" placeholder="请选择医生">
              <el-option 
                v-for="doctor in doctors" 
                :key="doctor.id"
                :label="doctor.name"
                :value="doctor.id"
              />
            </el-select>
          </el-form-item>
  
          <el-form-item label="咨询主题">
            <el-input 
              v-model="newChatForm.title" 
              placeholder="请输入咨询主题"
            />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showNewChatDialog = false">取消</el-button>
          <el-button type="primary" @click="createChatSession">确定</el-button>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { ElMessage } from 'element-plus'
  import { useUserStore } from '@/store/user'
  import { ChatStorage } from '@/utils/chatStorage'
  import ChatList from '@/components/ChatList.vue'
  import ChatWindow from '@/components/ChatWindow.vue'
  import { ChatLineRound } from '@element-plus/icons-vue'
  
  const userStore = useUserStore()
  const currentSession = ref(null)
  const showNewChatDialog = ref(false)
  const newChatForm = ref({
    targetType: '',
    doctorId: '',
    title: ''
  })
  
  // 模拟医生数据
  const doctors = ref([
    { id: 'doc1', name: '张医生', department: '内科' },
    { id: 'doc2', name: '李医生', department: '外科' },
    { id: 'doc3', name: '王医生', department: '儿科' }
  ])
  
  // 选择会话
  const handleSelectSession = (session) => {
    currentSession.value = session
  }
  
  // 新建聊天
  const handleNewChat = () => {
    showNewChatDialog.value = true
    newChatForm.value = {
      targetType: '',
      doctorId: '',
      title: ''
    }
  }
  
  // 创建聊天会话
  const createChatSession = () => {
    if (!newChatForm.value.title.trim()) {
      ElMessage.warning('请输入咨询主题')
      return
    }
  
    const sessionId = `chat_${Date.now()}`
    const selectedDoctor = doctors.value.find(d => d.id === newChatForm.value.doctorId)
    
    const session = {
      sessionId: sessionId,
      title: newChatForm.value.title,
      targetType: newChatForm.value.targetType,
      targetId: newChatForm.value.doctorId,
      targetName: selectedDoctor ? selectedDoctor.name : '药师',
      avatar: selectedDoctor ? '/avatars/doctor.png' : '/avatars/pharmacy.png',
      status: '在线',
      lastMessageTime: new Date().toISOString(),
      lastMessage: '',
      createdTime: new Date().toISOString()
    }
  
    ChatStorage.saveChatSession(session)
    currentSession.value = session
    showNewChatDialog.value = false
    
    ElMessage.success('咨询会话创建成功')
  }
  
  // 初始化聊天存储
  ChatStorage.initChatStorage()
  </script>
  
  <style scoped>
  .chat-container {
    display: flex;
    height: 100vh;
    background: #f5f7fa;
  }
  
  .chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
  }
  
  .chat-window-wrapper {
    flex: 1;
    display: flex;
  }
  
  .welcome-screen {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #999;
  }
  
  .welcome-screen h3 {
    margin: 16px 0 8px;
    color: #333;
  }
  
  .welcome-screen p {
    margin-bottom: 24px;
  }
  </style>