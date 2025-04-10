<template>
  <app-layout>
    <div class="page-header">
      <h1 class="page-title">Pet Tracker Map</h1>
      <div class="map-controls">
        <select v-model="selectedPet" class="form-select select-pet">
          <option value="all">All Pets</option>
          <option v-for="pet in pets" :key="pet.id" :value="pet.id">
            {{ pet.name }}
          </option>
        </select>
        <button class="btn btn-primary refresh-btn" @click="refreshMap">
          <i class="bi bi-arrow-clockwise"></i> Refresh
        </button>
      </div>
    </div>
    
    <card-component
      title="Live Pet Tracking"
      icon="bi bi-geo-alt"
      type="map"
      no-padding
    >
      <div class="full-map">
        <div class="map-placeholder">
          <i class="bi bi-map"></i>
          <h3>Interactive Map Coming Soon</h3>
          <p>We're working on integrating a real-time map for tracking your pets.</p>
        </div>
      </div>
    </card-component>
    
    <div class="map-legend">
      <div class="legend-item">
        <div class="legend-color" style="background-color: #4285F4;"></div>
        <div>Current Location</div>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background-color: #FBBC05;"></div>
        <div>Previous Location</div>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background-color: #34A853;"></div>
        <div>Safe Zone</div>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background-color: #EA4335;"></div>
        <div>Alert Zone</div>
      </div>
    </div>
    
    <div class="pet-locations">
      <h2 class="section-title">Recent Pet Locations</h2>
      
      <table class="locations-table">
        <thead>
          <tr>
            <th>Pet</th>
            <th>Time</th>
            <th>Location</th>
            <th>Speed</th>
            <th>Battery</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(location, index) in recentLocations" :key="index">
            <td>
              <div class="pet-cell">
                <div class="pet-avatar">
                  <i class="bi" :class="getPetIcon(location.petType)"></i>
                </div>
                <div>{{ location.petName }}</div>
              </div>
            </td>
            <td>{{ location.time }}</td>
            <td>{{ location.address }}</td>
            <td>{{ location.speed }} km/h</td>
            <td>
              <div class="battery-cell" :class="getBatteryClass(location.battery)">
                <i class="bi" :class="getBatteryIcon(location.battery)"></i>
                {{ location.battery }}%
              </div>
            </td>
            <td>
              <button class="btn btn-sm btn-outline-primary" @click="viewOnMap(location)">
                <i class="bi bi-geo-alt"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';
import CardComponent from '../components/common/CardComponent.vue';

export default {
  name: 'Map',
  components: {
    AppLayout,
    CardComponent
  },
  data() {
    return {
      selectedPet: 'all',
      pets: [
        { id: 1, name: 'Buddy', type: 'Dog' },
        { id: 2, name: 'Max', type: 'Dog' },
        { id: 3, name: 'Luna', type: 'Cat' }
      ],
      recentLocations: [
        {
          petName: 'Buddy',
          petType: 'Dog',
          time: '5 minutes ago',
          address: 'Central Park, New York',
          speed: 3.2,
          battery: 85
        },
        {
          petName: 'Max',
          petType: 'Dog',
          time: '15 minutes ago',
          address: 'Downtown, New York',
          speed: 1.5,
          battery: 72
        },
        {
          petName: 'Luna',
          petType: 'Cat',
          time: '32 minutes ago',
          address: 'River Park, New York',
          speed: 4.7,
          battery: 18
        }
      ]
    }
  },
  methods: {
    refreshMap() {
      console.log('Refreshing map data for pet:', this.selectedPet);
    },
    viewOnMap(location) {
      console.log('Viewing location on map:', location);
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
    getBatteryIcon(level) {
      if (level >= 80) return 'bi-battery-full';
      if (level >= 50) return 'bi-battery-half';
      if (level >= 20) return 'bi-battery-low';
      return 'bi-battery';
    },
    getBatteryClass(level) {
      if (level >= 60) return 'battery-good';
      if (level >= 30) return 'battery-medium';
      return 'battery-low';
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

.map-controls {
  display: flex;
  gap: 12px;
}

.select-pet {
  width: 200px;
}

.full-map {
  height: 500px;
  width: 100%;
}

.map-placeholder {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-light);
  color: var(--primary);
}

.map-placeholder i {
  font-size: 48px;
  margin-bottom: 16px;
}

.map-placeholder h3 {
  font-size: 24px;
  margin-bottom: 8px;
}

.map-placeholder p {
  font-size: 16px;
  max-width: 400px;
  text-align: center;
}

.map-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin: 20px 0 40px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.pet-locations {
  margin-top: 40px;
}

.locations-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.locations-table th,
.locations-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.locations-table th {
  color: var(--text-light);
  font-weight: 600;
  font-size: 14px;
}

.pet-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pet-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.battery-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.battery-good {
  color: var(--success);
}

.battery-medium {
  color: var(--warning);
}

.battery-low {
  color: var(--danger);
}

.btn-outline-primary {
  border: 1px solid var(--primary);
  color: var(--primary);
  background-color: transparent;
}

.btn-outline-primary:hover {
  background-color: var(--primary);
  color: white;
}
</style>
