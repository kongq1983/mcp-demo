<script setup>
defineProps({
  messages: Array
});
</script>

<template>
  <div class="chat-main">
    <div v-for="(msg, index) in messages" :key="index" :class="['message-row', msg.role]">
      <div class="message-bubble">
        <div class="message-content">{{ msg.content }}</div>
      </div>
    </div>
    <slot></slot> <!-- 用于放置请假表单 -->
  </div>
</template>

<style scoped>
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
</style>
