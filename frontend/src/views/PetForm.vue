<template>
  <div class="pet-form">
    <h2>{{ isEditMode ? 'Edit Pet' : 'Add New Pet' }}</h2>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading pet data...</p>
    </div>
    
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>
    
    <form v-else @submit.prevent="savePet" class="mt-4">
      <div class="mb-3">
        <label for="petName" class="form-label">Pet Name <span class="text-danger">*</span></label>
        <input 
          type="text" 
          class="form-control" 
          id="petName" 
          v-model="pet.name" 
          required
          :class="{ 'is-invalid': errors.name }"
        >
        <div class="invalid-feedback" v-if="errors.name">{{ errors.name }}</div>
      </div>
      
      <div class="mb-3">
        <label for="petType" class="form-label">Pet Type <span class="text-danger">*</span></label>
        <select 
          class="form-select" 
          id="petType" 
          v-model="pet.pet_type" 
          required
          :class="{ 'is-invalid': errors.pet_type }"
        >
          <option value="">Select a pet type</option>
          <option v-for="type in petTypes" :key="type" :value="type">{{ type }}</option>
        </select>
        <div class="invalid-feedback" v-if="errors.pet_type">{{ errors.pet_type }}</div>
      </div>
      
      <div class="mb-3">
        <label for="breed" class="form-label">Breed</label>
        <input 
          type="text" 
          class="form-control" 
          id="breed" 
          v-model="pet.breed"
          :class="{ 'is-invalid': errors.breed }"
        >
        <div class="invalid-feedback" v-if="errors.breed">{{ errors.breed }}</div>
      </div>
      
      <div class="mb-3">
        <label for="color" class="form-label">Color</label>
        <input 
          type="text" 
          class="form-control" 
          id="color" 
          v-model="pet.color"
          :class="{ 'is-invalid': errors.color }"
        >
        <div class="invalid-feedback" v-if="errors.color">{{ errors.color }}</div>
      </div>
      
      <div class="mb-3">
        <label for="birthdate" class="form-label">Birthdate</label>
        <input 
          type="date" 
          class="form-control" 
          id="birthdate" 
          v-model="pet.birthdate"
          :class="{ 'is-invalid': errors.birthdate }"
        >
        <div class="invalid-feedback" v-if="errors.birthdate">{{ errors.birthdate }}</div>
      </div>
      
      <div class="mb-3">
        <label for="weight" class="form-label">Weight (kg)</label>
        <input 
          type="number" 
          step="0.1" 
          class="form-control" 
          id="weight" 
          v-model="pet.weight"
          :class="{ 'is-invalid': errors.weight }"
        >
        <div class="invalid-feedback" v-if="errors.weight">{{ errors.weight }}</div>
      </div>
      
      <div class="mb-3">
        <label for="description" class="form-label">Description</label>
        <textarea 
          class="form-control" 
          id="description" 
          rows="3" 
          v-model="pet.description"
          :class="{ 'is-invalid': errors.description }"
        ></textarea>
        <div class="invalid-feedback" v-if="errors.description">{{ errors.description }}</div>
      </div>
      
      <div class="mb-3">
        <label for="imageUrl" class="form-label">Image URL</label>
        <input 
          type="url" 
          class="form-control" 
          id="imageUrl" 
          v-model="pet.image_url"
          :class="{ 'is-invalid': errors.image_url }"
        >
        <div class="invalid-feedback" v-if="errors.image_url">{{ errors.image_url }}</div>
        <small class="form-text text-muted">Enter a URL to your pet's image</small>
      </div>
      
      <div class="d-flex justify-content-between mt-4">
        <router-link to="/pets" class="btn btn-secondary">
          Cancel
        </router-link>
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
          {{ submitting ? 'Saving...' : 'Save Pet' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PetForm',
  props: {
    id: {
      type: String,
      required: false
    }
  },
  data() {
    return {
      pet: {
        name: '',
        pet_type: '',
        breed: '',
        color: '',
        birthdate: '',
        weight: null,
        description: '',
        image_url: ''
      },
      petTypes: ['Dog', 'Cat', 'Bird', 'Other'],
      loading: false,
      submitting: false,
      error: null,
      errors: {}
    };
  },
  computed: {
    isEditMode() {
      return !!this.id;
    }
  },
  async created() {
    if (this.isEditMode) {
      await this.fetchPet();
    }
  },
  methods: {
    async fetchPet() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`/api/pets/${this.id}`);
        // Format birthdate for input type="date"
        if (response.data.birthdate) {
          response.data.birthdate = new Date(response.data.birthdate).toISOString().split('T')[0];
        }
        this.pet = response.data;
      } catch (error) {
        console.error('Error fetching pet:', error);
        this.error = error.response?.data?.message || 'Failed to load pet data';
      } finally {
        this.loading = false;
      }
    },
    async savePet() {
      this.submitting = true;
      this.errors = {};
      
      try {
        let response;
        if (this.isEditMode) {
          response = await axios.put(`/api/pets/${this.id}`, this.pet);
        } else {
          response = await axios.post('/api/pets', this.pet);
        }
        
        // Navigate back to pets list
        this.$router.push('/pets');
      } catch (error) {
        console.error('Error saving pet:', error);
        if (error.response?.status === 400 && error.response.data.errors) {
          // Validation errors
          this.errors = error.response.data.errors;
        } else {
          this.error = error.response?.data?.message || 'Failed to save pet';
        }
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>

<style scoped>
.pet-form {
  max-width: 800px;
  margin: 0 auto 50px auto;
}
</style>
