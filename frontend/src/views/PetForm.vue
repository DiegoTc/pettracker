<template>
  <app-layout>
    <div class="page-header">
      <div class="d-flex align-items-center">
        <button class="btn btn-outline-secondary me-3" @click="$router.go(-1)">
          <i class="bi bi-arrow-left"></i>
        </button>
        <h1 class="page-title mb-0">{{ isEditMode ? 'Edit Pet' : 'Add New Pet' }}</h1>
      </div>
    </div>

    <div class="form-container">
      <card-component :title="isEditMode ? 'Edit Pet Information' : 'Pet Information'" icon="bi bi-pencil-square">
        <form @submit.prevent="savePet">
          <div class="form-group">
            <label for="petName" class="form-label">Pet Name</label>
            <input 
              type="text" 
              id="petName" 
              v-model="pet.name" 
              class="form-control" 
              required 
              placeholder="Enter pet name"
            >
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="petType" class="form-label">Pet Type</label>
              <select id="petType" v-model="pet.pet_type" class="form-select" required>
                <option value="" disabled selected>Select a pet type</option>
                <option value="Dog">Dog</option>
                <option value="Cat">Cat</option>
                <option value="Bird">Bird</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div class="form-group">
              <label for="breed" class="form-label">Breed</label>
              <input 
                type="text" 
                id="breed" 
                v-model="pet.breed" 
                class="form-control" 
                placeholder="Enter breed (optional)"
              >
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="color" class="form-label">Color</label>
              <input 
                type="text" 
                id="color" 
                v-model="pet.color" 
                class="form-control" 
                placeholder="Enter color (optional)"
              >
            </div>

            <div class="form-group">
              <label for="weight" class="form-label">Weight (kg)</label>
              <input 
                type="number" 
                id="weight" 
                v-model="pet.weight" 
                class="form-control" 
                step="0.1"
                min="0"
                placeholder="Enter weight (optional)"
              >
            </div>
          </div>

          <div class="form-group">
            <label for="birthdate" class="form-label">Birthdate</label>
            <input 
              type="date" 
              id="birthdate" 
              v-model="pet.birthdate" 
              class="form-control"
            >
          </div>

          <div class="form-group">
            <label for="description" class="form-label">Description</label>
            <textarea 
              id="description" 
              v-model="pet.description" 
              class="form-control" 
              rows="5"
              placeholder="Enter a description about your pet (optional)"
            ></textarea>
          </div>

          <div class="form-group">
            <label for="image" class="form-label">Pet Image</label>
            <div class="image-upload-container">
              <div class="image-preview" v-if="pet.image_url">
                <img :src="pet.image_url" alt="Pet preview">
                <button type="button" class="btn-remove-image" @click="removeImage">
                  <i class="bi bi-x-circle-fill"></i>
                </button>
              </div>
              <div class="image-upload" v-else>
                <label for="image" class="upload-label">
                  <i class="bi bi-cloud-upload"></i>
                  <span>Click to upload image</span>
                </label>
                <input 
                  type="file" 
                  id="image" 
                  class="form-control" 
                  @change="handleImageUpload"
                  accept="image/*"
                  hidden
                >
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="$router.go(-1)">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              {{ isEditMode ? 'Update Pet' : 'Add Pet' }}
            </button>
          </div>
        </form>
      </card-component>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';
import CardComponent from '../components/common/CardComponent.vue';

export default {
  name: 'PetForm',
  components: {
    AppLayout,
    CardComponent
  },
  data() {
    return {
      pet: {
        name: '',
        pet_type: '',
        breed: '',
        color: '',
        weight: null,
        birthdate: '',
        description: '',
        image_url: null
      },
      isLoading: false
    }
  },
  computed: {
    isEditMode() {
      return this.$route.path.includes('/edit');
    },
    petId() {
      return this.$route.params.id;
    }
  },
  mounted() {
    if (this.isEditMode) {
      this.fetchPetDetails();
    }
  },
  methods: {
    fetchPetDetails() {
      // Simulate API call
      setTimeout(() => {
        this.pet = {
          id: this.petId,
          name: 'Buddy',
          pet_type: 'Dog',
          breed: 'Golden Retriever',
          color: 'Golden',
          weight: 28.5,
          birthdate: '2022-03-15',
          description: 'Buddy is a friendly and energetic dog who loves to play fetch and go for long walks in the park. He is good with children and other pets.',
          image_url: null
        };
      }, 500);
      
      // Real API call will look like:
      /*
      fetch(`/api/pets/${this.petId}`)
        .then(response => {
          if (!response.ok) throw new Error('Pet not found');
          return response.json();
        })
        .then(data => {
          this.pet = data;
        })
        .catch(error => {
          console.error('Error fetching pet details:', error);
          this.$router.push('/pets');
        });
      */
    },
    savePet() {
      this.isLoading = true;
      
      console.log('Saving pet:', this.pet);
      
      // Simulate API save
      setTimeout(() => {
        this.isLoading = false;
        this.$router.push('/pets');
      }, 1000);
      
      // Real API call will look like:
      /*
      const url = this.isEditMode ? `/api/pets/${this.petId}` : '/api/pets';
      const method = this.isEditMode ? 'PUT' : 'POST';
      
      fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this.pet)
      })
        .then(response => {
          if (!response.ok) throw new Error('Failed to save pet');
          return response.json();
        })
        .then(data => {
          this.$router.push('/pets');
        })
        .catch(error => {
          console.error('Error saving pet:', error);
          this.isLoading = false;
        });
      */
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // For demo just use a local URL
      this.pet.image_url = URL.createObjectURL(file);
      
      // In a real implementation we would upload to server
    },
    removeImage() {
      this.pet.image_url = null;
    }
  }
}
</script>

<style scoped>
.form-container {
  max-width: 900px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
}

.image-upload-container {
  width: 100%;
  margin-top: 8px;
}

.image-upload {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: a24px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: var(--background);
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  color: var(--text-light);
}

.upload-label i {
  font-size: 48px;
  margin-bottom: 8px;
}

.image-preview {
  position: relative;
  height: 200px;
  border-radius: var(--radius);
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-remove-image:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

.btn-secondary {
  background-color: var(--background);
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background-color: var(--border);
}
</style>
