<template>
  <section class="staff-login" aria-labelledby="staff-login-title">
    <div class="staff-login__copy">
      <p class="staff-login__eyebrow">Beautician Portal</p>
      <h1 id="staff-login-title">Sign in to today&apos;s bookings.</h1>
      <p>
        Protected staff access for appointments, payment visibility, and audited customer contact
        reveal. Customer remembered-device access cannot sign in here.
      </p>
    </div>

    <form class="staff-login__card" novalidate @submit.prevent="submitLogin">
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
        Use your staff password. Routine staff login does not require email OTP; recovery is only
        for forgotten passwords.
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
    </form>
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
  statusMessage.value = `${provider} sign-in is not available right now.`
}
</script>

<style scoped>
.staff-login {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 430px);
  gap: clamp(2rem, 6vw, 6rem);
  align-items: center;
  padding: clamp(1.5rem, 6vw, 5rem);
  color: #20130c;
  background:
    radial-gradient(circle at 15% 10%, rgba(240, 157, 94, 0.42), transparent 24rem),
    radial-gradient(circle at 80% 80%, rgba(89, 53, 35, 0.2), transparent 26rem),
    linear-gradient(135deg, #fff8ef 0%, #efd1b6 42%, #a6533f 100%);
}

.staff-login__copy {
  max-width: 720px;
}

.staff-login__eyebrow {
  margin: 0 0 1rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font: 800 0.78rem ui-sans-serif, system-ui, sans-serif;
}

.staff-login h1 {
  max-width: 10ch;
  margin: 0;
  font-size: clamp(3rem, 8vw, 6.6rem);
  line-height: 0.9;
}

.staff-login__copy p:last-child {
  max-width: 58ch;
  color: #563324;
  font: 1.05rem/1.7 ui-sans-serif, system-ui, sans-serif;
}

.staff-login__card {
  display: grid;
  gap: 1rem;
  padding: clamp(1.25rem, 4vw, 2rem);
  border: 1px solid rgba(32, 19, 12, 0.16);
  border-radius: 28px;
  background: rgba(255, 251, 246, 0.84);
  box-shadow: 0 30px 90px rgba(44, 24, 12, 0.22);
  backdrop-filter: blur(18px);
}

.staff-login label {
  display: grid;
  gap: 0.45rem;
  font: 800 0.82rem ui-sans-serif, system-ui, sans-serif;
}

.staff-login input {
  width: 100%;
  min-height: 3rem;
  border: 1px solid rgba(32, 19, 12, 0.2);
  border-radius: 16px;
  padding: 0 1rem;
  background: #fffdf9;
  color: #20130c;
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
  color: #684331;
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
  background: #20130c;
  cursor: pointer;
}

.staff-login__ghost {
  min-width: 4.4rem;
  border: 1px solid rgba(32, 19, 12, 0.16);
  border-radius: 16px;
  color: #20130c;
  background: #fff8ef;
  cursor: pointer;
  font-weight: 900;
}

.staff-login__primary:disabled {
  cursor: wait;
  opacity: 0.68;
}

.staff-login__google {
  border: 1px solid rgba(32, 19, 12, 0.18);
  color: #20130c;
  background: #ffffff;
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

@media (max-width: 820px) {
  .staff-login {
    grid-template-columns: 1fr;
  }

  .staff-login h1 {
    max-width: 11ch;
  }
}
</style>
