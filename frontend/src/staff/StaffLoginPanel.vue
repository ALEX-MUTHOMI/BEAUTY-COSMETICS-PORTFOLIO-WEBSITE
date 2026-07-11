<template>
  <section class="staff-login" aria-labelledby="staff-login-title">
    <div class="staff-login__stage">
      <div class="staff-login__brand staff-login__brand--enter">
        <div class="staff-login__brand-top">
          <StaffSheeBrand to="/staff/login" size="lg" />
          <StaffThemeToggle />
        </div>
        <p class="staff-login__eyebrow">Staff portal</p>
        <h1 id="staff-login-title" class="staff-login__brand-name">Shee Aesthetics</h1>
        <p class="staff-login__purpose">Staff desk</p>
      </div>

      <form class="staff-login__card staff-login__card--enter" novalidate @submit.prevent="submitLogin">
        <div class="staff-login__card-head">
          <p class="staff-login__eyebrow">Beautician sign in</p>
          <p class="staff-login__lede">Use your staff email and password. Sessions are cookie-based and staff-only.</p>
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

        <p v-if="statusMessage" class="staff-login__status" role="status" aria-live="polite">
          {{ statusMessage }}
        </p>

        <button class="staff-login__primary" type="submit" :disabled="submitting">
          <span v-if="submitting" class="staff-login__spinner" aria-hidden="true" />
          {{ submitting ? 'Checking access...' : 'Sign in' }}
        </button>

        <a
          v-if="googleEnabled"
          class="staff-login__provider"
          :href="googleLoginUrl"
          rel="nofollow"
        >
          Continue with Google
        </a>

        <a
          v-if="appleEnabled"
          class="staff-login__provider"
          :href="appleLoginUrl"
          rel="nofollow"
        >
          Continue with Apple
        </a>

        <a class="staff-login__reset" :href="passwordResetPath">Forgot your staff password?</a>

        <p class="staff-login__fineprint">
          Do not use this screen on a shared device without signing out afterwards.
        </p>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import StaffSheeBrand from './StaffSheeBrand.vue'
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
</script>

<style scoped>
.staff-login {
  --staff-ink: var(--color-ink, #27272a);
  --staff-muted: var(--color-muted, #89858d);
  --staff-cream: var(--color-cream, #fcf5f5);
  --staff-rose: var(--color-rose, #de968d);
  --staff-rose-dark: var(--color-rose-dark, #c97f76);
  --staff-rose-soft: var(--color-rose-soft, #f5e8e6);
  --staff-paper: var(--color-paper, #ffffff);
  --staff-line: var(--color-line, rgba(39, 37, 42, 0.1));
  --staff-display: var(--font-display, 'Libre Baskerville', Georgia, serif);
  --staff-body: var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: clamp(1rem, 4vw, 2.5rem);
  color: var(--staff-ink);
  font-family: var(--staff-body);
  background:
    radial-gradient(circle at 12% 18%, rgba(222, 150, 141, 0.28), transparent 22rem),
    radial-gradient(circle at 88% 8%, rgba(245, 232, 230, 0.95), transparent 18rem),
    linear-gradient(165deg, var(--staff-cream) 0%, #fff 42%, var(--staff-rose-soft) 100%);
}

:global(html[data-staff-theme='dark']) .staff-login {
  --staff-ink: #f5f0f2;
  --staff-muted: #b7b0b6;
  --staff-cream: #1a1719;
  --staff-rose: #e4a79f;
  --staff-rose-dark: #d18f86;
  --staff-rose-soft: #2a2224;
  --staff-paper: #221e21;
  --staff-line: rgba(245, 240, 242, 0.12);
  background:
    radial-gradient(circle at 12% 18%, rgba(222, 150, 141, 0.18), transparent 22rem),
    linear-gradient(165deg, #141214 0%, #1c181a 48%, #2a2224 100%);
}

.staff-login__stage {
  width: min(100%, 28rem);
  display: grid;
  gap: 1.5rem;
}

.staff-login__brand,
.staff-login__card {
  border: 1px solid var(--staff-line);
  background: color-mix(in srgb, var(--staff-paper) 92%, transparent);
  box-shadow: var(--shadow-card, 0 0 40px rgba(39, 37, 42, 0.06));
}

.staff-login__brand {
  display: grid;
  gap: 0.65rem;
  padding: clamp(1.25rem, 4vw, 2rem);
}

.staff-login__brand-top {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

.staff-login__eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--staff-rose-dark);
  font: 600 0.72rem/1.2 var(--staff-body);
}

.staff-login__brand-name {
  margin: 0;
  max-width: 12ch;
  font-family: var(--staff-display);
  font-size: clamp(2.4rem, 10vw, 3.4rem);
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.02em;
}

.staff-login__purpose {
  margin: 0;
  color: var(--staff-muted);
  font: 500 1rem/1.5 var(--staff-body);
}

.staff-login__card {
  display: grid;
  gap: 1rem;
  padding: clamp(1.25rem, 4vw, 2rem);
}

.staff-login__card-head {
  display: grid;
  gap: 0.35rem;
}

.staff-login__lede,
.staff-login__status,
.staff-login__reset,
.staff-login__fineprint {
  margin: 0;
  color: var(--staff-muted);
  font: 0.92rem/1.55 var(--staff-body);
}

.staff-login label {
  display: grid;
  gap: 0.45rem;
  font: 600 0.82rem/1.2 var(--staff-body);
}

.staff-login input {
  width: 100%;
  min-height: 3.1rem;
  border: 1px solid var(--staff-line);
  border-radius: 0;
  padding: 0 1rem;
  background: var(--staff-paper);
  color: var(--staff-ink);
  font: 1rem var(--staff-body);
}

.staff-login__password-control {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.5rem;
}

.staff-login__primary,
.staff-login__provider {
  min-height: 3rem;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 0.7rem;
  border-radius: 0;
  text-decoration: none;
  font: 600 0.78rem/1 var(--staff-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.staff-login__primary {
  border: 0;
  color: #fff;
  background: var(--staff-rose);
  cursor: pointer;
}

.staff-login__primary:hover:not(:disabled) {
  background: var(--staff-rose-dark);
}

.staff-login__primary:disabled {
  cursor: wait;
  opacity: 0.68;
}

.staff-login__ghost {
  min-width: 4.4rem;
  border: 1px solid var(--staff-line);
  border-radius: 0;
  color: var(--staff-ink);
  background: var(--staff-cream);
  cursor: pointer;
  font: 600 0.82rem var(--staff-body);
}

.staff-login__provider {
  border: 1px solid var(--staff-line);
  color: var(--staff-ink);
  background: var(--staff-cream);
}

.staff-login__spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: staff-spin 0.8s linear infinite;
}

.staff-login__reset {
  justify-self: center;
}

.staff-login__brand--enter {
  animation: staff-rise 0.7s var(--ease-story, cubic-bezier(0.22, 1, 0.36, 1)) both;
}

.staff-login__card--enter {
  animation: staff-rise 0.7s var(--ease-story, cubic-bezier(0.22, 1, 0.36, 1)) 0.12s both;
}

@keyframes staff-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes staff-rise {
  from {
    opacity: 0;
    transform: translateY(0.85rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 420px) {
  .staff-login__password-control {
    grid-template-columns: 1fr;
  }
}
</style>
