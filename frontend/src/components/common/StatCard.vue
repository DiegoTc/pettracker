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
  padding: 24px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
  position: relative;
  height: 100%;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background-color: var(--primary);
}

.stat-card:nth-child(2)::before {
  background-color: var(--warning);
}

.stat-card:nth-child(3)::before {
  background-color: var(--success);
}

.stat-card:nth-child(4)::before {
  background-color: var(--secondary);
}

.stat-icon {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  font-size: 26px;
  color: var(--primary);
}

.stat-card:nth-child(2) .stat-icon {
  color: var(--warning);
}

.stat-card:nth-child(3) .stat-icon {
  color: var(--success);
}

.stat-card:nth-child(4) .stat-icon {
  color: var(--secondary);
}

.stat-content h3 {
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-light);
  margin-bottom: 12px;
}

.stat-value {
  font-family: 'Quicksand', sans-serif;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text);
}

.stat-change {
  display: flex;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
}

.change-positive {
  color: var(--success);
}

.change-negative {
  color: var(--danger);
}

.change-neutral {
  color: var(--text-light);
}

.stat-change i {
  margin-right: 5px;
}
</style>