<template>
  <div class="card" :class="{ 'map-card': type === 'map' }">
    <div class="card-header">
      <h2 class="card-title">
        <i v-if="icon" :class="icon"></i>
        {{ title }}
      </h2>
      <div class="card-actions">
        <slot name="actions">
          <button v-if="showRefresh" class="card-button" @click="$emit('refresh')">
            <i class="bi bi-arrow-repeat"></i>
          </button>
          <button v-if="showMore" class="card-button">
            <i class="bi bi-three-dots-vertical"></i>
          </button>
        </slot>
      </div>
    </div>
    <div class="card-body" :class="{ 'no-padding': noPadding }">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardComponent',
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      default: null
    },
    showRefresh: {
      type: Boolean,
      default: false
    },
    showMore: {
      type: Boolean,
      default: false
    },
    noPadding: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'default'
    }
  }
}
</script>

<style scoped>
.card-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border);
}
</style>