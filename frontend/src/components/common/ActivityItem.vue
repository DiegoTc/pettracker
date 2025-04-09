<template>
  <div class="activity-item">
    <div class="activity-icon">
      <i :class="icon || 'bi bi-geo-alt'"></i>
    </div>
    <div class="activity-content">
      <p class="activity-text">
        <strong>{{ petName }}</strong> 
        was located at 
        <span class="location">{{ location }}</span>
      </p>
      <div class="activity-info">
        <span>
          <i class="bi bi-clock"></i> {{ timeAgo }}
        </span>
        <span v-if="batteryLevel !== undefined">
          <i class="bi bi-battery-half"></i> {{ batteryLevel }}%
        </span>
        <span v-if="speed !== undefined">
          <i class="bi bi-speedometer"></i> {{ speed }} km/h
        </span>
        <slot name="extra-info"></slot>
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
      default: undefined
    },
    speed: {
      type: Number,
      default: undefined
    },
    icon: {
      type: String,
      default: null
    }
  }
}
</script>