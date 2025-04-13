<template>
  <div class="activity-item">
    <div class="activity-icon">
      <i class="bi bi-geo-alt"></i>
    </div>
    <div class="activity-content">
      <div class="activity-text">
        <strong>{{ petName }}</strong> was seen at <span class="location">{{ location }}</span>
      </div>
      <div class="activity-info">
        <span>
          <i class="bi bi-clock"></i> {{ timeAgo }}
        </span>
        <span>
          <i :class="batteryIcon"></i> {{ batteryLevel }}%
        </span>
        <span>
          <i class="bi bi-speedometer2"></i> {{ speed }} km/h
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActivityItem',
  props: {
    petName: {
      type: String,
      required: true
    },
    location: {
      type: String,
      required: true
    },
    timeAgo: {
      type: String,
      required: true
    },
    batteryLevel: {
      type: Number,
      default: 100
    },
    speed: {
      type: Number,
      default: 0
    }
  },
  computed: {
    batteryIcon() {
      if (this.batteryLevel >= 80) return 'bi-battery-full';
      if (this.batteryLevel >= 50) return 'bi-battery-half';
      if (this.batteryLevel >= 20) return 'bi-battery-low';
      return 'bi-battery';
    }
  }
}
</script>

<style scoped>
.activity-item {
  display: flex;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 42px;
  height: 42px;
  background-color: #E3F2FD;
  border-radius: var(--radius);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.activity-icon i {
  font-size: 20px;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 15px;
  margin-bottom: 6px;
  color: var(--text);
}

.activity-text strong {
  font-weight: 600;
}

.location {
  color: var(--primary);
  font-weight: 500;
}

.activity-info {
  display: flex;
  flex-wrap: wrap;
}

.activity-info span {
  font-size: 13px;
  display: flex;
  align-items: center;
  color: var(--text-light);
  margin-right: 16px;
  margin-bottom: 4px;
}

.activity-info i {
  margin-right: 6px;
  font-size: 14px;
}
</style>