<template>
  <app-layout>
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading pet details...</p>
    </div>

    <div v-else-if="!pet" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle"></i>
      Pet not found. The pet you're looking for may have been removed.
      <router-link to="/pets" class="btn btn-outline-primary mt-3">Go back to pets</router-link>
    </div>

    <div v-else>
      <div class="page-header">
        <div class="d-flex align-items-center">
          <button class="btn btn-outline-secondary me-3" @click="$router.go(-1)">
            <i class="bi bi-arrow-left"></i>
          </button>
          <h1 class="page-title mb-0">{{ pet.name }}</h1>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary me-2" @click="navigateTo(`/pets/${pet.id}/edit`)">
            <i class="bi bi-pencil"></i> Edit
          </button>
          <button class="btn btn-danger" @click="confirmDelete">
            <i class="bi bi-trash"></i> Delete
          </button>
        </div>
      </div>

      <div class="pet-details-layout">
        <div class="pet-main-info">
          <div class="pet-image-container">
            <img v-if="pet.image_url" :src="pet.image_url" :alt="pet.name">
            <div v-else class="pet-image-placeholder">
              <i class="bi" :class="getPetIcon(pet.pet_type)"></i>
              <span>No Image</span>
            </div>
          </div>

          <card-component title="Pet Information" icon="bi bi-info-circle">
            <div class="pet-info-grid">
              <div class="info-item">
                <div class="info-label">Type</div>
                <div class="info-value">{{ pet.pet_type }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Breed</div>
                <div class="info-value">{{ pet.breed || 'Not specified' }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Color</div>
                <div class="info-value">{{ pet.color || 'Not specified' }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Age</div>
                <div class="info-value">{{ petAge }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Weight</div>
                <div class="info-value">{{ pet.weight ? `${pet.weight} kg` : 'Not specified' }}</div>
              </div>
              
              <div class="info-item">
                <div class="info-label">Registered</div>
                <div class="info-value">{{ formatDate(pet.created_at) }}</div>
              </div>
            </div>
          </card-component>

          <card-component v-if="pet.description" title="About" icon="bi bi-file-text">
            <p>{{ pet.description }}</p>
          </card-component>
        </div>

        <div class="pet-tracking-info">
          <card-component 
            title="Current Location" 
            icon="bi bi-geo-alt"
            type="map"
            no-padding
            show-refresh
            @refresh="refreshMap"
          >
            <div class="map-container">
              <!-- Map component will go here -->
              <div>Interactive Map Coming Soon</div>
            </div>
          </card-component>

          <card-component title="Assigned Devices" icon="bi bi-cpu">
            <div v-if="!devices.length" class="no-devices">
              <p>No devices assigned to this pet.</p>
              <button class="btn btn-primary btn-sm" @click="navigateTo('/devices/new')">
                <i class="bi bi-plus-lg"></i> Add Device
              </button>
            </div>
            <div v-else class="devices-list">
              <div v-for="device in devices" :key="device.id" class="device-item">
                <div class="device-info">
                  <div class="device-name">{{ device.name || device.device_id }}</div>
                  <div class="device-type">{{ device.device_type || 'Unknown type' }}</div>
                </div>
                <div class="device-stats">
                  <div class="device-battery">
                    <i class="bi bi-battery-half"></i> {{ device.battery_level }}%
                  </div>
                  <div class="device-status" :class="device.is_active ? 'active' : 'inactive'">
                    <i class="bi" :class="device.is_active ? 'bi-check-circle' : 'bi-x-circle'"></i>
                    {{ device.is_active ? 'Active' : 'Inactive' }}
                  </div>
                </div>
              </div>
            </div>
          </card-component>

          <card-component title="Recent Activity" icon="bi bi-clock-history">
            <div v-if="!activities.length" class="no-activity">
              <p>No recent activity for this pet.</p>
            </div>
            <div v-else class="activity-list">
              <div v-for="(activity, index) in activities" :key="index" class="activity-item-simple">
                <div class="activity-time">{{ activity.timeAgo }}</div>
                <div class="activity-content">
                  <div class="activity-title">{{ activity.title }}</div>
                  <div class="activity-details">{{ activity.details }}</div>
                </div>
              </div>
            </div>
          </card-component>
        </div>
      </div>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';
import CardComponent from '../components/common/CardComponent.vue';

export default {
  name: 'PetDetails',
  components: {
    AppLayout,
    CardComponent
  },
  data() {
    return {
      pet: null,
      loading: true,
      devices: [],
      activities: []
    }
  },
  computed: {
    petAge() {
      if (!this.pet.birthdate) return 'Not specified';
      
      // This is just a placeholder - will implement proper age calculation
      return '3 years';
    }
  },
  mounted() {
    this.fetchPetDetails();
  },
  methods: {
    fetchPetDetails() {
      // Simulate API call
      setTimeout(() => {
        this.pet = {
          id: this.$route.params.id,
          name: 'Buddy',
          pet_type: 'Dog',
          breed: 'Golden Retriever',
          color: 'Golden',
          weight: 28.5,
          birthdate: '2022-03-15',
          description: 'Buddy is a friendly and energetic dog who loves to play fetch and go for long walks in the park. He is good with children and other pets.',
          created_at: '2023-06-01T10:00:00.000Z',
          image_url: null
        };
        
        this.devices = [
          {
            id: 1,
            device_id: 'ABC123',
            name: 'Collar Tracker',
            device_type: 'GPS Collar',
            battery_level: 87,
            is_active: true
          }
        ];
        
        this.activities = [
          {
            timeAgo: '2 hours ago',
            title: 'Location Updated',
            details: 'Pet was at Dog Park'
          },
          {
            timeAgo: '5 hours ago',
            title: 'Battery Level',
            details: 'Device battery dropped to 87%'
          },
          {
            timeAgo: 'Yesterday',
            title: 'Activity Alert',
            details: 'High activity level detected'
          }
        ];
        
        this.loading = false;
      }, 1000);
    },
    refreshMap() {
      console.log('Refreshing map...');
    },
    navigateTo(route) {
      this.$router.push(route);
    },
    confirmDelete() {
      if (confirm(`Are you sure you want to delete ${this.pet.name}?`)) {
        console.log('Delete pet:', this.pet.id);
        // Will implement API call
        this.$router.push('/pets');
      }
    },
    getPetIcon(petType) {
      switch(petType.toLowerCase()) {
        case 'dog':
          return 'bi-emoji-smile';
        case 'cat':
          return 'bi-emoji-smile-upside-down';
        case 'bird':
          return 'bi-emoji-laughing';
        default:
          return 'bi-emoji-smile';
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'Unknown';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
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

.pet-details-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 992px) {
  .pet-details-layout {
    grid-template-columns: 1fr;
  }
}

.pet-main-info, .pet-tracking-info {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.pet-image-container {
  background-color: var(--primary-light);
  border-radius: var(--radius);
  overflow: hidden;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.pet-image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pet-image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.pet-image-placeholder i {
  font-size: 64px;
  margin-bottom: 16px;
}

.pet-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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
  font-size: 16px;
  font-weight: 500;
}

.map-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-light);
  color: var(--primary);
  font-size: 18px;
  font-weight: 500;
}

.no-devices, .no-activity {
  text-align: center;
  padding: 24px;
  color: var(--text-light);
}

.devices-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.device-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: var(--background);
  border-radius: var(--radius);
}

.device-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.device-type {
  font-size: 14px;
  color: var(--text-light);
}

.device-stats {
  display: flex;
  gap: 16px;
  font-size: 14px;
}

.device-battery, .device-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.device-status.active {
  color: var(--success);
}

.device-status.inactive {
  color: var(--danger);
}

.activity-list {
  display: flex;
  flex-direction: column;
}

.activity-item-simple {
  padding: 12px 0;
  display: flex;
  border-bottom: 1px solid var(--border);
}

.activity-item-simple:last-child {
  border-bottom: none;
}

.activity-time {
  min-width: 80px;
  font-size: 13px;
  color: var(--text-lighter);
}

.activity-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.activity-details {
  font-size: 14px;
  color: var(--text-light);
}

.btn-outline-secondary {
  background-color: transparent;
  border: 1px solid var(--border);
  color: var(--text);
}

.btn-outline-secondary:hover {
  background-color: var(--border);
  color: var(--text);
}

.header-actions {
  display: flex;
}

.alert {
  padding: 24px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.alert i {
  font-size: 24px;
  margin-bottom: 12px;
}
</style>
