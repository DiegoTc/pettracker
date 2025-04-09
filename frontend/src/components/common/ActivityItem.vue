<template>
  <div class="activity-item">
    <div class="activity-icon">
      <i class="bi bi-geo-fill"></i>
    </div>
    <div class="activity-content">
      <h4 class="activity-title">{{ petName }}</h4>
      <p class="activity-location">{{ location }}</p>
      <div class="activity-details">
        <span class="activity-time">
          <i class="bi bi-clock"></i> {{ timeAgo }}
        </span>
        <span class="activity-battery">
          <i class="bi bi-battery-half"></i> {{ batteryLevel }}%
        </span>
        <span class="activity-speed">
          <i class="bi bi-speedometer"></i> {{ speed }} km/h
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
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 36px;
  height: 36px;
  background-color: var(--primary-light);
  color: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 2px 0;
  color: var(--text);
}

.activity-location {
  font-size: 14px;
  color: var(--text-light);
  margin: 0 0 4px 0;
}

.activity-details {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-lighter);
}

.activity-details span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.activity-time i,
.activity-battery i,
.activity-speed i {
  font-size: 12px;
}
</style>