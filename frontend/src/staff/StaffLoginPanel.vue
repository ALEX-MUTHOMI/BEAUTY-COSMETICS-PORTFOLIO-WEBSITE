<template>
  <section class="staff-login" aria-labelledby="staff-login-title">
    <div class="staff-login__brand">
      <div class="staff-login__brand-top">
        <div class="staff-login__seal" aria-hidden="true">AO</div>
        <StaffThemeToggle />
      </div>
      <p class="staff-login__eyebrow">Private studio operations</p>
      <h1 id="staff-login-title">Your studio desk, ready before the first client arrives.</h1>
      <p class="staff-login__intro">
        Secure staff access for appointments, payments, reschedules, and short-lived contact
        reveal. Customer remembered-device access cannot enter this portal.
      </p>

      <div class="staff-login__preview" aria-label="Portal preview">
        <article>
          <span>09:00</span>
          <strong>Soft glam</strong>
          <small>Payment confirmed</small>
        </article>
        <article>
          <span>11:30</span>
          <strong>Full package</strong>
          <small>Awaiting payment</small>
        </article>
        <article>
          <span>Today</span>
          <strong>6 bookings</strong>
          <small>2 need attention</small>
        </article>
      </div>
    </div>

    <form class="staff-login__card" novalidate @submit.prevent="submitLogin">
      <div class="staff-login__card-head">
        <p class="staff-login__eyebrow">Beautician sign in</p>
        <h2>Open the staff portal</h2>
        <span>Protected by secure session cookies and staff-only checks.</span>
      </div>

      <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken" autocomplete="off" />

      <label>
        <span>Email</span>
        <input
          v-model.trim="email"
          autocomplete="username"
          inputmode="email"
          name="email"
          required
          type="email"
        />
      </label>

      <label>
        <span>Password</span>
        <span class="staff-login__password-control">
          <input
            v-model="password"
            autocomplete="current-password"
            minlength="15"
            name="password"
            required
            :type="showPassword ? 'text' : 'password'"
          />
          <button type="button" class="staff-login__ghost" @click="showPassword = !showPassword">
            {{ showPassword ? 'Hide' : 'Show' }}
          </button>
        </span>
      </label>

      <p class="staff-login__policy">
        Use your staff password. Rapid repeated attempts are slowed down and recovery is only for
        forgotten passwords.
      </p>

      <p v-if="statusMessage" class="staff-login__status" role="status" aria-live="polite">
        {{ statusMessage }}
      </p>

      <button class="staff-login__primary" type="submit" :disabled="submitting">
        <span v-if="submitting" class="staff-login__spinner" aria-hidden="true" />
        {{ submitting ? 'Checking access...' : 'Sign in securely' }}
      </button>

      <a
        class="staff-login__google"
        :href="googleEnabled ? googleLoginUrl : '#'"
        rel="nofollow"
        :aria-disabled="!googleEnabled"
        @click="handleProviderClick('Google', googleEnabled, $event)"
      >
        <span aria-hidden="true">G</span>
        Continue with Google
      </a>

      <a
        class="staff-login__google staff-login__apple"
        :href="appleEnabled ? appleLoginUrl : '#'"
        rel="nofollow"
        :aria-disabled="!appleEnabled"
        @click="handleProviderClick('Apple', appleEnabled, $event)"
      >
        <span aria-hidden="true">A</span>
        Continue with Apple
      </a>

      <a class="staff-login__reset" :href="passwordResetPath">
        Forgot your staff password?
      </a>

      <p class="staff-login__fineprint">
        Do not use this screen on a shared device without signing out afterwards.
      </p>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import { createClickGate } from './botGuard'
import { buildStaffAppleLoginUrl, buildStaffGoogleLoginUrl, staffPasswordLogin } from './staffAuth'
import StaffThemeToggle from './StaffThemeToggle.vue'

const props = withDefaults(
  defineProps<{
    apiBaseUrl: string
    csrfToken: string
    nextPath?: string
    passwordResetPath?: string
    googleEnabled?: boolean
    appleEnabled?: boolean
  }>(),
  {
    nextPath: '/staff/dashboard',
    passwordResetPath: '/staff/forgot-password',
    googleEnabled: false,
    appleEnabled: false,
  },
)

const emit = defineEmits<{
  signedIn: [nextPath: string]
}>()

const email = ref('')
const password = ref('')
const submitting = ref(false)
const statusMessage = ref('')
const showPassword = ref(false)
const clickGate = createClickGate(1200)

const googleLoginUrl = computed(() => buildStaffGoogleLoginUrl(props.apiBaseUrl, props.nextPath))
const appleLoginUrl = computed(() => buildStaffAppleLoginUrl(props.apiBaseUrl, props.nextPath))

