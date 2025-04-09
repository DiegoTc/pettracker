<template>
  <div class="action-card">
    <div class="action-icon">
      <i :class="icon"></i>
    </div>
    <div class="action-content">
      <h3 class="action-title">{{ title }}</h3>
      <p class="action-description">{{ description }}</p>
    </div>
    <div class="action-footer">
      <button 
        @click="$emit('action')" 
        class="btn"
        :class="`btn-${buttonType}`"
      >
        <i v-if="buttonIcon" :class="buttonIcon"></i>
        {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActionCard',
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    buttonText: {
      type: String,
      required: true
    },
    buttonIcon: {
      type: String,
      default: null
    },
    buttonType: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'success', 'warning', 'danger', 'info'].includes(value)
    }
  }
}
</script>

<style scoped>
.action-card {
  background-color: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.action-icon {
  width: 50px;
  height: 50px;
  margin: 24px auto 16px;
  border-radius: 50%;
  background-color: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.action-content {
  padding: 0 24px;
  text-align: center;
  flex: 1;
}

.action-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.action-description {
  color: var(--text-light);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.action-footer {
  padding: 24px;
  text-align: center;
}
</style>