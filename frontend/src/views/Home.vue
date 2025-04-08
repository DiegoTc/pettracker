<template>
  <div class="home-page">
    <div class="welcome-section mb-5">
      <h2>Welcome to Pet Tracker</h2>
      <p class="lead">Monitor and manage your pets in real-time with advanced tracking technology.</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <!-- No Pets State -->
    <div v-else-if="pets.length === 0" class="text-center my-5">
      <i class="bi bi-heart display-4 text-muted"></i>
      <h4 class="mt-3">No pets added yet</h4>
      <p class="text-muted">Start by adding your pets to track them</p>
      <router-link to="/pets/new" class="btn btn-primary mt-2">
        Add Your First Pet
      </router-link>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Pet Summary Cards -->
      <div class="row mb-5">
        <div class="col-md-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <i class="bi bi-heart-fill text-danger display-4"></i>
              <h5 class="mt-3">Total Pets</h5>
              <p class="display-5">{{ pets.length }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <i class="bi bi-cpu display-4 text-info"></i>
              <h5 class="mt-3">Active Devices</h5>
              <p class="display-5">{{ activeDevices }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <i class="bi bi-geo-alt-fill display-4 text-success"></i>
              <h5 class="mt-3">Locations Tracked</h5>
              <p class="display-5">{{ totalLocations }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <h3 class="mb-4">Recent Activity</h3>
      <div class="card mb-5">
        <div class="card-body p-0">
          <div class="list-group list-group-flush">
            <div v-if="recentLocations.length === 0" class="list-group-item py-4 text-center">
              <p class="text-muted mb-0">No recent activity to display</p>
            </div>
            <div v-else v-for="location in recentLocations" :key="location.id" class="list-group-item">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <i class="bi bi-geo-alt-fill text-primary me-2"></i>
                  <strong>{{ getPetName(getDevicePetId(location.device_id)) }}</strong> 
                  was located at 
                  <span class="text-info">{{ formatCoordinates(location.latitude, location.longitude) }}</span>
                </div>
                <small class="text-muted">{{ formatTimeAgo(location.timestamp) }}</small>
              </div>
              <div class="mt-1 small text-muted">
                <i class="bi bi-battery-half me-1"></i> Battery: {{ location.battery_level || 'N/A' }}%
                <i class="bi bi-speedometer2 ms-3 me-1"></i> Speed: {{ formatSpeed(location.speed) }}
                <i class="bi bi-thermometer-half ms-3 me-1"></i> Temp: {{ formatTemperature(location.temperature) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <h3 class="mb-4">Quick Actions</h3>
      <div class="row">
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="card">
            <div class="card-body text-center py-4">
              <i class="bi bi-plus-circle display-5 text-primary mb-3"></i>
              <h5>Add Pet</h5>
              <p class="card-text text-muted">Register a new pet in the system</p>
              <router-link to="/pets/new" class="btn btn-primary">
                Add Pet
              </router-link>
            </div>
          </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="card">
            <div class="card-body text-center py-4">
              <i class="bi bi-cpu display-5 text-info mb-3"></i>
              <h5>Register Device</h5>
              <p class="card-text text-muted">Connect a new tracking device</p>
              <router-link to="/devices/new" class="btn btn-info text-white">
                Add Device
              </router-link>
            </div>
          </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="card">
            <div class="card-body text-center py-4">
              <i class="bi bi-geo-alt display-5 text-success mb-3"></i>
              <h5>View Map</h5>
              <p class="card-text text-muted">See where your pets are located</p>
              <router-link to="/map" class="btn btn-success">
                Open Map
              </router-link>
            </div>
          </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="card">
            <div class="card-body text-center py-4">
              <i class="bi bi-journal-text display-5 text-warning mb-3"></i>
              <h5>Reports</h5>
              <p class="card-text text-muted">View activity and health reports</p>
              <router-link to="/reports" class="btn btn-warning">
                View Reports
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { petsAPI, devicesAPI, locationsAPI } from '../services/api';

export default {
  name: 'Home',
  data() {
    return {
      loading: true,
      error: null,
      pets: [],
      devices: [],
      recentLocations: [],
      totalLocations: 0
    };
  },
  computed: {
    activeDevices() {
      return this.devices.filter(device => device.is_active).length;
    }
  },
  async created() {
    try {
      // Fetch data in parallel
      const [petsResponse, devicesResponse, locationsResponse] = await Promise.all([
        petsAPI.getAll(),
        devicesAPI.getAll(),
        locationsAPI.getRecent() // Assuming this endpoint exists
      ]);
      
      this.pets = petsResponse.data;
      this.devices = devicesResponse.data;
      
      // Assuming locationsResponse has data and recent_count properties
      this.recentLocations = locationsResponse.data.recent || [];
      this.totalLocations = locationsResponse.data.total_count || 0;
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      this.error = 'Failed to load dashboard data. Please try refreshing the page.';
    } finally {
      this.loading = false;
    }
  },
  methods: {
    getPetName(petId) {
      if (!petId) return 'Unknown Pet';
      const pet = this.pets.find(p => p.id === petId);
      return pet ? pet.name : 'Unknown Pet';
    },
    getDevicePetId(deviceId) {
      const device = this.devices.find(d => d.id === deviceId);
      return device ? device.pet_id : null;
    },
    formatCoordinates(lat, lng) {
      if (!lat || !lng) return 'Unknown Location';
      return `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    },
    formatTimeAgo(timestamp) {
      if (!timestamp) return 'Unknown Time';
      
      const now = new Date();
      const locationTime = new Date(timestamp);
      const diffMs = now - locationTime;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);
      const diffDay = Math.floor(diffHour / 24);
      
      if (diffDay > 0) {
        return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
      } else if (diffHour > 0) {
        return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
      } else if (diffMin > 0) {
        return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
      } else {
        return 'Just now';
      }
    },
    formatSpeed(speed) {
      if (speed === undefined || speed === null) return 'N/A';
      return `${speed.toFixed(1)} km/h`;
    },
    formatTemperature(temp) {
      if (temp === undefined || temp === null) return 'N/A';
      return `${temp.toFixed(1)}°C`;
    }
  }
};
</script>

<style scoped>
.home-page {
  margin-bottom: 50px;
}
</style>
