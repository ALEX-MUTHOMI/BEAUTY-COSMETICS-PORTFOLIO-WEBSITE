<template>
  <StaffPortalShell title="Booking detail" :api-base-url="apiBaseUrl">
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
        <span class="code">Code {{ detail.bookingReference || detail.publicBookingId }}</span>
        <StaffStatusChip :status="detail.bookingStatus" />
        <StaffStatusChip :status="detail.fulfillmentStatus || 'not_started'" />
        <StaffStatusChip :status="detail.paymentStatus" />
        <span v-if="detail.amount">{{ detail.currency }} {{ detail.amount }}</span>
        <span v-if="detail.assignedStaffDisplayName">Beautician {{ detail.assignedStaffDisplayName }}</span>
      </div>

      <section class="payment-panel" aria-label="Payment summary">
        <p class="eyebrow">Payment</p>
        <p v-if="paymentLoading" class="payment-panel__copy">Loading payment summary…</p>
        <p v-else-if="paymentError" class="payment-panel__copy" role="alert">{{ paymentError }}</p>
        <template v-else-if="payment">
          <div class="detail-grid">
            <StaffStatusChip :status="payment.paymentStatus" />
            <span>{{ payment.currency }} {{ payment.amount }}</span>
            <StaffStatusChip :status="receiptChipStatus(payment.receiptStatus)" />
            <span v-if="payment.paidAtEat">Paid {{ payment.paidAtEat }}</span>
            <span v-if="payment.providerReference && payment.providerReference !== 'unavailable'" class="code">
              Ref {{ payment.providerReference }}
            </span>
          </div>
          <p v-if="!receiptReady" class="payment-panel__copy">Receipt not issued yet.</p>
          <button
            v-if="showReceiptDownload"
            type="button"
            class="receipt-button"
            :disabled="!receiptReady || receiptDownloading"
            @click="openReceiptPdf"
          >
            {{ receiptDownloading ? 'Opening receipt…' : 'View receipt PDF' }}
          </button>
          <p v-else-if="receiptReady" class="payment-panel__copy">Payment confirmed — receipt download is locked.</p>
          <p v-if="receiptMessage" class="payment-panel__copy" role="status">{{ receiptMessage }}</p>
        </template>
      </section>

      <section v-if="canAssign" class="assign-panel" aria-label="Assign beautician">
        <p class="eyebrow">Beautician</p>
        <label>
          Assign
          <select v-model="assignSelection" @change="saveAssignment">
            <option :value="null">Unassigned</option>
            <option v-for="person in beauticians" :key="person.id" :value="person.id">
              {{ person.displayName }}
            </option>
          </select>
        </label>
        <p v-if="assignMessage" class="payment-panel__copy" role="status">{{ assignMessage }}</p>
      </section>

      <section v-if="canReschedule" class="assign-panel" aria-label="Reschedule visit">
        <p class="eyebrow">Reschedule</p>
        <p class="payment-panel__copy">Choose a new start time (Africa/Nairobi business hours).</p>
        <label>
          New start
          <input v-model="rescheduleStartsAt" type="datetime-local" />
        </label>
        <label>
          Note (optional)
          <input v-model.trim="rescheduleReason" type="text" maxlength="120" placeholder="Moved at client request" />
        </label>
        <button type="button" :disabled="rescheduleSaving || !rescheduleStartsAt" @click="saveReschedule">
          {{ rescheduleSaving ? 'Saving move…' : 'Confirm new time' }}
        </button>
        <p v-if="rescheduleMessage" class="payment-panel__copy" role="status">{{ rescheduleMessage }}</p>
      </section>

      <div v-if="revealedContact" class="contact-reveal" role="status">
        <p><strong>Email</strong> {{ revealedContact.email }}</p>
        <p><strong>Phone</strong> {{ revealedContact.phone }}</p>
      </div>

      <div class="actions">
        <button type="button" @click="showReauth = true">Reveal customer contact</button>
        <button
          v-if="canConfirm"
          type="button"
          :disabled="fulfillmentSaving || detail.fulfillmentStatus === 'completed'"
          @click="markCompleted"
        >
          {{
            detail.fulfillmentStatus === 'completed'
              ? 'Service completed'
              : fulfillmentSaving
                ? 'Saving…'
                : 'Mark service completed'
          }}
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
import { computed, onMounted, ref, watch } from 'vue'

import { ensureBookingCsrfToken } from '~/src/booking/bookingCsrf'
import StaffContactRevealModal from './StaffContactRevealModal.vue'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import {
  canAssignStaff,
  canConfirmAttendance,
  canDownloadReceipt,
  downloadStaffReceiptPdf,
  getAssignableBeauticians,
  getStaffBookingDetail,
  getStaffBookingPayment,
  getStaffMe,
  postStaffAssign,
  postStaffContactAccess,
  postStaffFulfillment,
  postStaffReschedule,
  type StaffBookingDetailData,
  type StaffPaymentSummary,
} from '~/src/staff/staffPortalApi'
import { isReceiptIssued, receiptChipStatus } from '~/src/staff/staffUxHelpers'

