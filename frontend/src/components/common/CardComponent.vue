<template>
  <div class="card-component" :class="{ 'no-padding': noPadding, [`card-${type}`]: type }">
    <div class="card-header">
      <div class="card-header-left">
        <i v-if="icon" :class="icon"></i>
        <h3 class="card-title">{{ title }}</h3>
      </div>
      <div class="card-header-right">
        <button v-if="showRefresh" @click="$emit('refresh')" class="card-action refresh">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
        <router-link v-if="showMore" :to="moreLink" class="card-action more">
          <span>View all</span>
          <i class="bi bi-chevron-right"></i>
        </router-link>
      </div>
    </div>
    <div class="card-body">
      <slot></slot>
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
    type: {
      type: String,
      default: 'default',
      validator: value => ['default', 'primary', 'map', 'table'].includes(value)
    },
    showRefresh: {
      type: Boolean,
      default: false
    },
    showMore: {
      type: Boolean,
      default: false
    },
    moreLink: {
      type: String,
      default: '#'
    },
    noPadding: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.card-component {
  background-color: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-md);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-header-left i {
  font-size: 18px;
  color: var(--primary);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.card-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-action {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-light);
  transition: color 0.2s;
}

.card-action:hover {
  color: var(--primary);
}

.more {
  text-decoration: none;
}

.card-body {
  padding: 20px;
}

.no-padding .card-body {
  padding: 0;
}

/* Card types */
.card-primary {
  border-top: 3px solid var(--primary);
}

.card-map {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-map .card-body {
  flex: 1;
  padding: 0;
}
</style>