<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  initialData: Object,
  show: Boolean
});

const emit = defineEmits(['submit', 'cancel']);

const leaveForm = ref({
  applicant: '',
  start_time: '',
  end_time: '',
  leave_type: '事假',
  reason: ''
});

const leaveTypes = ['事假', '病假', '年假', '调休', '其他'];

watch(() => props.initialData, (newData) => {
  if (newData) {
    leaveForm.value = {
      applicant: newData.applicant || '',
      start_time: newData.start_time || '',
      end_time: newData.end_time || '',
      leave_type: newData.leave_type || '事假',
      reason: newData.reason || ''
    };
  }
}, { immediate: true, deep: true });

const handleSubmit = () => {
  emit('submit', { ...leaveForm.value });
};
</script>

<template>
  <div v-if="show" class="leave-form-card">
    <h3>填写请假申请</h3>
    <div class="form-group">
      <label>请假人:</label>
      <input v-model="leaveForm.applicant" placeholder="请输入姓名" required />
    </div>
    <div class="form-grid">
      <div class="form-group">
        <label>开始时间:</label>
        <input v-model="leaveForm.start_time" type="datetime-local" required />
      </div>
      <div class="form-group">
        <label>结束时间:</label>
        <input v-model="leaveForm.end_time" type="datetime-local" required />
      </div>
    </div>
    <div class="form-group">
      <label>请假类型:</label>
      <select v-model="leaveForm.leave_type">
        <option v-for="type in leaveTypes" :key="type" :value="type">{{ type }}</option>
      </select>
    </div>
    <div class="form-group">
      <label>请假原因:</label>
      <textarea v-model="leaveForm.reason" placeholder="请输入详细原因" rows="3"></textarea>
    </div>
    <div class="form-actions">
      <button @click="handleSubmit" class="btn-submit">确认提交</button>
      <button @click="emit('cancel')" class="btn-cancel">取消</button>
    </div>
  </div>
</template>

<style scoped>
.leave-form-card {
  background: var(--bg);
  border: 1px solid var(--accent);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.leave-form-card h3 {
  margin-top: 0;
  margin-bottom: 1.2rem;
  color: var(--accent);
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  text-align: left;
}

.form-group label {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-h);
}

.form-group input, 
.form-group select, 
.form-group textarea {
  padding: 0.6rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--code-bg);
  color: var(--text-h);
  font-size: 0.95rem;
}

.form-group input:focus, 
.form-group select:focus, 
.form-group textarea:focus {
  border-color: var(--accent);
  outline: none;
  box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.2);
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.2rem;
}

.btn-submit {
  flex: 2;
  background: var(--accent);
  color: white;
  border: none;
  padding: 0.7rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-cancel {
  flex: 1;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  padding: 0.7rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-submit:hover { opacity: 0.9; }
.btn-cancel:hover { background: var(--social-bg); }
</style>