async function submitLogin() {
  if (!clickGate.canRun('staff-login')) {
    statusMessage.value = 'Please wait a moment before trying again.'
    return
  }
  submitting.value = true
  statusMessage.value = ''

  try {
    const result = await staffPasswordLogin(props.apiBaseUrl, {
      email: email.value,
      password: password.value,
      csrfToken: props.csrfToken,
    })

    if (!result.ok) {
      statusMessage.value = result.message
      return
    }

    password.value = ''
    statusMessage.value = 'Signed in.'
    emit('signedIn', result.nextPath)
  } catch {
    statusMessage.value = 'Invalid credentials.'
  } finally {
    submitting.value = false
    clickGate.finish('staff-login')
  }
}

function handleProviderClick(provider: 'Google' | 'Apple', enabled: boolean, event: MouseEvent) {
  if (enabled) {
    return
  }
  event.preventDefault()
  statusMessage.value = `${provider} sign-in is not available yet.`
}
</script>

<style scoped>
.staff-login {
  --ink: #23140f;
  --muted: #6f4b3a;
  --cream: #fff8ee;
  --paper: rgba(255, 252, 247, 0.9);
  --rose: #b96550;
  --clay: #6d3426;
  --staff-text: var(--ink);
  --staff-muted: var(--muted);
  --staff-surface: #fffdf8;
  --staff-surface-muted: rgba(255, 252, 247, 0.62);
  --staff-border: rgba(35, 20, 15, 0.13);
  --staff-primary: var(--clay);
  --staff-inverse: var(--cream);
  --staff-focus: #d89c73;
  min-height: 100vh;
  display: grid;
  gap: 1.35rem;
  align-items: stretch;
  padding: 1rem;
  color: var(--ink);
  background:
    radial-gradient(circle at 18% 14%, rgba(255, 224, 185, 0.9), transparent 16rem),
    radial-gradient(circle at 94% 6%, rgba(185, 101, 80, 0.28), transparent 18rem),
    linear-gradient(160deg, #fff8ef 0%, #f3dfc8 44%, #b96550 100%);
}

:global(html[data-staff-theme='dark']) .staff-login {
  --ink: #f8efe7;
  --muted: #cdb9a9;
  --cream: #180f0c;
  --paper: rgba(35, 25, 22, 0.9);
  --rose: #d59b86;
  --clay: #e0b083;
  --staff-text: #f8efe7;
  --staff-muted: #cdb9a9;
  --staff-surface: #2a1d19;
  --staff-surface-muted: rgba(55, 39, 33, 0.78);
  --staff-border: rgba(255, 239, 226, 0.14);
  --staff-primary: #d59b86;
  --staff-inverse: #180f0c;
  --staff-focus: #e0b083;
  background:
    radial-gradient(circle at 18% 14%, rgba(152, 86, 70, 0.32), transparent 16rem),
    radial-gradient(circle at 94% 6%, rgba(224, 176, 131, 0.16), transparent 18rem),
    linear-gradient(160deg, #140d0a 0%, #231714 48%, #3b211b 100%);
}

.staff-login__brand,
.staff-login__card {
  border: 1px solid var(--staff-border);
  box-shadow: 0 28px 80px rgba(43, 22, 14, 0.16);
}

.staff-login__brand {
  position: relative;
  overflow: hidden;
  display: grid;
  align-content: end;
  gap: 1rem;
  min-height: 25rem;
  padding: clamp(1.2rem, 8vw, 3rem);
  border-radius: 34px;
  background:
    linear-gradient(140deg, rgba(35, 20, 15, 0.12), rgba(35, 20, 15, 0)),
    linear-gradient(135deg, rgba(255, 250, 243, 0.84), rgba(233, 190, 161, 0.72));
}

.staff-login__brand-top {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

.staff-login__brand::before,
.staff-login__brand::after {
  content: '';
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
}

.staff-login__brand::before {
  width: 18rem;
  height: 18rem;
  top: -7rem;
  right: -6rem;
  background: rgba(35, 20, 15, 0.08);
}

.staff-login__brand::after {
  width: 14rem;
  height: 14rem;
  bottom: -6rem;
  left: -4rem;
  background: rgba(185, 101, 80, 0.18);
}

.staff-login__seal {
  position: relative;
  z-index: 1;
  width: 3.2rem;
  height: 3.2rem;
  display: grid;
  place-items: center;
  border-radius: 1.1rem;
  color: var(--staff-inverse);
  background: var(--staff-text);
  font: 950 1rem/1 ui-sans-serif, system-ui, sans-serif;
  letter-spacing: 0.08em;
}

.staff-login__eyebrow {
  position: relative;
  z-index: 1;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--clay);
  font: 900 0.72rem ui-sans-serif, system-ui, sans-serif;
}

.staff-login h1 {
  position: relative;
  z-index: 1;
  max-width: 12ch;
  margin: 0;
  font-size: clamp(2.7rem, 12vw, 5.6rem);
  line-height: 0.86;
  letter-spacing: -0.08em;
}

.staff-login__intro {
  position: relative;
  z-index: 1;
  max-width: 48ch;
  margin: 0;
  color: var(--muted);
  font: 1rem/1.65 ui-sans-serif, system-ui, sans-serif;
}

.staff-login__preview {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 0.7rem;
}

.staff-login__preview article {
  display: grid;
  grid-template-columns: 4.5rem minmax(0, 1fr);
  gap: 0.15rem 0.8rem;
  align-items: center;
  padding: 0.85rem;
  border: 1px solid rgba(35, 20, 15, 0.1);
  border-radius: 22px;
  background: var(--staff-surface-muted);
  backdrop-filter: blur(12px);
}

.staff-login__preview span {
  grid-row: span 2;
  color: var(--clay);
  font-weight: 950;
}

.staff-login__preview strong,
.staff-login__preview small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.staff-login__preview small {
  color: var(--muted);
}

.staff-login__card {
  align-self: center;
  display: grid;
  gap: 1rem;
  padding: clamp(1.25rem, 4vw, 2rem);
  border-radius: 30px;
  background: var(--paper);
  backdrop-filter: blur(18px);
}

.staff-login__card-head {
  display: grid;
  gap: 0.35rem;
}

.staff-login__card-head h2,
.staff-login__card-head span {
  margin: 0;
}

.staff-login__card-head h2 {
  font-size: 1.8rem;
  letter-spacing: -0.04em;
}

.staff-login__card-head span {
  color: var(--muted);
  font: 0.92rem/1.45 ui-sans-serif, system-ui, sans-serif;
}

.staff-login label {
  display: grid;
  gap: 0.45rem;
  font: 900 0.82rem ui-sans-serif, system-ui, sans-serif;
}

.staff-login input {
  width: 100%;
  min-height: 3.25rem;
  border: 1px solid var(--staff-border);
  border-radius: 18px;
  padding: 0 1rem;
  background: var(--staff-surface);
  color: var(--ink);
  font: 1rem ui-sans-serif, system-ui, sans-serif;
}

.staff-login__password-control {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.5rem;
}

.staff-login__policy,
.staff-login__status,
.staff-login__reset {
  margin: 0;
  color: var(--staff-muted);
  font: 0.9rem/1.55 ui-sans-serif, system-ui, sans-serif;
}

.staff-login__primary,
.staff-login__google {
  min-height: 3.1rem;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 0.7rem;
  border-radius: 999px;
  text-decoration: none;
  font: 900 0.95rem ui-sans-serif, system-ui, sans-serif;
}

.staff-login__primary {
  border: 0;
  color: #fffaf3;
  background: linear-gradient(135deg, var(--staff-text), var(--staff-primary));
  cursor: pointer;
  box-shadow: 0 16px 34px rgba(35, 20, 15, 0.22);
}

.staff-login__ghost {
  min-width: 4.4rem;
  border: 1px solid var(--staff-border);
  border-radius: 16px;
  color: var(--staff-text);
  background: var(--staff-surface);
  cursor: pointer;
  font-weight: 900;
}

.staff-login__primary:disabled {
  cursor: wait;
  opacity: 0.68;
}

.staff-login__google {
  border: 1px solid var(--staff-border);
  color: var(--staff-text);
  background: var(--staff-surface);
}

.staff-login__google[aria-disabled='true'] {
  cursor: not-allowed;
  opacity: 0.68;
}

.staff-login__apple span {
  background: #20130c;
}

.staff-login__spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 250, 243, 0.35);
  border-top-color: #fffaf3;
  border-radius: 50%;
  animation: staff-spin 0.8s linear infinite;
}

@keyframes staff-spin {
  to {
    transform: rotate(360deg);
  }
}

.staff-login__google span {
  width: 1.55rem;
  height: 1.55rem;
  display: inline-grid;
  place-items: center;
  border-radius: 50%;
  color: #ffffff;
  background: #1a73e8;
}

.staff-login__reset {
  justify-self: center;
}

@media (min-width: 860px) {
  .staff-login {
    grid-template-columns: minmax(0, 1.12fr) minmax(360px, 440px);
    gap: clamp(2rem, 5vw, 5rem);
    align-items: center;
    padding: clamp(1.5rem, 5vw, 4rem);
  }

  .staff-login__brand {
    min-height: calc(100vh - clamp(3rem, 10vw, 8rem));
  }

  .staff-login__preview {
    max-width: 34rem;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .staff-login__preview article {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 420px) {
  .staff-login {
    padding: 0.65rem;
  }

  .staff-login__brand,
  .staff-login__card {
    border-radius: 24px;
  }

  .staff-login__password-control {
    grid-template-columns: 1fr;
  }
}
</style>
