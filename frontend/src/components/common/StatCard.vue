<template>
  <div class="stat-card">
    <div class="stat-icon">
      <i :class="icon"></i>
    </div>
    <div class="stat-content">
      <h3 class="stat-title">{{ title }}</h3>
      <div class="stat-value">{{ value }}</div>
      <div v-if="change" class="stat-change" :class="changeTypeClass">
        <i :class="changeIcon"></i> {{ change }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    change: {
      type: String,
      default: null
    },
    changeType: {
      type: String,
      default: 'neutral',
      validator: value => ['positive', 'negative', 'neutral'].includes(value)
    }
  },
  computed: {
    changeTypeClass() {
      return `change-${this.changeType}`;
    },
    changeIcon() {
      if (this.changeType === 'positive') return 'bi bi-arrow-up-right';
      if (this.changeType === 'negative') return 'bi bi-arrow-down-right';
      return 'bi bi-dash';
    }
  }
}
</script>

<style scoped>
.stat-card {
  background-color: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: var(--text-light);
  margin-bottom: 4px;
  font-weight: 500;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.stat-change {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.change-positive {
  color: var(--success);
}

.change-negative {
  color: var(--danger);
}

.change-neutral {
  color: var(--text-lighter);
}
</style>