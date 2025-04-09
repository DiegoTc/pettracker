<template>
  <app-layout>
    <div class="page-header">
      <h1 class="page-title">My Pets</h1>
      <button class="btn btn-primary" @click="navigateTo('/pets/new')">
        <i class="bi bi-plus-lg"></i> Add New Pet
      </button>
    </div>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your pets...</p>
    </div>
    
    <div v-else-if="pets.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="bi bi-heart"></i>
      </div>
      <h3>No Pets Found</h3>
      <p>You haven't added any pets yet. Add your first pet to start tracking.</p>
      <button class="btn btn-primary" @click="navigateTo('/pets/new')">
        <i class="bi bi-plus-lg"></i> Add First Pet
      </button>
    </div>
    
    <div v-else class="pet-grid">
      <div v-for="pet in pets" :key="pet.id" class="pet-card" @click="navigateTo(`/pets/${pet.id}`)">
        <div class="pet-image">
          <img v-if="pet.image_url" :src="pet.image_url" :alt="pet.name">
          <div v-else class="pet-placeholder">
            <i class="bi" :class="getPetIcon(pet.pet_type)"></i>
          </div>
        </div>
        <div class="pet-info">
          <h3 class="pet-name">{{ pet.name }}</h3>
          <p class="pet-details">{{ pet.breed || pet.pet_type }}</p>
          <div class="pet-stats">
            <span v-if="pet.age" class="pet-age">
              <i class="bi bi-calendar3"></i> {{ pet.age }}
            </span>
            <span v-if="pet.weight" class="pet-weight">
              <i class="bi bi-speedometer"></i> {{ pet.weight }} kg
            </span>
          </div>
        </div>
        <div class="pet-actions">
          <button class="btn btn-sm btn-primary" @click.stop="navigateTo(`/pets/${pet.id}/edit`)">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger ms-2" @click.stop="confirmDelete(pet)">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal (placeholder) -->
    <div v-if="showDeleteModal" class="delete-modal">
      <!-- Modal content will go here -->
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';

export default {
  name: 'Pets',
  components: {
    AppLayout,
  },
  data() {
    return {
      pets: [],
      loading: true,
      showDeleteModal: false,
      petToDelete: null
    }
  },
  mounted() {
    this.fetchPets();
  },
  methods: {
    fetchPets() {
      // Simulate API call for now - will replace with actual API call
      setTimeout(() => {
        this.pets = [
          {
            id: 1,
            name: 'Buddy',
            pet_type: 'Dog',
            breed: 'Golden Retriever',
            weight: 28.5,
            age: '3 years',
            image_url: null
          },
          {
            id: 2,
            name: 'Luna',
            pet_type: 'Cat',
            breed: 'Maine Coon',
            weight: 5.2,
            age: '2 years',
            image_url: null
          },
          {
            id: 3,
            name: 'Max',
            pet_type: 'Dog',
            breed: 'Labrador',
            weight: 32.1,
            age: '5 years',
            image_url: null
          }
        ];
        this.loading = false;
      }, 1000);
      
      // Real API call will look like this:
      /*
      fetch('/api/pets')
        .then(response => response.json())
        .then(data => {
          this.pets = data;
          this.loading = false;
        })
        .catch(error => {
          console.error('Error fetching pets:', error);
          this.loading = false;
        });
      */
    },
    navigateTo(route) {
      this.$router.push(route);
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
    confirmDelete(pet) {
      this.petToDelete = pet;
      this.showDeleteModal = true;
      // In a real implementation, show a modal confirmation dialog
      // For now, we'll just log a message
      console.log(`Request to delete pet: ${pet.name}`);
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

.pet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.pet-card {
  background-color: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.pet-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.pet-image {
  height: 180px;
  background-color: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.pet-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pet-placeholder {
  width: 80px;
  height: 80px;
  background-color: var(--primary-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-dark);
  font-size: 40px;
}

.pet-info {
  padding: 20px;
}

.pet-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 5px;
}

.pet-details {
  color: var(--text-light);
  margin-bottom: 12px;
}

.pet-stats {
  display: flex;
  gap: 12px;
}

.pet-stats span {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--text-light);
}

.pet-stats i {
  margin-right: 5px;
}

.pet-actions {
  padding: 0 20px 20px;
  display: flex;
  justify-content: flex-end;
}
</style>