const props = withDefaults(
  defineProps<{
    apiBaseUrl?: string
    publicBookingId?: string
  }>(),
  { apiBaseUrl: '', publicBookingId: '' },
)

const showReauth = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const detail = ref<StaffBookingDetailData | null>(null)
const payment = ref<StaffPaymentSummary | null>(null)
const paymentLoading = ref(false)
const paymentError = ref('')
const receiptDownloading = ref(false)
const receiptMessage = ref('')
const revealedContact = ref<{ email: string; phone: string } | null>(null)
const permissions = ref<string[] | null>(null)
const fulfillmentSaving = ref(false)
const beauticians = ref<{ id: string; email: string; displayName: string; role: string }[]>([])
const assignSelection = ref<string | null>(null)
const assignMessage = ref('')
const rescheduleStartsAt = ref('')
const rescheduleReason = ref('')
const rescheduleSaving = ref(false)
const rescheduleMessage = ref('')

const demoDetail: StaffBookingDetailData = {
  publicBookingId: 'demo',
  bookingReference: 'demo',
  localDate: 'Today',
  time: '09:00',
  endTime: '',
  client: 'Grace M.',
  service: 'Soft glam makeup',
  bookingStatus: 'confirmed',
  fulfillmentStatus: 'not_started',
  paymentStatus: 'paid',
  receiptStatus: 'issued',
  amount: '4,500',
  currency: 'KES',
  resource: '',
}

const receiptReady = computed(() => isReceiptIssued(payment.value?.receiptStatus || detail.value?.receiptStatus))
const showReceiptDownload = computed(() => {
  if (!props.apiBaseUrl || !props.publicBookingId) return true
  return canDownloadReceipt(permissions.value)
})
const canConfirm = computed(() => {
  if (!props.apiBaseUrl || !props.publicBookingId) return true
  return canConfirmAttendance(permissions.value)
})
const canAssign = computed(() => {
  if (!props.apiBaseUrl || !props.publicBookingId) return false
  return canAssignStaff(permissions.value)
})
const canReschedule = computed(() => {
  if (!detail.value) return false
  const status = String(detail.value.bookingStatus || '').toLowerCase()
  if (!['confirmed', 'reschedule_requested'].includes(status)) return false
  if (!props.apiBaseUrl || !props.publicBookingId) return true
  return canConfirmAttendance(permissions.value)
})

if (!props.publicBookingId) {
  detail.value = demoDetail
  payment.value = {
    paymentStatus: 'paid',
    amount: '4,500',
    currency: 'KES',
    receiptStatus: 'issued',
    paidAtEat: '',
    providerReference: 'redacted',
  }
}

async function loadPermissions() {
  if (!props.apiBaseUrl) return
  const result = await getStaffMe(props.apiBaseUrl)
  if (result.ok && result.data) {
    permissions.value = result.data.permissions
  }
}

async function loadBeauticians() {
  if (!props.apiBaseUrl || !canAssign.value) return
  const result = await getAssignableBeauticians(props.apiBaseUrl)
  if (result.ok && result.data) {
    beauticians.value = result.data.beauticians
  }
}

async function loadPayment() {
  if (!props.apiBaseUrl || !props.publicBookingId) return
  paymentLoading.value = true
  paymentError.value = ''
  try {
    const result = await getStaffBookingPayment(props.apiBaseUrl, props.publicBookingId)
    if (!result.ok || !result.data) {
      paymentError.value = result.message || 'Payment summary could not load.'
      payment.value = null
      return
    }
    payment.value = result.data
  } catch {
    paymentError.value = 'Payment summary could not load.'
    payment.value = null
  } finally {
    paymentLoading.value = false
  }
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
    assignSelection.value =
      result.data.assignedStaffId == null || result.data.assignedStaffId === ''
        ? null
        : String(result.data.assignedStaffId)
    await loadPayment()
  } catch {
    errorMessage.value = 'Please check your connection and try again.'
    detail.value = null
  } finally {
    loading.value = false
  }
}

async function openReceiptPdf() {
  if (!props.apiBaseUrl || !props.publicBookingId || !receiptReady.value || !showReceiptDownload.value) return
  receiptDownloading.value = true
  receiptMessage.value = ''
  try {
    const result = await downloadStaffReceiptPdf(props.apiBaseUrl, props.publicBookingId)
    if (!result.ok) {
      receiptMessage.value = result.message || 'Receipt could not be opened.'
    }
  } catch {
    receiptMessage.value = 'Receipt could not be opened.'
  } finally {
    receiptDownloading.value = false
  }
}

