<template>
  <section class="staff-login" aria-labelledby="staff-login-title">
    <header class="staff-login__header">
      <a class="staff-login__logo" href="/staff/login" aria-label="Shee Aesthetics">
        <span class="staff-login__logo-mark" aria-hidden="true" />
        <span class="staff-login__logo-text">
          <span class="staff-login__logo-name">Shee</span>
          <span class="staff-login__logo-tag">Aesthetics</span>
        </span>
      </a>
    </header>

    <div class="staff-login__panel">
      <h1 id="staff-login-title">Welcome back</h1>
      <p class="staff-login__lede">Sign in to your staff desk.</p>

      <form class="staff-login__form" novalidate @submit.prevent="submitLogin">
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
          <span class="staff-login__password-row">
            <input
              v-model="password"
              autocomplete="current-password"
              minlength="15"
              name="password"
              required
              :type="showPassword ? 'text' : 'password'"
            />
            <button type="button" class="staff-login__text-btn" @click="showPassword = !showPassword">
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </span>
        </label>

        <p v-if="statusMessage" class="staff-login__status" role="status" aria-live="polite">
          {{ statusMessage }}
        </p>

        <button class="staff-login__primary" type="submit" :disabled="submitting">
          <span v-if="submitting" class="staff-login__spinner" aria-hidden="true" />
          {{ submitting ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <div class="staff-login__divider" aria-hidden="true"><span>or</span></div>

      <div class="staff-login__providers">
        <a class="staff-login__provider" :href="googleLoginUrl" rel="nofollow">
          <span class="staff-login__provider-icon staff-login__provider-icon--google" aria-hidden="true">G</span>
          Continue with Google
        </a>
        <a class="staff-login__provider" :href="appleLoginUrl" rel="nofollow">
          <span class="staff-login__provider-icon staff-login__provider-icon--apple" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
              <path
                fill="currentColor"
                d="M16.7 12.6c0-2.1 1.7-3.1 1.8-3.2-1-1.4-2.5-1.6-3-1.7-1.3-.1-2.5.8-3.1.8-.7 0-1.7-.7-2.8-.7-1.4 0-2.8.9-3.5 2.2-1.5 2.6-.4 6.4 1.1 8.5.7 1 1.6 2.1 2.7 2.1 1.1 0 1.5-.7 2.8-.7s1.7.7 2.8.7c1.2 0 1.9-1 2.6-2 .8-1.1 1.1-2.2 1.1-2.3-.1 0-2.1-.8-2.1-3.7zM14.4 6.5c.6-.7 1-1.7.9-2.7-0.9.1-1.9.6-2.5 1.3-.6.6-1.1 1.6-1 2.6 1 .1 1.9-.5 2.6-1.2z"
              />
            </svg>
          </span>
          Continue with Apple
        </a>
      </div>

      <a class="staff-login__reset" :href="passwordResetPath">Forgot password?</a>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import { createClickGate } from './botGuard'
import { buildStaffAppleLoginUrl, buildStaffGoogleLoginUrl, staffPasswordLogin } from './staffAuth'

const props = withDefaults(
  defineProps<{
    apiBaseUrl: string
    csrfToken: string
    nextPath?: string
    passwordResetPath?: string
    /** Kept for page wiring; provider buttons are always shown and hit fail-closed start URLs. */
    googleEnabled?: boolean
    appleEnabled?: boolean
  }>(),
  {
    nextPath: '/staff/dashboard',
    passwordResetPath: '/staff/forgot-password',
    googleEnabled: true,
    appleEnabled: true,
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
    statusMessage.value = 'Please wait a moment.'
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
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
  color: var(--color-ink, #27272a);
  font-family: var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(222, 150, 141, 0.22), transparent 55%),
    linear-gradient(180deg, var(--color-cream, #fcf5f5) 0%, #fff 48%, var(--color-rose-soft, #f5e8e6) 100%);
}

.staff-login__header {
  display: flex;
  align-items: center;
  padding: 1.25rem clamp(1.25rem, 4vw, 2.5rem);
}

.staff-login__logo {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  text-decoration: none;
  color: inherit;
}

.staff-login__logo-mark {
  display: block;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background-color: var(--color-rose, #de968d);
  background-image: url('/images/logo-mark.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: 30px 30px;
  box-shadow: 0 4px 14px rgba(222, 150, 141, 0.35);
  /* Invert white mark on rose disc when the PNG is dark. */
  filter: none;
}

.staff-login__logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}

.staff-login__logo-name {
  font-family: var(--font-script, 'Parisienne', cursive);
  font-size: 2.15rem;
  font-weight: 400;
}

.staff-login__logo-tag {
  margin-top: 0.1rem;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: 0.72rem;
  letter-spacing: 0.34em;
  text-transform: uppercase;
  color: var(--color-muted, #89858d);
}

.staff-login__panel {
  width: min(100% - 2rem, 26rem);
  margin: 0 auto auto;
  padding: 0 0 3rem;
  display: grid;
  gap: 1rem;
  animation: staff-login-rise 0.7s var(--ease-story, cubic-bezier(0.22, 1, 0.36, 1)) both;
}

.staff-login h1 {
  margin: 0;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: clamp(1.85rem, 5vw, 2.35rem);
  font-weight: 400;
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.staff-login__lede {
  margin: -0.35rem 0 0.35rem;
  color: var(--color-muted, #89858d);
  font-size: 1rem;
  line-height: 1.5;
}

.staff-login__form {
  display: grid;
  gap: 0.9rem;
}

.staff-login label {
  display: grid;
  gap: 0.4rem;
  font-size: 0.82rem;
  font-weight: 600;
}

.staff-login input[type='email'],
.staff-login input[type='password'],
.staff-login input[type='text'] {
  width: 100%;
  min-height: 3rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.12));
  border-radius: 0;
  padding: 0 0.95rem;
  background: #fff;
  color: inherit;
  font: 1rem/1.2 var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
}

.staff-login input:focus {
  outline: 2px solid var(--color-rose, #de968d);
  outline-offset: 1px;
}

.staff-login__password-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.5rem;
  align-items: center;
}

.staff-login__text-btn {
  min-height: 3rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.12));
  background: #fff;
  color: var(--color-ink, #27272a);
  padding: 0 0.9rem;
  cursor: pointer;
  font: 600 0.85rem/1 var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
}

.staff-login__primary,
.staff-login__provider {
  min-height: 3.1rem;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  font: 600 0.95rem/1 var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  cursor: pointer;
}

.staff-login__primary {
  border: 0;
  color: #fff;
  background: var(--color-rose, #de968d);
  transition: background 0.2s var(--ease-story, ease);
}

.staff-login__primary:hover:not(:disabled) {
  background: var(--color-rose-dark, #c97f76);
}

.staff-login__primary:disabled {
  opacity: 0.7;
  cursor: wait;
}

.staff-login__divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0.75rem;
  align-items: center;
  color: var(--color-muted, #89858d);
  font-size: 0.8rem;
}

.staff-login__divider::before,
.staff-login__divider::after {
  content: '';
  height: 1px;
  background: var(--color-line, rgba(39, 37, 42, 0.12));
}

.staff-login__providers {
  display: grid;
  gap: 0.65rem;
}

.staff-login__provider {
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.14));
  background: #fff;
  color: var(--color-ink, #27272a);
}

.staff-login__provider:hover {
  border-color: rgba(39, 37, 42, 0.28);
}

.staff-login__provider-icon {
  width: 1.55rem;
  height: 1.55rem;
  display: inline-grid;
  place-items: center;
  border-radius: 50%;
  font-size: 0.78rem;
  font-weight: 700;
}

.staff-login__provider-icon--google {
  color: #fff;
  background: #1a73e8;
}

.staff-login__provider-icon--apple {
  color: #fff;
  background: #111;
}

.staff-login__status {
  margin: 0;
  color: var(--color-muted, #89858d);
  font-size: 0.9rem;
}

.staff-login__reset {
  justify-self: center;
  margin-top: 0.25rem;
  color: var(--color-muted, #89858d);
  font-size: 0.9rem;
}

.staff-login__spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: staff-spin 0.8s linear infinite;
}

@keyframes staff-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes staff-login-rise {
  from {
    opacity: 0;
    transform: translateY(0.75rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 420px) {
  .staff-login__password-row {
    grid-template-columns: 1fr;
  }
}
</style>
