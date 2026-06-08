<script setup>
import { ref, nextTick } from 'vue';
import ChatWindow from './components/ChatWindow.vue';
import ChatInput from './components/ChatInput.vue';
import LeaveForm from './components/LeaveForm.vue';
import { chatService } from './services/chatService';
import { leaveService } from './services/leaveService';

const messages = ref([
  { role: 'assistant', content: '你好！我是你的 MCP 助手。我可以帮你计算面积、查询天气或处理请假申请。有什么我可以帮你的吗？' }
]);
const isTyping = ref(false);
const chatContainer = ref(null);

// 表单相关状态
const showLeaveForm = ref(false);
const initialLeaveDate = ref('');

const scrollToBottom = async () => {
  await nextTick();
  // 注意：在组件化后，滚动条可能在 ChatWindow 内部或者由 App 容器处理
  // 这里我们假设 ChatWindow 暴露了滚动方法或者直接操作 DOM
  const el = document.querySelector('.chat-main');
  if (el) {
    el.scrollTop = el.scrollHeight;
  }
};

const handleSendMessage = async (userMsg) => {
  messages.value.push({ role: 'user', content: userMsg });
  isTyping.value = true;
  await scrollToBottom();

  const history = messages.value.slice(0, -1).map(m => ({
    role: m.role,
    content: m.content
  }));

  let assistantMsg = { role: 'assistant', content: '' };
  messages.value.push(assistantMsg);

  await chatService.sendMessage(
    userMsg,
    history,
    (data) => {
      if (data.content) {
        assistantMsg.content += data.content;
        
        // 检查是否包含请假表单触发词 [[LEAVE_FORM:YYYY-MM-DD]]
        const leaveMatch = assistantMsg.content.match(/\[\[LEAVE_FORM:(.*?)\]\]/);
        if (leaveMatch) {
          initialLeaveDate.value = leaveMatch[1];
          showLeaveForm.value = true;
        }
        scrollToBottom();
      } else if (data.error) {
        assistantMsg.content += `\n[错误: ${data.error}]`;
      }
    },
    (error) => {
      assistantMsg.content = '抱歉，连接服务器出错：' + error.message;
    }
  );

  isTyping.value = false;
  await scrollToBottom();
};

const handleLeaveSubmit = async (formData) => {
  try {
    const result = await leaveService.submitLeave(formData);
    if (result.success) {
      messages.value.push({ role: 'assistant', content: result.message });
      showLeaveForm.value = false;
    } else {
      alert('提交失败: ' + result.message);
    }
  } catch (error) {
    alert('提交出错: ' + error.message);
  }
  await scrollToBottom();
};
</script>

<template>
  <div class="chat-wrapper">
    <header class="chat-header">
      <h1>MCP Chat Bot</h1>
    </header>

    <ChatWindow :messages="messages">
      <LeaveForm 
        :show="showLeaveForm" 
        :initial-date="initialLeaveDate"
        @submit="handleLeaveSubmit"
        @cancel="showLeaveForm = false"
      />
    </ChatWindow>

    <ChatInput 
      :is-typing="isTyping" 
      @send="handleSendMessage" 
    />
  </div>
</template>

<style>
/* 全局变量和基础样式 */
:root {
  --bg: #ffffff;
  --text: #333333;
  --text-h: #1a1a1a;
  --accent: #4f46e5;
  --accent-rgb: 79, 70, 229;
  --border: #e5e7eb;
  --social-bg: #f3f4f6;
  --code-bg: #f9fafb;
  --shadow: 0 1px 3px rgba(0,0,0,0.1);
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #f0f2f5;
}

#app {
  height: 100vh;
}
</style>

<style scoped>
.chat-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: var(--bg);
  border-left: 1px solid var(--border);
  border-right: 1px solid var(--border);
}

.chat-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border);
  text-align: center;
  background: white;
  z-index: 10;
}

.chat-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--accent);
}
</style>
