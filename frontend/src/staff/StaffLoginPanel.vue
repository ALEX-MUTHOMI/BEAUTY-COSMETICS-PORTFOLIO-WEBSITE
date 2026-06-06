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
        <input
          v-model="password"
          autocomplete="current-password"
          minlength="15"
          name="password"
          required
          type="password"
        />
      </label>

      <p class="staff-login__policy">
        Use your staff password. Routine staff login does not require email OTP; recovery is only
        for forgotten passwords.
      </p>

      <p v-if="statusMessage" class="staff-login__status" role="status" aria-live="polite">
        {{ statusMessage }}
      </p>

      <button class="staff-login__primary" type="submit" :disabled="submitting">
        {{ submitting ? 'Checking access...' : 'Sign in securely' }}
      </button>

      <a class="staff-login__google" :href="googleLoginUrl" rel="nofollow">
        <span aria-hidden="true">G</span>
        Continue with Google
      </a>

      <a class="staff-login__reset" :href="passwordResetPath">
        Forgot your staff password?
      </a>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import { buildStaffGoogleLoginUrl, staffPasswordLogin } from './staffAuth'

const props = withDefaults(
  defineProps<{
    apiBaseUrl: string
    csrfToken: string
    nextPath?: string
    passwordResetPath?: string
  }>(),
  {
    nextPath: '/staff/portal',
    passwordResetPath: '/staff/password-reset',
  },
)

const emit = defineEmits<{
  signedIn: [nextPath: string]
}>()

const email = ref('')
const password = ref('')
const submitting = ref(false)
const statusMessage = ref('')

const googleLoginUrl = computed(() => buildStaffGoogleLoginUrl(props.apiBaseUrl, props.nextPath))

async function submitLogin() {
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
  }
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
  min-height: 3rem;
  border: 1px solid rgba(32, 19, 12, 0.2);
  border-radius: 16px;
  padding: 0 1rem;
  background: #fffdf9;
  color: #20130c;
  font: 1rem ui-sans-serif, system-ui, sans-serif;
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

.staff-login__primary:disabled {
  cursor: wait;
  opacity: 0.68;
}

.staff-login__google {
  border: 1px solid rgba(32, 19, 12, 0.18);
  color: #20130c;
  background: #ffffff;
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