async function markCompleted() {
  if (!detail.value) return
  if (!props.apiBaseUrl || !props.publicBookingId) {
    detail.value = { ...detail.value, fulfillmentStatus: 'completed' }
    return
  }
  if (!canConfirm.value) return
  fulfillmentSaving.value = true
  errorMessage.value = ''
  try {
    const csrfToken = await ensureBookingCsrfToken(props.apiBaseUrl)
    if (!csrfToken) {
      errorMessage.value = 'Could not reach the desk. Refresh and try again.'
      return
    }
    const result = await postStaffFulfillment(props.apiBaseUrl, props.publicBookingId, 'completed', csrfToken)
    if (!result.ok || !result.data) {
      errorMessage.value = result.message || 'Visit status could not be updated.'
      return
    }
    detail.value = { ...detail.value, fulfillmentStatus: result.data.fulfillmentStatus || 'completed' }
  } catch {
    errorMessage.value = 'Visit status could not be updated.'
  } finally {
    fulfillmentSaving.value = false
  }
}

async function saveReschedule() {
  if (!detail.value || !rescheduleStartsAt.value) return
  if (!props.apiBaseUrl || !props.publicBookingId) {
    rescheduleMessage.value = 'New time saved (demo).'
    return
  }
  if (!canReschedule.value) return
  rescheduleSaving.value = true
  rescheduleMessage.value = ''
  try {
    const csrfToken = await ensureBookingCsrfToken(props.apiBaseUrl)
    if (!csrfToken) {
      rescheduleMessage.value = 'Could not reach the desk. Refresh and try again.'
      return
    }
    // datetime-local has no offset; send as Africa/Nairobi (+03:00) wall time.
    const isoLocal = `${rescheduleStartsAt.value}:00+03:00`
    const result = await postStaffReschedule(
      props.apiBaseUrl,
      props.publicBookingId,
      isoLocal,
      csrfToken,
      rescheduleReason.value,
    )
    if (!result.ok || !result.data) {
      rescheduleMessage.value = result.message || 'Unable to reschedule booking.'
      return
    }
    detail.value = {
      ...detail.value,
      time: result.data.time || detail.value.time,
      bookingStatus: result.data.bookingStatus || 'confirmed',
    }
    rescheduleMessage.value = 'Visit moved successfully.'
    rescheduleReason.value = ''
  } catch {
    rescheduleMessage.value = 'Unable to reschedule booking.'
  } finally {
    rescheduleSaving.value = false
  }
}

async function saveAssignment() {
  if (!props.apiBaseUrl || !props.publicBookingId || !canAssign.value) return
  assignMessage.value = ''
  try {
    const csrfToken = await ensureBookingCsrfToken(props.apiBaseUrl)
    if (!csrfToken) {
      assignMessage.value = 'Could not reach the desk. Refresh and try again.'
      return
    }
    const result = await postStaffAssign(props.apiBaseUrl, props.publicBookingId, assignSelection.value, csrfToken)
    if (!result.ok || !result.data) {
      assignMessage.value = result.message || 'Assignment could not be updated.'
      return
    }
    if (detail.value) {
      detail.value = {
        ...detail.value,
        assignedStaffDisplayName: result.data.assignedStaffDisplayName,
        assignedStaffId: assignSelection.value,
      }
    }
    assignMessage.value = 'Beautician assignment saved.'
  } catch {
    assignMessage.value = 'Assignment could not be updated.'
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

onMounted(async () => {
  await loadPermissions()
  await loadBeauticians()
  await loadDetail()
})
watch(
  () => props.publicBookingId,
  async () => {
    await loadDetail()
  },
)
</script>

<style scoped>
.detail-card {
  display: grid;
  gap: 1rem;
  padding: 1.25rem 1.35rem;
  border-radius: 1.1rem;
  background: color-mix(in srgb, var(--staff-surface, #f7f3ee) 92%, white);
  border: 1px solid color-mix(in srgb, var(--staff-ink, #2c2420) 8%, transparent);
}

.detail-card--state {
  min-height: 10rem;
}

.eyebrow {
  margin: 0;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: color-mix(in srgb, var(--staff-ink, #2c2420) 55%, transparent);
}

.detail-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem 1rem;
  align-items: center;
}

.code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.85rem;
}

.payment-panel,
.assign-panel {
  display: grid;
  gap: 0.65rem;
  padding-top: 0.35rem;
}

.payment-panel__copy {
  margin: 0;
  color: color-mix(in srgb, var(--staff-ink, #2c2420) 70%, transparent);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.receipt-button,
.actions button,
.assign-panel select {
  font: inherit;
}

.skeleton-block {
  height: 1.1rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--staff-ink, #2c2420) 8%, transparent);
}

.skeleton-block--short {
  width: 40%;
}

.contact-reveal {
  display: grid;
  gap: 0.25rem;
}
</style>
