<template>
  <app-layout>
    <div class="page-header">
      <h1 class="page-title">Activity Reports</h1>
      <div class="report-controls">
        <select v-model="selectedPet" class="form-select select-pet">
          <option value="all">All Pets</option>
          <option v-for="pet in pets" :key="pet.id" :value="pet.id">
            {{ pet.name }}
          </option>
        </select>
        <select v-model="selectedPeriod" class="form-select select-period">
          <option value="day">Last 24 Hours</option>
          <option value="week">Last 7 Days</option>
          <option value="month">Last 30 Days</option>
          <option value="custom">Custom Range</option>
        </select>
      </div>
    </div>
    
    <div class="report-cards">
      <card-component title="Activity Overview" icon="bi bi-activity">
        <div class="report-placeholder">
          <i class="bi bi-bar-chart"></i>
          <h3>Activity Chart Coming Soon</h3>
          <p>We're working on adding detailed activity tracking reports.</p>
        </div>
      </card-component>
      
      <card-component title="Movement Patterns" icon="bi bi-map">
        <div class="report-placeholder">
          <i class="bi bi-geo-alt"></i>
          <h3>Movement Map Coming Soon</h3>
          <p>Soon you'll be able to visualize your pet's movement patterns.</p>
        </div>
      </card-component>
      
      <card-component title="Activity Statistics" icon="bi bi-clipboard-data">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">Active Time</div>
            <div class="stat-value">4.5 hours</div>
            <div class="stat-change positive">
              <i class="bi bi-arrow-up-right"></i> +15% from last week
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-label">Distance</div>
            <div class="stat-value">3.2 km</div>
            <div class="stat-change positive">
              <i class="bi bi-arrow-up-right"></i> +8% from last week
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-label">Avg. Speed</div>
            <div class="stat-value">2.4 km/h</div>
            <div class="stat-change neutral">
              <i class="bi bi-dash"></i> No change
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-label">Rest Time</div>
            <div class="stat-value">12.3 hours</div>
            <div class="stat-change negative">
              <i class="bi bi-arrow-down-right"></i> -10% from last week
            </div>
          </div>
        </div>
      </card-component>
      
      <card-component title="Health Indicators" icon="bi bi-heart-pulse">
        <div class="report-placeholder">
          <i class="bi bi-heart"></i>
          <h3>Health Tracking Coming Soon</h3>
          <p>Advanced health tracking features are coming to help monitor your pet's wellbeing.</p>
        </div>
      </card-component>
    </div>
    
    <div class="activity-history">
      <h2 class="section-title">Activity History</h2>
      
      <table class="activity-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Pet</th>
            <th>Activity</th>
            <th>Duration</th>
            <th>Location</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(activity, index) in activities" :key="index">
            <td>{{ activity.date }}</td>
            <td>
              <div class="pet-cell">
                <div class="pet-avatar">
                  <i class="bi" :class="getPetIcon(activity.petType)"></i>
                </div>
                <div>{{ activity.petName }}</div>
              </div>
            </td>
            <td>{{ activity.type }}</td>
            <td>{{ activity.duration }}</td>
            <td>{{ activity.location }}</td>
          </tr>
        </tbody>
      </table>
      
      <div class="pagination">
        <button class="btn btn-sm btn-outline-secondary">
          <i class="bi bi-chevron-left"></i> Previous
        </button>
        <div class="page-info">Page 1 of 5</div>
        <button class="btn btn-sm btn-outline-secondary">
          Next <i class="bi bi-chevron-right"></i>
        </button>
      </div>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';
import CardComponent from '../components/common/CardComponent.vue';

export default {
  name: 'Reports',
  components: {
    AppLayout,
    CardComponent
  },
  data() {
    return {
      selectedPet: 'all',
      selectedPeriod: 'week',
      pets: [
        { id: 1, name: 'Buddy', type: 'Dog' },
        { id: 2, name: 'Max', type: 'Dog' },
        { id: 3, name: 'Luna', type: 'Cat' }
      ],
      activities: [
        {
          date: 'Today, 10:15 AM',
          petName: 'Buddy',
          petType: 'Dog',
          type: 'Walking',
          duration: '45 minutes',
          location: 'Central Park'
        },
        {
          date: 'Today, 8:30 AM',
          petName: 'Max',
          petType: 'Dog',
          type: 'Running',
          duration: '30 minutes',
          location: 'River Trail'
        },
        {
          date: 'Yesterday, 4:20 PM',
          petName: 'Luna',
          petType: 'Cat',
          type: 'Playing',
          duration: '15 minutes',
          location: 'Home'
        },
        {
          date: 'Yesterday, 9:45 AM',
          petName: 'Buddy',
          petType: 'Dog',
          type: 'Walking',
          duration: '35 minutes',
          location: 'Downtown'
        },
        {
          date: '2 days ago, 11:30 AM',
          petName: 'Max',
          petType: 'Dog',
          type: 'Playing',
          duration: '20 minutes',
          location: 'Dog Park'
        }
      ]
    }
  },
  methods: {
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

.report-controls {
  display: flex;
  gap: 12px;
}

.select-pet, .select-period {
  min-width: 150px;
}

.report-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

@media (max-width: 992px) {
  .report-cards {
    grid-template-columns: 1fr;
  }
}

.report-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-light);
  text-align: center;
}

.report-placeholder i {
  font-size: 48px;
  color: var(--primary);
  margin-bottom: 16px;
}

.report-placeholder h3 {
  font-size: 18px;
  margin-bottom: 8px;
  color: var(--text);
}

.report-placeholder p {
  font-size: 14px;
  max-width: 300px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.stat-item {
  padding: 16px;
  background-color: var(--background);
  border-radius: var(--radius);
}

.stat-label {
  font-size: 14px;
  color: var(--text-light);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-change {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.positive {
  color: var(--success);
}

.negative {
  color: var(--danger);
}

.neutral {
  color: var(--text-lighter);
}

.activity-history {
  margin-top: 40px;
}

.activity-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.activity-table th,
.activity-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.activity-table th {
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.page-info {
  font-size: 14px;
  color: var(--text-light);
}

.btn-outline-secondary {
  border: 1px solid var(--border);
  color: var(--text);
  background-color: transparent;
}

.btn-outline-secondary:hover {
  background-color: var(--border);
}
</style>
