<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/index.js'
import { useEmployeeStore } from '@/stores/employee.js'

const store = useEmployeeStore()

const projects = ref([])
const notification = ref(null) // { type: 'success' | 'error', message: string }
const emailChecked = ref(false)

const emptyForm = () => ({
  full_name: '',
  email: '',
  experience_level: '',
  tech_stack: '',
  preferred_duration: '',
  additional_skills: '',
  availability_confirmed: false,
  project_ids: [],
})

const form = ref(emptyForm())

const isUpdate = computed(() => !!store.employee?.id)
const emailLocked = computed(() => isUpdate.value)

onMounted(async () => {
  projects.value = await api.getProjects().catch(() => [])
  await store.loadStoredEmployee()
  if (store.employee) fillForm(store.employee)
})

function fillForm(emp) {
  form.value.full_name = emp.full_name
  form.value.email = emp.email
  form.value.experience_level = emp.experience_level
  form.value.tech_stack = emp.tech_stack
  form.value.preferred_duration = emp.preferred_duration
  form.value.additional_skills = emp.additional_skills ?? ''
  form.value.availability_confirmed = emp.availability_confirmed
  form.value.project_ids = emp.projects.map((p) => p.id)
}

async function handleEmailBlur() {
  if (emailChecked.value || !form.value.email || store.employee) return
  emailChecked.value = true

  const found = await store.lookupByEmail(form.value.email)
  if (found) {
    fillForm(found)
    notify('success', 'Existing profile loaded — update your information and click Save Profile.')
  }
}

async function handleSubmit() {
  if (!form.value.availability_confirmed) {
    notify('error', 'Please confirm your availability before saving.')
    return
  }
  try {
    await store.saveEmployee({ ...form.value })
    notify(
      'success',
      isUpdate.value ? 'Profile updated successfully!' : 'Profile registered successfully!',
    )
  } catch (e) {
    notify('error', store.error ?? e.message)
  }
}

function handleClear() {
  form.value = emptyForm()
  store.clear()
  notification.value = null
  emailChecked.value = false
}

function notify(type, message) {
  notification.value = { type, message }
  if (type === 'success') setTimeout(() => (notification.value = null), 5000)
}
</script>

<template>
  <div class="page">
    <div class="card">
      <h1 class="card-title">Project Assignment Form</h1>
      <p class="card-subtitle">Complete your profile to get assigned to internal projects.</p>

      <Transition name="fade">
        <div v-if="notification" :class="['notification', notification.type]" role="alert">
          {{ notification.message }}
          <button class="notif-close" @click="notification = null" aria-label="Dismiss">×</button>
        </div>
      </Transition>

      <form @submit.prevent="handleSubmit" novalidate>
        <!-- Full Name -->
        <div class="field">
          <label for="full_name">Full Name</label>
          <input
            id="full_name"
            v-model="form.full_name"
            type="text"
            placeholder="Jane Doe"
            required
          />
        </div>

        <!-- Email -->
        <div class="field">
          <label for="email">
            Email Address
            <span v-if="store.loading" class="badge loading">Looking up…</span>
            <span v-else-if="emailLocked" class="badge locked">Profile loaded</span>
          </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="jane@company.com"
            :readonly="emailLocked"
            :class="{ 'input-locked': emailLocked }"
            @blur="handleEmailBlur"
            required
          />
        </div>

        <!-- Experience Level -->
        <div class="field">
          <label for="experience_level">Experience Level</label>
          <select id="experience_level" v-model="form.experience_level" required>
            <option value="">Select your level</option>
            <option value="junior">Junior (0–2 years)</option>
            <option value="mid">Mid-level (2–5 years)</option>
            <option value="senior">Senior (5+ years)</option>
          </select>
        </div>

        <!-- Tech Stack -->
        <div class="field">
          <label for="tech_stack">Primary Technology Stack</label>
          <select id="tech_stack" v-model="form.tech_stack" required>
            <option value="">Choose one</option>
            <option value="backend">Backend Development</option>
            <option value="frontend">Frontend Development</option>
            <option value="fullstack">Full-Stack Development</option>
            <option value="data">Data Engineering</option>
            <option value="devops">DevOps</option>
            <option value="mobile">Mobile Development</option>
          </select>
        </div>

        <!-- Available Projects — populated dynamically from the API -->
        <div class="field">
          <label for="projects">
            Available Projects
            <span class="hint">Hold Ctrl / ⌘ to select multiple</span>
          </label>
          <select id="projects" v-model="form.project_ids" multiple class="multi-select">
            <option v-if="projects.length === 0" disabled value="">Loading projects…</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">
              {{ p.name }}
            </option>
          </select>
        </div>

        <!-- Preferred Duration -->
        <div class="field">
          <label>Preferred Project Duration</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" v-model="form.preferred_duration" value="short" />
              Short-term (1–3 months)
            </label>
            <label class="radio-label">
              <input type="radio" v-model="form.preferred_duration" value="medium" />
              Medium-term (3–6 months)
            </label>
            <label class="radio-label">
              <input type="radio" v-model="form.preferred_duration" value="long" />
              Long-term (6+ months)
            </label>
          </div>
        </div>

        <!-- Additional Skills -->
        <div class="field">
          <label for="additional_skills">
            Additional Skills
            <span class="optional">optional</span>
          </label>
          <input
            id="additional_skills"
            v-model="form.additional_skills"
            type="text"
            placeholder="e.g. Python, Docker, React"
          />
        </div>

        <!-- Availability Confirmation -->
        <div class="field">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.availability_confirmed" />
            I confirm my availability for the selected projects
          </label>
        </div>

        <!-- Actions -->
        <div class="actions">
          <button type="submit" class="btn-primary" :disabled="store.loading">
            {{ store.loading ? 'Saving…' : isUpdate ? 'Update Profile' : 'Save Profile' }}
          </button>
          <button type="button" class="btn-secondary" @click="handleClear">Clear Form</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2.5rem 1rem;
}

