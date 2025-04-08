<template>
  <div class="pet-list-container">
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    
    <div v-else-if="pets.length === 0" class="text-center my-4">
      <p>No pets found. Add your first pet to get started!</p>
      <button class="btn btn-primary" @click="$emit('add-pet')">Add Pet</button>
    </div>
    
    <div v-else class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
      <div v-for="pet in pets" :key="pet.id" class="col">
        <div class="card h-100">
          <img 
            v-if="pet.image_url" 
            :src="pet.image_url" 
            class="card-img-top pet-image" 
            :alt="pet.name"
          >
          <div v-else class="card-img-top pet-image-placeholder">
            <i class="bi bi-image"></i>
          </div>
          
          <div class="card-body">
            <h5 class="card-title">{{ pet.name }}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{{ pet.pet_type }}</h6>
            <p class="card-text" v-if="pet.description">{{ pet.description }}</p>
            
            <div class="pet-details mt-3">
              <div v-if="pet.breed" class="detail-item">
                <span class="detail-label">Breed:</span> {{ pet.breed }}
              </div>
              <div v-if="pet.color" class="detail-item">
                <span class="detail-label">Color:</span> {{ pet.color }}
              </div>
              <div v-if="pet.weight" class="detail-item">
                <span class="detail-label">Weight:</span> {{ pet.weight }} kg
              </div>
              <div v-if="pet.birthdate" class="detail-item">
                <span class="detail-label">Age:</span> {{ calculateAge(pet.birthdate) }}
              </div>
            </div>
          </div>
          
          <div class="card-footer bg-transparent border-top-0 d-flex justify-content-between">
            <button 
              class="btn btn-sm btn-outline-primary" 
              @click="$emit('edit-pet', pet.id)"
            >
              Edit
            </button>
            <button 
              class="btn btn-sm btn-outline-danger" 
              @click="$emit('delete-pet', pet.id)"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { petsAPI } from '../services/api';

export default {
  name: 'PetList',
  emits: ['add-pet', 'edit-pet', 'delete-pet'],
  
  setup() {
    const pets = ref([]);
    const loading = ref(true);
    const error = ref(null);
    
    const fetchPets = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await petsAPI.getAll();
        pets.value = response.data;
      } catch (err) {
        console.error('Error fetching pets:', err);
        error.value = 'Failed to load pets. Please try again later.';
      } finally {
        loading.value = false;
      }
    };
    
    const calculateAge = (birthdate) => {
      if (!birthdate) return '';
      
      const birth = new Date(birthdate);
      const now = new Date();
      
      let years = now.getFullYear() - birth.getFullYear();
      const months = now.getMonth() - birth.getMonth();
      
      if (months < 0 || (months === 0 && now.getDate() < birth.getDate())) {
        years--;
      }
      
      return years > 0 ? `${years} years` : 'Less than 1 year';
    };
    
    onMounted(fetchPets);
    
    return {
      pets,
      loading,
      error,
      calculateAge
    };
  }
};
</script>

<style scoped>
.pet-list-container {
  padding: 1rem 0;
}

.pet-image {
  height: 200px;
  object-fit: cover;
}

.pet-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  background-color: var(--bs-gray-200);
  color: var(--bs-gray-600);
  font-size: 3rem;
}

.detail-label {
  font-weight: 500;
  margin-right: 0.25rem;
}

.detail-item {
  margin-bottom: 0.25rem;
}
</style>
