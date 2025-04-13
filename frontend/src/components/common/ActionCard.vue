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
  padding: 30px 24px;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.action-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  background-color: rgba(33, 150, 243, 0.1);
  color: var(--primary);
  font-size: 28px;
}

.action-card:hover .action-icon {
  transform: scale(1.05);
}

.action-content {
  flex: 1;
  margin-bottom: 20px;
  width: 100%;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text);
}

.action-description {
  font-size: 14px;
  color: var(--text-light);
  margin-bottom: 0;
  line-height: 1.5;
}

.action-footer {
  width: 100%;
  margin-top: auto;
}

/* Button Style Customizations */
.btn-primary .action-icon {
  background-color: rgba(33, 150, 243, 0.1);
  color: var(--primary);
}

.btn-secondary .action-icon {
  background-color: rgba(255, 64, 129, 0.1);
  color: var(--secondary);
}

.btn-success .action-icon {
  background-color: rgba(76, 175, 80, 0.1);
  color: var(--success);
}

.btn-warning .action-icon {
  background-color: rgba(255, 193, 7, 0.1);
  color: var(--warning);
}
</style>