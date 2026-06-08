<script setup>
import { ref } from 'vue';

defineProps({
  isTyping: Boolean
});

const emit = defineEmits(['send']);
const userInput = ref('');

const handleSend = () => {
  if (!userInput.value.trim()) return;
  emit('send', userInput.value);
  userInput.value = '';
};
</script>

<template>
  <footer class="chat-footer">
    <div class="input-area">
      <input 
        v-model="userInput" 
        @keyup.enter="handleSend" 
        placeholder="输入消息..." 
        :disabled="isTyping"
      />
      <button @click="handleSend" :disabled="isTyping || !userInput.trim()">
        {{ isTyping ? '发送中...' : '发送' }}
      </button>
    </div>
  </footer>
</template>

<style scoped>
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