.card {
  width: 100%;
  max-width: 580px;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 2.5rem;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 0.4rem;
}

.card-subtitle {
  color: var(--color-text);
  opacity: 0.7;
  margin-bottom: 1.8rem;
}

/* ── Notification ─────────────────────────────────────────── */
.notification {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.notification.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #6ee7b7;
}

.notification.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.notif-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0;
  color: inherit;
  opacity: 0.6;
}

.notif-close:hover {
  opacity: 1;
}

/* ── Form Fields ──────────────────────────────────────────── */
.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 1.2rem;
}

.field label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-heading);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field input[type='text'],
.field input[type='email'],
.field select {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-border-hover);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.95rem;
  transition: border-color 0.2s;
  width: 100%;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: hsla(160, 100%, 37%, 0.8);
}

.input-locked {
  opacity: 0.65;
  cursor: not-allowed;
  background: var(--color-background-mute) !important;
}

/* ── Multi-select ─────────────────────────────────────────── */
.multi-select {
  height: 220px;
  padding: 0.25rem;
}

.multi-select option {
  padding: 0.4rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.multi-select option:checked {
  background: hsla(160, 100%, 37%, 0.15);
  color: var(--color-heading);
}

/* ── Radio Group ──────────────────────────────────────────── */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: normal !important;
  color: var(--color-text) !important;
}

/* ── Checkbox ─────────────────────────────────────────────── */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: normal !important;
  color: var(--color-text) !important;
}

/* ── Badges ───────────────────────────────────────────────── */
.badge {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
}

.badge.loading {
  background: #fef3c7;
  color: #92400e;
}

.badge.locked {
  background: #d1fae5;
  color: #065f46;
}

.hint {
  font-size: 0.75rem;
  color: var(--color-text);
  opacity: 0.55;
  font-weight: normal;
}

.optional {
  font-size: 0.75rem;
  color: var(--color-text);
  opacity: 0.5;
  font-style: italic;
  font-weight: normal;
}

/* ── Actions ──────────────────────────────────────────────── */
.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.8rem;
}

button {
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition:
    background 0.2s,
    opacity 0.2s;
}

.btn-primary {
  background: hsla(160, 100%, 37%, 1);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: hsla(160, 100%, 30%, 1);
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  color: var(--color-text);
  border-color: var(--color-border-hover);
}

.btn-secondary:hover {
  background: var(--color-background-mute);
}

/* ── Fade transition for notification ────────────────────── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
