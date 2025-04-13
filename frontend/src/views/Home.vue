<template>
  <app-layout>
    <h1 class="page-title">Dashboard</h1>
    
    <!-- Stats Cards -->
    <loading-state
      :loading="loadingStats"
      :error="statsError"
      :retry-enabled="true"
      error-message="Could not fetch dashboard statistics. Please try again."
      @retry="fetchDashboardStats"
      full-height
    >
      <div class="card-grid">
        <stat-card 
          title="Total Pets"
          :value="stats.totalPets"
          icon="bi bi-heart-fill"
          :change="statsChangeText.pets"
          :change-type="stats.totalPets > 0 ? 'positive' : 'neutral'"
        />
        
        <stat-card 
          title="Active Devices"
          :value="stats.activeDevices"
          icon="bi bi-cpu-fill"
          :change="statsChangeText.devices"
          change-type="neutral"
        />
        
        <stat-card 
          title="Tracked Locations"
          :value="stats.totalLocations"
          icon="bi bi-geo-alt-fill"
          :change="statsChangeText.locations"
          :change-type="stats.totalLocations > 0 ? 'positive' : 'neutral'"
        />
        
        <stat-card 
          v-if="stats.activityScore !== null"
          title="Activity Score"
          :value="stats.activityScore"
          icon="bi bi-activity"
          :change="statsChangeText.activity"
          change-type="neutral"
        />
        
        <stat-card 
          v-else
          title="Activity Score"
          value="N/A"
          icon="bi bi-activity"
          change="Calculating score..."
          change-type="neutral"
        />
      </div>
    </loading-state>
    
    <!-- Main Content Cards -->
    <div class="main-cards">
      <card-component 
        title="Pet Locations"
        icon="bi bi-geo-alt"
        type="map"
        no-padding
        show-refresh
        @refresh="refreshMap"
      >
        <coming-soon 
          title="Interactive Map"
          description="A real-time map showing your pets' locations is coming soon. Stay tuned for updates!"
        />
      </card-component>
      
      <card-component 
        title="Recent Activity"
        icon="bi bi-clock-history"
        show-more
      >
        <loading-state
          :loading="loadingActivities"
          :error="activitiesError"
          :empty="recentActivity.length === 0"
          :retry-enabled="true"
          empty-message="No recent activity found. Add devices and pets to see location updates here."
          error-message="Could not fetch recent activities. Please try again."
          @retry="fetchRecentActivities"
          full-height
        >
          <div class="activity-list">
            <activity-item
              v-for="(activity, index) in recentActivity"
              :key="index"
              :pet-name="activity.petName"
              :location="activity.location"
              :time-ago="activity.timeAgo"
              :battery-level="activity.batteryLevel"
              :speed="activity.speed"
            />
          </div>
        </loading-state>
      </card-component>
    </div>
    
    <!-- Quick Actions Section -->
    <div class="quick-access">
      <h2 class="section-title">Quick Actions</h2>
      
      <div class="quick-cards">
        <action-card
          title="Add Pet"
          description="Register a new pet in the system"
          icon="bi bi-plus-lg"
          button-text="Add Pet"
          button-icon="bi bi-plus-circle"
          button-type="primary"
          @action="navigateTo('/pets/new')"
        />
        
        <action-card
          title="Register Device"
          description="Connect a new tracking device"
          icon="bi bi-cpu"
          button-text="Add Device"
          button-icon="bi bi-plus-circle"
          button-type="secondary"
          @action="navigateTo('/devices/new')"
        />
        
        <action-card
          title="View Map"
          description="See where your pets are located"
          icon="bi bi-geo-alt"
          button-text="Open Map"
          button-icon="bi bi-map"
          button-type="success"
          @action="navigateTo('/map')"
        />
        
        <action-card
          title="Reports"
          description="View activity and health reports"
          icon="bi bi-file-earmark-text"
          button-text="View Reports"
          button-icon="bi bi-bar-chart"
          button-type="warning"
          @action="navigateTo('/reports')"
        />
      </div>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';
