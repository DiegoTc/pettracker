<template>
  <app-layout>
    <div class="page-header">
      <h1 class="page-title">My Devices</h1>
      <button class="btn btn-primary" @click="navigateTo('/devices/new')">
        <i class="bi bi-plus-lg"></i> Add New Device
      </button>
    </div>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your devices...</p>
    </div>
    
    <div v-else-if="devices.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="bi bi-cpu"></i>
      </div>
      <h3>No Devices Found</h3>
      <p>You haven't added any tracking devices yet. Add your first device to start tracking your pets.</p>
      <button class="btn btn-primary" @click="navigateTo('/devices/new')">
        <i class="bi bi-plus-lg"></i> Add First Device
      </button>
    </div>
    
    <div v-else>
      <div class="devices-grid">
        <card-component
          v-for="device in devices"
          :key="device.id"
          :title="device.name || device.device_id"
          icon="bi bi-cpu"
        >
          <div class="device-card-content">
            <div class="device-info">
              <div class="info-item">
                <div class="info-label">Device ID</div>
                <div class="info-value">{{ device.device_id }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Type</div>
                <div class="info-value">{{ device.device_type || 'Not specified' }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Status</div>
                <div class="info-value status" :class="device.is_active ? 'active' : 'inactive'">
                  <i class="bi" :class="device.is_active ? 'bi-check-circle' : 'bi-x-circle'"></i>
                  {{ device.is_active ? 'Active' : 'Inactive' }}
                </div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Battery</div>
                <div class="info-value">{{ device.battery_level }}%</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Last Ping</div>
                <div class="info-value">{{ formatDate(device.last_ping) || 'Never' }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Assigned To</div>
                <div class="info-value">{{ device.pet ? device.pet.name : 'Not assigned' }}</div>
              </div>
            </div>
            
            <div class="device-actions">
              <button class="btn btn-sm btn-outline-primary me-2" @click="editDevice(device)">
                <i class="bi bi-pencil"></i> Edit
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="confirmDelete(device)">
                <i class="bi bi-trash"></i> Delete
              </button>
            </div>
          </div>
        </card-component>
      </div>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';
import CardComponent from '../components/common/CardComponent.vue';

export default {
  name: 'Devices',
  components: {
    AppLayout,
    CardComponent
  },
  data() {
    return {
      devices: [],
      loading: true
    }
  },
  mounted() {
    this.fetchDevices();
  },
  methods: {
    fetchDevices() {
      // Simulate API call
      setTimeout(() => {
        this.devices = [
          {
            id: 1,
            device_id: 'ABC123',
            name: 'Buddy\'s Collar',
            device_type: 'GPS Collar',
            is_active: true,
            battery_level: 87,
            last_ping: new Date().toISOString(),
            pet: {
              id: 1,
              name: 'Buddy'
            }
          },
          {
            id: 2,
            device_id: 'XYZ789',
            name: 'Home Tracker',
            device_type: 'Smart Tag',
            is_active: false,
            battery_level: 32,
            last_ping: '2023-04-01T15:30:00.000Z',
            pet: null
          }
        ];
        this.loading = false;
      }, 1000);
      
      // Real API call will look like:
      /*
      fetch('/api/devices')
        .then(response => response.json())
        .then(data => {
          this.devices = data;
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching devices:', error);
          this.loading = false;
        });
      */
    },
    navigateTo(route) {
      this.$router.push(route);
    },
    editDevice(device) {
      this.$router.push(`/devices/${device.id}/edit`);
    },
    confirmDelete(device) {
      if (confirm(`Are you sure you want to delete device ${device.name || device.device_id}?`)) {
        console.log('Delete device:', device.id);
        // Will implement actual delete API call
        this.devices = this.devices.filter(d => d.id !== device.id);
      }
    },
    formatDate(dateString) {
      if (!dateString) return null;
      
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins} minute${diffMins === 1 ? '' : 's'} ago`;
      
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
      
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric'
      });
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background-color: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  margin: 40px auto;
  max-width: 500px;
}

.empty-icon {
  font-size: 48px;
  color: var(--primary);
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 10px;
}

.empty-state p {
  color: var(--text-light);
  margin-bottom: 20px;
}

.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

@media (max-width: 576px) {
  .devices-grid {
    grid-template-columns: 1fr;
  }
}

.device-card-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.device-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.info-item {
  margin-bottom: 8px;
}

.info-label {
  font-size: 14px;
  color: var(--text-light);
  margin-bottom: 4px;
}

.info-value {
  font-size: 15px;
  font-weight: 500;
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status.active {
  color: var(--success);
}

.status.inactive {
  color: var(--danger);
}

.device-actions {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
}
</style>
