<template>
  <section class="staff-login" aria-labelledby="staff-login-title">
    <div class="staff-login__atmosphere" aria-hidden="true" />

    <header class="staff-login__header">
      <a class="staff-login__logo" href="/staff/login" aria-label="Shee Aesthetics">
        <span class="staff-login__logo-mark" aria-hidden="true" />
        <span class="staff-login__logo-text">
          <span class="staff-login__logo-name">Shee</span>
          <span class="staff-login__logo-tag">Aesthetics</span>
        </span>
      </a>
      <StaffThemeToggle variant="icon" />
    </header>

    <div class="staff-login__panel" :class="{ 'staff-login__panel--ready': panelReady }">
      <h1 id="staff-login-title" class="staff-login__title" :key="headline">
        {{ headline }}
      </h1>

      <form
        class="staff-login__form"
        novalidate
        @submit.prevent="submitLogin"
      >
        <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken" autocomplete="off" />

        <label class="staff-login__field" :class="{ 'is-focused': focusedField === 'email' }">
          <span>Email</span>
          <input
            v-model.trim="email"
            autocomplete="username"
            inputmode="email"
            name="email"
            required
            type="email"
            @focus="focusedField = 'email'"
            @blur="focusedField = ''"
            @input="onEmailInput"
          />
        </label>

        <label class="staff-login__field" :class="{ 'is-focused': focusedField === 'password' }">
          <span>Password</span>
          <span class="staff-login__password-wrap">
            <input
              v-model="password"
              autocomplete="current-password"
              minlength="15"
              name="password"
              required
              :type="showPassword ? 'text' : 'password'"
              @focus="focusedField = 'password'"
              @blur="focusedField = ''"
            />
            <button
              type="button"
              class="staff-login__eye"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              :aria-pressed="showPassword"
              @click="showPassword = !showPassword"
            >
              <svg v-if="!showPassword" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                <path
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                  d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z"
                />
                <circle cx="12" cy="12" r="2.6" fill="none" stroke="currentColor" stroke-width="1.7" />
              </svg>
              <svg v-else viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                <path
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                  d="M3 3l18 18M10.6 10.7a2.6 2.6 0 0 0 3.7 3.7M9.4 5.6A10.4 10.4 0 0 1 12 5.2c6 0 9.5 6 9.5 6a16.6 16.6 0 0 1-3.1 3.4M6.2 6.4A16.2 16.2 0 0 0 2.5 12s3.5 6 9.5 6c1.1 0 2.1-.2 3.1-.5"
                />
              </svg>
            </button>
          </span>
        </label>

        <p
          v-if="statusMessage"
          class="staff-login__status"
          :class="{
            'staff-login__status--error': statusTone === 'error',
            'staff-login__status--ok': statusTone === 'ok',
          }"
          role="status"
          aria-live="polite"
        >
          {{ statusMessage }}
        </p>

        <button
          v-if="showRetry"
          type="button"
          class="staff-login__retry"
          :disabled="submitting || refreshingDesk"
          @click="retryDesk"
        >
          {{ refreshingDesk ? 'Checking desk…' : 'Retry' }}
        </button>

        <button class="staff-login__primary" type="submit" :disabled="submitting || refreshingDesk">
          <span v-if="submitting" class="staff-login__spinner" aria-hidden="true" />
          {{ submitting ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <div class="staff-login__divider" aria-hidden="true"><span>or</span></div>

      <div class="staff-login__providers">
        <a
          class="staff-login__provider"
          :href="googleLoginUrl"
          rel="nofollow"
          :aria-disabled="!googleReady"
          @click="onProviderClick('google', googleReady, $event)"
        >
          <span class="staff-login__provider-icon staff-login__provider-icon--google" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path
                fill="#4285F4"
                d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.4h6.4c-.3 1.5-1.1 2.7-2.4 3.6v3h3.9c2.3-2.1 3.6-5.2 3.6-8.7z"
              />
              <path
                fill="#34A853"
                d="M12 24c3.2 0 5.9-1.1 7.9-2.9l-3.9-3c-1.1.7-2.5 1.2-4 1.2-3.1 0-5.7-2.1-6.6-4.9H1.4v3.1C3.4 21.3 7.4 24 12 24z"
              />
              <path
                fill="#FBBC05"
                d="M5.4 14.4c-.2-.7-.4-1.4-.4-2.4s.1-1.7.4-2.4V6.5H1.4C.5 8.3 0 10.1 0 12s.5 3.7 1.4 5.5l4-3.1z"
              />
              <path
                fill="#EA4335"
                d="M12 4.8c1.8 0 3.3.6 4.6 1.8l3.4-3.4C17.9 1.1 15.2 0 12 0 7.4 0 3.4 2.7 1.4 6.5l4 3.1C6.3 6.8 8.9 4.8 12 4.8z"
              />
            </svg>
          </span>
          Continue with Google
        </a>
        <a
          class="staff-login__provider"
          :href="appleLoginUrl"
          rel="nofollow"
          :aria-disabled="!appleReady"
          @click="onProviderClick('apple', appleReady, $event)"
        >
          <span class="staff-login__provider-icon staff-login__provider-icon--apple" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path
                fill="currentColor"
                d="M16.365 12.24c-.03-2.3 1.88-3.4 1.97-3.46-1.08-1.57-2.75-1.79-3.34-1.81-1.42-.14-2.77.84-3.49.84-.72 0-1.84-.82-3.03-.8-1.56.02-3 0.91-3.8 2.3-1.62 2.81-.41 6.97 1.16 9.25.77 1.12 1.69 2.37 2.9 2.33 1.16-.05 1.6-.75 3.01-.75 1.4 0 1.8.75 3.03.72 1.25-.02 2.05-1.14 2.81-2.27.89-1.29 1.25-2.54 1.27-2.6-.03-.01-2.43-.93-2.49-3.75zM14.5 5.63c.63-.77 1.06-1.83.94-2.89-.91.04-2.01.61-2.66 1.37-.58.68-1.09 1.77-.95 2.81 1.01.08 2.04-.51 2.67-1.29z"
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
import { computed, onMounted, ref, watch } from 'vue'

import { createClickGate } from './botGuard'
import {
  DESK_UNAVAILABLE_ERROR,
  DESK_UNREACHABLE_ERROR,
  SESSION_REFRESH_ERROR,
  buildStaffAppleLoginUrl,
  buildStaffGoogleLoginUrl,
  fetchStaffOAuthProviders,
  staffApiHostMismatch,
  staffPasswordLogin,
} from './staffAuth'
import { readStoredGreetName, welcomeHeadline, writeStoredGreetName } from './staffGreeting'
import StaffThemeToggle from './StaffThemeToggle.vue'
import { applyStaffTheme, resolveStaffTheme } from './theme'

const props = withDefaults(
  defineProps<{
    apiBaseUrl: string
    csrfToken: string
    /** Parent finished CSRF bootstrap with no token (503/timeout/network). */
    csrfBootstrapFailed?: boolean
    nextPath?: string
    passwordResetPath?: string
    googleEnabled?: boolean
    appleEnabled?: boolean
    signInHint?: string
  }>(),
  {
    csrfBootstrapFailed: false,
    nextPath: '/staff/dashboard',
    passwordResetPath: '/staff/forgot-password',
    googleEnabled: false,
    appleEnabled: false,
    signInHint: '',
  },
)

const emit = defineEmits<{
  signedIn: [nextPath: string]
  retryDesk: []
}>()

const email = ref('')
const password = ref('')
const submitting = ref(false)
const refreshingDesk = ref(false)
const statusMessage = ref('')
const statusTone = ref<'neutral' | 'error' | 'ok'>('neutral')
const showRetry = ref(false)
const showPassword = ref(false)
const focusedField = ref('')
const panelReady = ref(false)
const storedName = ref('')
const googleReady = ref(false)
const appleReady = ref(false)
const clickGate = createClickGate(1200)

const googleLoginUrl = computed(() => buildStaffGoogleLoginUrl(props.apiBaseUrl, props.nextPath))
const appleLoginUrl = computed(() => buildStaffAppleLoginUrl(props.apiBaseUrl, props.nextPath))
const headline = computed(() => welcomeHeadline(storedName.value, email.value))

onMounted(() => {
  applyStaffTheme(resolveStaffTheme())
  storedName.value = readStoredGreetName()
  if (props.signInHint) {
    statusMessage.value = props.signInHint
    statusTone.value = 'error'
  }
  if (typeof window !== 'undefined' && staffApiHostMismatch(props.apiBaseUrl, window.location.hostname)) {
    statusTone.value = 'error'
    statusMessage.value =
      'Open the desk on the same host as the API (use 127.0.0.1 for both, not localhost mixed with 127.0.0.1).'
    showRetry.value = true
  }
  requestAnimationFrame(() => {
    panelReady.value = true
  })
  void loadProviders()
})

watch(
  () => props.csrfToken,
  (token) => {
    if (token && showRetry.value && statusTone.value === 'error') {
      showRetry.value = false
      statusTone.value = 'neutral'
      statusMessage.value = ''
    }
  },
)

watch(
  () => props.csrfBootstrapFailed,
  (failed) => {
    if (failed && !props.csrfToken) {
      markRetryableFailure(DESK_UNAVAILABLE_ERROR)
    }
  },
)

function onEmailInput() {
  // Live name in headline is derived from email; keep status clear while typing.
  if (statusTone.value === 'ok') {
    statusMessage.value = ''
    statusTone.value = 'neutral'
  }
}

async function loadProviders() {
  const providers = await fetchStaffOAuthProviders(props.apiBaseUrl)
  googleReady.value = Boolean(providers.google && props.googleEnabled)
  appleReady.value = Boolean(providers.apple && props.appleEnabled)
}

function onProviderClick(_provider: 'google' | 'apple', ready: boolean, event: MouseEvent) {
  if (ready) return
  event.preventDefault()
  statusTone.value = 'neutral'
  statusMessage.value = 'Use email for now.'
}

function markRetryableFailure(message: string) {
  statusTone.value = 'error'
  statusMessage.value = message
  showRetry.value =
    message === DESK_UNREACHABLE_ERROR ||
    message === DESK_UNAVAILABLE_ERROR ||
    message === SESSION_REFRESH_ERROR ||
    message.includes('same host as the API')
}

async function retryDesk() {
  refreshingDesk.value = true
  showRetry.value = false
  statusTone.value = 'neutral'
  statusMessage.value = ''
  try {
    emit('retryDesk')
  } finally {
    refreshingDesk.value = false
  }
}

async function submitLogin() {
  if (!props.csrfToken) {
    markRetryableFailure(DESK_UNAVAILABLE_ERROR)
    return
  }
  if (!clickGate.canRun('staff-login')) {
    statusTone.value = 'neutral'
    statusMessage.value = 'Please wait a moment.'
    return
  }
  submitting.value = true
  statusMessage.value = ''
  statusTone.value = 'neutral'
  showRetry.value = false

  try {
    const result = await staffPasswordLogin(props.apiBaseUrl, {
      email: email.value,
      password: password.value,
      csrfToken: props.csrfToken,
    })

    if (!result.ok) {
      if (result.retryable) {
        markRetryableFailure(result.message)
      } else {
        statusTone.value = 'error'
        statusMessage.value = result.message
      }
      return
    }

    writeStoredGreetName(result.displayName || email.value)
    storedName.value = readStoredGreetName()
    password.value = ''
    statusTone.value = 'ok'
    statusMessage.value = storedName.value ? `Welcome back, ${storedName.value}.` : 'Signed in.'
    emit('signedIn', result.nextPath)
  } catch {
    markRetryableFailure(DESK_UNREACHABLE_ERROR)
  } finally {
    submitting.value = false
    clickGate.finish('staff-login')
  }
}
</script>

<style scoped>
.staff-login {
  --desk-ink: var(--color-ink, #27272a);
  --desk-muted: var(--color-muted, #8a8580);
  --desk-rose: var(--color-rose, #b07a71);
  --desk-rose-deep: var(--color-rose-dark, #965f57);
  --desk-blush: var(--color-rose-soft, #e9e2e0);
  --desk-paper: var(--color-paper, #f3f2f1);
  --desk-cream: var(--color-cream, #ebe9e8);
  --desk-stone: var(--color-stone, #e4e2e1);
  --desk-parchment: var(--color-parchment, #eeedec);
  --desk-line: var(--color-line, rgba(39, 37, 42, 0.12));
  --desk-field: color-mix(in srgb, var(--desk-paper) 70%, var(--desk-cream));
  --desk-ease: var(--ease-story, cubic-bezier(0.22, 1, 0.36, 1));

  position: relative;
  isolation: isolate;
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
  color: var(--desk-ink);
  font-family: var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  background:
    radial-gradient(ellipse 55% 45% at 88% 8%, color-mix(in srgb, var(--desk-rose) 18%, transparent), transparent 70%),
    linear-gradient(168deg, var(--desk-paper) 0%, var(--desk-cream, var(--desk-paper)) 42%, var(--desk-parchment) 100%);
  overflow: hidden;
}

.staff-login__atmosphere {
  position: absolute;
  inset: -8% -4% auto;
  height: 48vh;
  z-index: -1;
  background:
    radial-gradient(ellipse 50% 60% at 82% 12%, color-mix(in srgb, var(--desk-rose) 16%, transparent), transparent 74%),
    radial-gradient(ellipse 42% 50% at 8% 36%, color-mix(in srgb, var(--desk-blush) 55%, transparent), transparent 72%);
  animation: staff-login-glow 22s var(--desk-ease) infinite alternate;
  pointer-events: none;
}

.staff-login__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.35rem clamp(1.25rem, 4vw, 2.75rem);
  animation: staff-login-rise 0.65s var(--desk-ease) both;
}

.staff-login__logo {
  display: inline-flex;
  align-items: center;
  gap: 0.9rem;
  text-decoration: none;
  color: inherit;
}

.staff-login__logo-mark {
  display: block;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  /* Brand rose mark — never inverted by dark theme. */
  background-color: #c98980;
  background-image: url('/images/logo-mark.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: 32px 32px;
  box-shadow: 0 6px 18px rgba(201, 137, 128, 0.22);
  animation: staff-login-mark 0.9s var(--desk-ease) both;
}

.staff-login__logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}

.staff-login__logo-name {
  font-family: var(--font-script, 'Parisienne', cursive);
  font-size: clamp(2.1rem, 5vw, 2.45rem);
  font-weight: 400;
}

.staff-login__logo-tag {
  margin-top: 0.12rem;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: 0.72rem;
  letter-spacing: 0.36em;
  text-transform: uppercase;
  color: var(--desk-muted);
}

.staff-login__panel {
  width: min(100% - 2rem, 26rem);
  margin: 0 auto auto;
  padding: 0 0 3.25rem;
  display: grid;
  gap: 0.9rem;
  opacity: 0;
  transform: translateY(1.1rem);
  transition:
    opacity 0.75s var(--desk-ease),
    transform 0.75s var(--desk-ease);
}

.staff-login__panel--ready {
  opacity: 1;
  transform: translateY(0);
}

.staff-login__title {
  margin: 0;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: clamp(1.9rem, 5.2vw, 2.55rem);
  font-weight: 400;
  letter-spacing: -0.02em;
  line-height: 1.12;
  animation: staff-login-rise 0.45s var(--desk-ease) both;
}

.staff-login__form {
  display: grid;
  gap: 0.95rem;
  margin-top: 0.4rem;
}

.staff-login__field {
  display: grid;
  gap: 0.4rem;
  font-size: 0.82rem;
  font-weight: 600;
  transition: transform 0.25s var(--desk-ease);
}

.staff-login__field.is-focused {
  transform: translateY(-1px);
}

.staff-login input[type='email'],
.staff-login input[type='password'],
.staff-login input[type='text'] {
  width: 100%;
  min-height: 3rem;
  border: 1px solid var(--desk-line);
  border-radius: 0.85rem;
  padding: 0 0.95rem;
  background: var(--desk-field);
  color: var(--desk-ink);
  caret-color: var(--desk-rose);
  font: 1rem/1.2 var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  transition:
    border-color 0.25s ease,
    box-shadow 0.25s ease,
    background 0.25s ease;
}

.staff-login input::placeholder {
  color: var(--desk-muted);
}

.staff-login input:focus {
  outline: 0;
  border-color: var(--desk-rose);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--desk-rose) 22%, transparent);
  background: var(--desk-paper);
}

.staff-login__password-wrap {
  position: relative;
  display: block;
}

.staff-login__password-wrap input {
  padding-right: 3rem;
}

.staff-login__eye {
  position: absolute;
  top: 50%;
  right: 0.35rem;
  transform: translateY(-50%);
  width: 2.4rem;
  height: 2.4rem;
  display: inline-grid;
  place-items: center;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--desk-muted);
  cursor: pointer;
  padding: 0;
}

.staff-login__eye:hover,
.staff-login__eye:focus-visible {
  color: var(--desk-ink);
  outline: 0;
  background: color-mix(in srgb, var(--desk-rose) 12%, transparent);
}

.staff-login__primary,
.staff-login__provider,
.staff-login__retry {
  min-height: 3.05rem;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 0.7rem;
  padding: 0 1.15rem;
  border-radius: 0.85rem;
  text-decoration: none;
  font: 600 0.95rem/1 var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  cursor: pointer;
  transition:
    transform 0.2s var(--desk-ease),
    background 0.2s var(--desk-ease),
    border-color 0.2s var(--desk-ease),
    box-shadow 0.2s var(--desk-ease),
    color 0.2s var(--desk-ease);
}

.staff-login__retry {
  width: 100%;
  margin: 0;
  border: 1px solid var(--desk-line);
  background: transparent;
  color: var(--desk-ink);
}

.staff-login__retry:hover:not(:disabled) {
  border-color: var(--desk-rose);
  color: var(--desk-rose-deep);
}

.staff-login__retry:disabled {
  opacity: 0.55;
  cursor: wait;
}

.staff-login__primary {
  border: 0;
  color: #fff;
  background: var(--desk-rose-deep, #965f57);
  box-shadow: 0 6px 16px rgba(150, 95, 87, 0.22);
  letter-spacing: 0.02em;
}

.staff-login__primary:hover:not(:disabled) {
  background: #84534c;
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(132, 83, 76, 0.28);
}

.staff-login__primary:active:not(:disabled) {
  background: #734842;
  color: #fff;
  transform: translateY(0);
  box-shadow: 0 3px 10px rgba(115, 72, 66, 0.24);
}

.staff-login__primary:focus-visible {
  outline: 0;
  box-shadow:
    0 0 0 3px rgba(176, 122, 113, 0.35),
    0 6px 16px rgba(150, 95, 87, 0.22);
}

.staff-login__primary:disabled {
  opacity: 0.62;
  cursor: wait;
  box-shadow: none;
  transform: none;
}

.staff-login__divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0.75rem;
  align-items: center;
  color: var(--desk-muted);
  font-size: 0.8rem;
}

.staff-login__divider::before,
.staff-login__divider::after {
  content: '';
  height: 1px;
  background: var(--desk-line);
}

.staff-login__providers {
  display: grid;
  gap: 0.65rem;
}

.staff-login__provider {
  border: 1px solid var(--desk-line);
  background: var(--desk-field);
  color: var(--desk-ink);
}

.staff-login__provider:hover {
  border-color: color-mix(in srgb, var(--desk-ink) 28%, transparent);
  background: var(--desk-paper);
  transform: translateY(-1px);
}

.staff-login__provider:focus-visible {
  outline: 0;
  border-color: var(--desk-rose);
  box-shadow: 0 0 0 3px rgba(201, 137, 128, 0.16);
}

.staff-login__provider[aria-disabled='true'] {
  opacity: 0.68;
  cursor: not-allowed;
}

.staff-login__provider-icon {
  width: 1.6rem;
  height: 1.6rem;
  flex-shrink: 0;
  display: inline-grid;
  place-items: center;
  border-radius: 50%;
  line-height: 1;
}

.staff-login__provider-icon--google {
  background: #fff;
  border: 1px solid rgba(39, 37, 42, 0.12);
}

.staff-login__provider-icon--apple {
  color: #111;
  background: #fff;
  border: 1px solid rgba(39, 37, 42, 0.12);
}

.staff-login__provider-icon svg {
  display: block;
}

.staff-login__status {
  margin: 0;
  color: var(--desk-muted);
  font-size: 0.9rem;
  animation: staff-login-rise 0.35s ease both;
}

.staff-login__status--error {
  color: #8a3a36;
}

.staff-login__status--ok {
  color: #3d5a45;
}

.staff-login__reset {
  justify-self: center;
  margin-top: 0.3rem;
  color: var(--desk-muted);
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.staff-login__reset:hover {
  color: var(--desk-ink);
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

@keyframes staff-login-mark {
  from {
    opacity: 0;
    transform: scale(0.92);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes staff-login-glow {
  from {
    transform: translate3d(0, 0, 0) scale(1);
    opacity: 0.85;
  }
  to {
    transform: translate3d(-1.2%, 2%, 0) scale(1.02);
    opacity: 1;
  }
}

:global(html[data-staff-theme='dark']) .staff-login {
  --desk-ink: var(--color-ink);
  --desk-muted: var(--color-muted);
  --desk-rose: var(--color-rose);
  --desk-rose-deep: var(--color-rose-dark);
  --desk-blush: var(--color-rose-soft);
  --desk-paper: var(--color-paper);
  --desk-cream: var(--color-cream);
  --desk-parchment: var(--color-parchment);
  --desk-stone: var(--color-stone);
  --desk-line: var(--color-line);
  --desk-field: var(--color-stone);
  background:
    radial-gradient(ellipse 50% 40% at 90% 0%, color-mix(in srgb, var(--color-rose) 16%, transparent), transparent 68%),
    linear-gradient(168deg, var(--color-cream) 0%, var(--color-paper) 52%, var(--color-parchment) 100%);
}

:global(html[data-staff-theme='dark']) .staff-login__atmosphere {
  background:
    radial-gradient(ellipse 48% 55% at 80% 10%, color-mix(in srgb, var(--color-rose) 14%, transparent), transparent 72%),
    radial-gradient(ellipse 36% 42% at 10% 38%, color-mix(in srgb, var(--color-rose) 6%, transparent), transparent 70%);
}

:global(html[data-staff-theme='dark']) .staff-login__provider-icon--google,
:global(html[data-staff-theme='dark']) .staff-login__provider-icon--apple {
  background: #fff;
  border-color: rgba(244, 244, 245, 0.2);
}

:global(html[data-staff-theme='dark']) .staff-login__provider-icon--apple {
  color: #111;
}

:global(html[data-staff-theme='dark']) .staff-login__status--error {
  color: #f0b4aa;
}

:global(html[data-staff-theme='dark']) .staff-login__status--ok {
  color: #a8c9b2;
}

:global(html[data-staff-theme='dark']) .staff-login .staff-login__primary {
  background: #b07a71;
  color: #fff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.45);
}

:global(html[data-staff-theme='dark']) .staff-login .staff-login__primary:hover:not(:disabled) {
  background: #c98980;
  color: #fff;
}

:global(html[data-staff-theme='dark']) .staff-login .staff-login__primary:active:not(:disabled) {
  background: #965f57;
  color: #fff;
}

@media (prefers-reduced-motion: reduce) {
  .staff-login__atmosphere,
  .staff-login__panel,
  .staff-login__header,
  .staff-login__status,
  .staff-login__field,
  .staff-login__primary,
  .staff-login__provider,
  .staff-login__logo-mark,
  .staff-login__title {
    animation: none !important;
    transition: none !important;
  }

  .staff-login__panel {
    opacity: 1;
    transform: none;
  }
}
</style>