import StatCard from '../components/common/StatCard.vue';
import CardComponent from '../components/common/CardComponent.vue';
import ActivityItem from '../components/common/ActivityItem.vue';
import ActionCard from '../components/common/ActionCard.vue';
import LoadingState from '../components/common/LoadingState.vue';
import ComingSoon from '../components/common/ComingSoon.vue';
import { dashboardAPI } from '../services/api';

export default {
  name: 'Home',
  components: {
    AppLayout,
    StatCard,
    CardComponent,
    ActivityItem,
    ActionCard,
    LoadingState,
    ComingSoon
  },
  data() {
    return {
      // Dashboard statistics
      stats: {
        totalPets: 0,
        totalDevices: 0,
        activeDevices: 0,
        totalLocations: 0,
        activityScore: null
      },
      statsChangeText: {
        pets: 'Loading...',
        devices: 'Loading...',
        locations: 'Loading...',
        activity: 'Loading...'
      },
      loadingStats: true,
      statsError: false,
      
      // Recent activity
      recentActivity: [],
      loadingActivities: true,
      activitiesError: false
    }
  },
  created() {
    // Fetch dashboard data when component is created
    this.fetchDashboardStats();
    this.fetchRecentActivities();
  },
  methods: {
    async fetchDashboardStats() {
      // Reset loading state
      this.loadingStats = true;
      this.statsError = false;
      
      try {
        console.log('Fetching dashboard statistics...');
        const statsData = await dashboardAPI.getStats();
        
        // Update stats with real data
        this.stats = statsData;
        
        // Generate change text based on the stats
        this.generateStatsChangeText();
        
        console.log('Dashboard statistics loaded:', this.stats);
      } catch (error) {
        console.error('Error fetching dashboard statistics:', error);
        this.statsError = true;
      } finally {
        this.loadingStats = false;
      }
    },
    
    async fetchRecentActivities() {
      // Reset loading state
      this.loadingActivities = true;
      this.activitiesError = false;
      
      try {
        console.log('Fetching recent activities...');
        const activities = await dashboardAPI.getRecentActivities(5);
        
        // Update activities with real data
        this.recentActivity = activities;
        
        console.log('Recent activities loaded:', this.recentActivity);
      } catch (error) {
        console.error('Error fetching recent activities:', error);
        this.activitiesError = true;
      } finally {
        this.loadingActivities = false;
      }
    },
    
    generateStatsChangeText() {
      // Generate contextually relevant change text based on the actual stats
      
      // Pets change text
      if (this.stats.totalPets === 0) {
        this.statsChangeText.pets = 'No pets added yet';
      } else if (this.stats.totalPets === 1) {
        this.statsChangeText.pets = '1 pet registered';
      } else {
        this.statsChangeText.pets = `${this.stats.totalPets} pets registered`;
      }
      
      // Devices change text
      if (this.stats.activeDevices === 0) {
        this.statsChangeText.devices = 'No active devices';
      } else {
        const percentage = Math.round((this.stats.activeDevices / this.stats.totalDevices) * 100);
        this.statsChangeText.devices = `${percentage}% of devices active`;
      }
      
      // Locations change text
      if (this.stats.totalLocations === 0) {
        this.statsChangeText.locations = 'No locations tracked yet';
      } else if (this.stats.totalLocations < 10) {
        this.statsChangeText.locations = 'Getting started with tracking';
      } else if (this.stats.totalLocations < 100) {
        this.statsChangeText.locations = 'Tracking is active';
      } else {
        this.statsChangeText.locations = 'Active tracking history';
      }
      
      // Activity score change text
      if (this.stats.activityScore === null) {
        this.statsChangeText.activity = 'Insufficient data';
      } else if (this.stats.activityScore < 30) {
        this.statsChangeText.activity = 'Low activity detected';
      } else if (this.stats.activityScore < 70) {
        this.statsChangeText.activity = 'Moderate activity level';
      } else {
        this.statsChangeText.activity = 'High activity level';
      }
    },
    
    refreshMap() {
      // This would refresh the map once implemented
      console.log('Refreshing map...');
    },
    
    navigateTo(route) {
      this.$router.push(route);
    }
  }
}
</script>

<style scoped>
.map-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border-radius: 0.5rem;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.main-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-title {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.quick-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .main-cards {
    grid-template-columns: 1fr;
  }
}
</style>