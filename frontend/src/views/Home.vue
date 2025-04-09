<template>
  <app-layout>
    <h1 class="page-title">Dashboard</h1>
    
    <!-- Stats Cards -->
    <div class="card-grid">
      <stat-card 
        title="Total Pets"
        :value="stats.totalPets"
        icon="bi bi-heart-fill"
        change="+2 since last month"
        change-type="positive"
      />
      
      <stat-card 
        title="Active Devices"
        :value="stats.activeDevices"
        icon="bi bi-cpu-fill"
        change="No change"
        change-type="neutral"
      />
      
      <stat-card 
        title="Tracked Locations"
        :value="stats.totalLocations"
        icon="bi bi-geo-alt-fill"
        change="+287 since yesterday"
        change-type="positive"
      />
      
      <stat-card 
        title="Activity Score"
        :value="stats.activityScore"
        icon="bi bi-activity"
        change="+5% since last week"
        change-type="positive"
      />
    </div>
    
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
        <div class="map-container">
          <!-- Map component will go here -->
          <div>Interactive Map Coming Soon</div>
        </div>
      </card-component>
      
      <card-component 
        title="Recent Activity"
        icon="bi bi-clock-history"
        show-more
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

export default {
  name: 'Home',
  components: {
    AppLayout,
    StatCard,
    CardComponent,
    ActivityItem,
    ActionCard
  },
  data() {
    return {
      stats: {
        totalPets: 8,
        activeDevices: 5,
        totalLocations: 1234,
        activityScore: 87
      },
      recentActivity: [
        {
          petName: 'Buddy',
          location: 'Central Park',
          timeAgo: '5 min ago',
          batteryLevel: 85,
          speed: 3.2
        },
        {
          petName: 'Max',
          location: 'Downtown',
          timeAgo: '15 min ago',
          batteryLevel: 72,
          speed: 1.5
        },
        {
          petName: 'Charlie',
          location: 'River Park',
          timeAgo: '32 min ago',
          batteryLevel: 91,
          speed: 4.7
        },
        {
          petName: 'Luna',
          location: 'Dog Park',
          timeAgo: '1 hour ago',
          batteryLevel: 64,
          speed: 0.8
        }
      ]
    }
  },
  methods: {
    refreshMap() {
      // Implement map refresh
      console.log('Refreshing map...');
    },
    navigateTo(route) {
      this.$router.push(route);
    }
  }
}
</script>