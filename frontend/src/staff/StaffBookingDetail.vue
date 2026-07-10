<template>
  <StaffPortalShell title="Booking detail">
    <section v-if="loading" class="detail-card detail-card--state" aria-label="Loading booking">
      <div class="skeleton-block" />
      <div class="skeleton-block skeleton-block--short" />
    </section>
    <section v-else-if="errorMessage" class="detail-card detail-card--state" role="alert">
      <h2>Booking could not load.</h2>
      <p>{{ errorMessage }}</p>
      <button type="button" @click="loadDetail">Try again</button>
    </section>
    <section v-else-if="detail" class="detail-card">
      <p class="eyebrow">Appointment</p>
      <h2>{{ detail.client }} · {{ detail.service }}</h2>
      <div class="detail-grid">
        <span>{{ detail.localDate }} · {{ detail.time }}{{ detail.endTime ? `–${detail.endTime}` : '' }}</span>
        <StaffStatusChip :status="detail.bookingStatus" />
        <StaffStatusChip :status="detail.paymentStatus" />
        <span v-if="detail.amount">{{ detail.currency }} {{ detail.amount }}</span>
      </div>

      <div v-if="revealedContact" class="contact-reveal" role="status">
        <p><strong>Email</strong> {{ revealedContact.email }}</p>
        <p><strong>Phone</strong> {{ revealedContact.phone }}</p>
      </div>

      <div class="actions">
        <button type="button" @click="showReauth = true">Reveal customer contact</button>
        <button type="button" :disabled="completed" @click="completed = true">
          {{ completed ? 'Service completed' : 'Mark service completed' }}
        </button>
        <NuxtLink to="/staff/bookings">Back to bookings</NuxtLink>
      </div>
    </section>

    <StaffContactRevealModal
      v-if="showReauth"
      :api-base-url="props.apiBaseUrl"
      @close="showReauth = false"
      @confirmed="onReauthConfirmed"
    />
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { ensureBookingCsrfToken } from '../booking/bookingCsrf'
import StaffContactRevealModal from './StaffContactRevealModal.vue'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import {
  getStaffBookingDetail,
  postStaffContactAccess,
  type StaffBookingDetailData,
} from './staffPortalApi'

const props = withDefaults(
  defineProps<{
    /** Injected by Nuxt pages — never call useRuntimeConfig inside src/ components. */
    apiBaseUrl?: string
    publicBookingId?: string
  }>(),
  { apiBaseUrl: '', publicBookingId: '' },
)

const showReauth = ref(false)
const completed = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const detail = ref<StaffBookingDetailData | null>(null)
const revealedContact = ref<{ email: string; phone: string } | null>(null)

const demoDetail: StaffBookingDetailData = {
  publicBookingId: 'demo',
  localDate: 'Today',
  time: '09:00',
  endTime: '',
  client: 'Grace M.',
  service: 'Soft glam makeup',
  bookingStatus: 'confirmed',
  paymentStatus: 'paid',
  amount: '4,500',
  currency: 'KES',
  resource: '',
}

if (!props.publicBookingId) {
  detail.value = demoDetail
}

async function loadDetail() {
  if (!props.apiBaseUrl || !props.publicBookingId) {
    detail.value = demoDetail
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await getStaffBookingDetail(props.apiBaseUrl, props.publicBookingId)
    if (!result.ok || !result.data) {
      errorMessage.value = result.message || 'Please check your connection and try again.'
      detail.value = null
      return
    }
    detail.value = result.data
  } catch {
    errorMessage.value = 'Please check your connection and try again.'
    detail.value = null
  } finally {
    loading.value = false
  }
}

async function onReauthConfirmed() {
  showReauth.value = false
  if (!props.apiBaseUrl || !props.publicBookingId) return
  try {
    const csrfToken = await ensureBookingCsrfToken(props.apiBaseUrl)
    if (!csrfToken) {
      errorMessage.value = 'Contact details could not be revealed. Confirm your password and try again.'
      return
    }
    const result = await postStaffContactAccess(
      props.apiBaseUrl,
      props.publicBookingId,
      'Staff needs customer contact for appointment coordination',
      csrfToken,
    )
    if (!result.ok || !result.data) {
      errorMessage.value = result.message || 'Contact details could not be revealed.'
      return
    }
    revealedContact.value = { email: result.data.email, phone: result.data.phone }
  } catch {
    errorMessage.value = 'Contact details could not be revealed. Confirm your password and try again.'
  }
}

onMounted(() => {
  void loadDetail()
})

watch(
  () => [props.apiBaseUrl, props.publicBookingId],
  () => {
    void loadDetail()
  },
)
</script>

<style scoped>
.detail-card {
  display: grid;
  gap: 1rem;
  padding: clamp(1rem, 3vw, 1.5rem);
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 32px;
  background: rgba(255, 253, 248, 0.86);
}

.detail-card--state {
  gap: 0.75rem;
}

.eyebrow {
  margin: 0;
  color: #8a4f34;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 900;
}

.detail-card h2 {
  margin: 0;
}

.detail-grid,
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.contact-reveal {
  display: grid;
  gap: 0.35rem;
  padding: 0.9rem 1rem;
  border-radius: 18px;
  background: rgba(55, 32, 22, 0.06);
}

.contact-reveal p {
  margin: 0;
}

.actions button,
.actions a,
.detail-card--state button {
  min-height: 2.8rem;
  display: inline-flex;
  align-items: center;
  padding: 0 1rem;
  border: 0;
  border-radius: 999px;
  color: #fffaf3;
  background: #241611;
  text-decoration: none;
  font-weight: 900;
  cursor: pointer;
}

.actions button:disabled {
  opacity: 0.6;
}

.skeleton-block {
  height: 2.8rem;
  border-radius: 16px;
  background: linear-gradient(90deg, rgba(55, 32, 22, 0.06), rgba(55, 32, 22, 0.12), rgba(55, 32, 22, 0.06));
  background-size: 200% 100%;
  animation: shimmer 1.2s linear infinite;
}

.skeleton-block--short {
  width: 60%;
}

@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}
</style>
