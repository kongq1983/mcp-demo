<script setup>
import { ref, nextTick, onMounted } from 'vue';

const messages = ref([
  { role: 'assistant', content: '你好！我是你的 MCP 助手。我可以帮你计算面积、查询天气或处理请假申请。有什么我可以帮你的吗？' }
]);
const userInput = ref('');
const isTyping = ref(false);
const chatContainer = ref(null);

// 表单相关状态
const showLeaveForm = ref(false);
const leaveForm = ref({
  name: '',
  date: '',
  reason: ''
});

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isTyping.value) return;

  const userMsg = userInput.value;
  messages.value.push({ role: 'user', content: userMsg });
  userInput.value = '';
  isTyping.value = true;
  await scrollToBottom();

  // 准备发送到后端的历史记录（排除当前最后一条）
  const history = messages.value.slice(0, -1).map(m => ({
    role: m.role,
    content: m.content
  }));

  try {
    const response = await fetch('http://localhost:8001/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: userMsg,
        history: history
      }),
    });

    if (!response.ok) throw new Error('网络请求失败');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let assistantMsg = { role: 'assistant', content: '' };
    messages.value.push(assistantMsg);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim();
          if (dataStr === '[DONE]') continue;
          
          try {
            const data = JSON.parse(dataStr);
            if (data.content) {
              assistantMsg.content += data.content;
              
              // 检查是否包含请假表单触发词 [[LEAVE_FORM:YYYY-MM-DD]]
              const leaveMatch = assistantMsg.content.match(/\[\[LEAVE_FORM:(.*?)\]\]/);
              if (leaveMatch) {
                leaveForm.value.date = leaveMatch[1];
                showLeaveForm.value = true;
              }
              
              await scrollToBottom();
            } else if (data.error) {
              assistantMsg.content += `\n[错误: ${data.error}]`;
            }
          } catch (e) {
            // 忽略非 JSON 数据
          }
        }
      }
    }
  } catch (error) {
    messages.value.push({ role: 'assistant', content: '抱歉，连接服务器出错：' + error.message });
  } finally {
    isTyping.value = false;
    await scrollToBottom();
  }
};

const submitLeave = async () => {
  try {
    const response = await fetch('http://localhost:8001/leave/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(leaveForm.value),
    });
    const result = await response.json();
    if (result.success) {
      messages.value.push({ role: 'assistant', content: result.message });
      showLeaveForm.value = false;
      leaveForm.value = { name: '', date: '', reason: '' };
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

    <main class="chat-main" ref="chatContainer">
      <div v-for="(msg, index) in messages" :key="index" :class="['message-row', msg.role]">
        <div class="message-bubble">
          <div class="message-content">{{ msg.content }}</div>
        </div>
      </div>

      <!-- 请假表单弹窗/嵌入 -->
      <div v-if="showLeaveForm" class="leave-form-card">
        <h3>填写请假申请</h3>
        <div class="form-group">
          <label>姓名:</label>
          <input v-model="leaveForm.name" placeholder="请输入姓名" />
        </div>
        <div class="form-group">
          <label>日期:</label>
          <input v-model="leaveForm.date" type="date" />
        </div>
        <div class="form-group">
          <label>原因:</label>
          <textarea v-model="leaveForm.reason" placeholder="请输入请假原因"></textarea>
        </div>
        <div class="form-actions">
          <button @click="submitLeave" class="btn-submit">确认提交</button>
          <button @click="showLeaveForm = false" class="btn-cancel">取消</button>
        </div>
      </div>
    </main>

    <footer class="chat-footer">
      <div class="input-area">
        <input 
          v-model="userInput" 
          @keyup.enter="sendMessage" 
          placeholder="输入消息..." 
          :disabled="isTyping"
        />
        <button @click="sendMessage" :disabled="isTyping || !userInput.trim()">
          {{ isTyping ? '发送中...' : '发送' }}
        </button>
      </div>
    </footer>
  </div>
</template>

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
}

.chat-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--accent);
}

.chat-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-row {
  display: flex;
  width: 100%;
}

.message-row.user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 80%;
  padding: 0.8rem 1rem;
  border-radius: 12px;
  font-size: 1rem;
  line-height: 1.5;
  word-wrap: break-word;
}

.user .message-bubble {
  background-color: var(--accent);
  color: white;
  border-bottom-right-radius: 2px;
}

.assistant .message-bubble {
  background-color: var(--social-bg);
  color: var(--text-h);
  border-bottom-left-radius: 2px;
}

.leave-form-card {
  background: var(--bg);
  border: 1px solid var(--accent);
  border-radius: 8px;
  padding: 1.2rem;
  margin-top: 1rem;
  box-shadow: var(--shadow);
}

.leave-form-card h3 {
  margin-top: 0;
  color: var(--accent);
}

.form-group {
  margin-bottom: 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  text-align: left;
}

.form-group input, .form-group textarea {
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--code-bg);
  color: var(--text-h);
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-submit {
  background: var(--accent);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-cancel {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.chat-footer {
  padding: 1rem;
  border-top: 1px solid var(--border);
}

.input-area {
  display: flex;
  gap: 0.5rem;
}

.input-area input {
  flex: 1;
  padding: 0.7rem 1rem;
  border: 1px solid var(--border);
  border-radius: 20px;
  outline: none;
  background: var(--code-bg);
  color: var(--text-h);
}

.input-area button {
  padding: 0 1.2rem;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.input-area button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
