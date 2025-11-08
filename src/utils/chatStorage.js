// 聊天记录存储管理工具
export class ChatStorage {
    // 初始化聊天存储
    static initChatStorage() {
      if (!localStorage.getItem('chatSessions')) {
        localStorage.setItem('chatSessions', JSON.stringify([]))
      }
    }
  
    // 获取所有聊天会话
    static getChatSessions() {
      return JSON.parse(localStorage.getItem('chatSessions') || '[]')
    }
  
    // 创建或更新聊天会话
    static saveChatSession(session) {
      const sessions = this.getChatSessions()
      const existingIndex = sessions.findIndex(s => s.sessionId === session.sessionId)
      
      if (existingIndex >= 0) {
        sessions[existingIndex] = session
      } else {
        sessions.push(session)
      }
      
      localStorage.setItem('chatSessions', JSON.stringify(sessions))
    }
  
    // 获取特定会话的聊天记录
    static getChatMessages(sessionId) {
      return JSON.parse(localStorage.getItem(`chat_${sessionId}`) || '[]')
    }
  
    // 保存聊天消息
    static saveChatMessage(sessionId, message) {
      const messages = this.getChatMessages(sessionId)
      messages.push(message)
      localStorage.setItem(`chat_${sessionId}`, JSON.stringify(messages))
      
      // 更新会话最后消息时间
      const sessions = this.getChatSessions()
      const sessionIndex = sessions.findIndex(s => s.sessionId === sessionId)
      if (sessionIndex >= 0) {
        sessions[sessionIndex].lastMessageTime = new Date().toISOString()
        sessions[sessionIndex].lastMessage = message.content.substring(0, 30) + '...'
        localStorage.setItem('chatSessions', JSON.stringify(sessions))
      }
    }
  
    // 删除聊天会话
    static deleteChatSession(sessionId) {
      const sessions = this.getChatSessions()
      const filteredSessions = sessions.filter(s => s.sessionId !== sessionId)
      localStorage.setItem('chatSessions', JSON.stringify(filteredSessions))
      localStorage.removeItem(`chat_${sessionId}`)
    }
  }