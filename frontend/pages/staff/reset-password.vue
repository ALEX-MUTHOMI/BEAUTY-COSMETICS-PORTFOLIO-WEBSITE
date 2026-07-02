<template>
  <main class="staff-reset-page">
    <section>
      <p>Staff recovery</p>
      <h1>Choose a new staff password.</h1>
      <form>
        <label>Reset token <input autocomplete="one-time-code" /></label>
        <label>New password <input autocomplete="new-password" minlength="15" type="password" /></label>
        <button type="button">Reset password</button>
      </form>
      <NuxtLink to="/staff/login">Back to sign in</NuxtLink>
    </section>
  </main>
</template>

<script setup lang="ts">
useHead({ title: 'Reset Staff Password | AestheticOS Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>

<style scoped>
.staff-reset-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: linear-gradient(135deg, #fffaf3, #e9c6ab);
}

.staff-reset-page section {
  width: min(100%, 32rem);
  display: grid;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 28px;
  background: #fffdf8;
}

.staff-reset-page form,
.staff-reset-page label {
  display: grid;
  gap: 0.7rem;
}
</style>
