<template>
  <StaffPortalShell title="Settings">
    <section class="settings-grid">
      <article>
        <h2>Security</h2>
        <p>Your staff session expires automatically. Use logout when leaving a shared device.</p>
        <NuxtLink to="/staff/settings/security">Open security settings</NuxtLink>
      </article>
      <article>
        <h2>Provider sign-in</h2>
        <p>Google and Apple sign-in are not connected yet.</p>
        <button type="button" disabled>Connect later</button>
      </article>
      <article>
        <h2>Password</h2>
        <p>Use a long staff passphrase. Password recovery is available from the sign-in page.</p>
        <NuxtLink to="/staff/forgot-password">Reset password</NuxtLink>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import StaffPortalShell from './StaffPortalShell.vue'
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.settings-grid article {
  padding: 1.2rem;
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 28px;
  background: rgba(255, 253, 248, 0.84);
}

.settings-grid h2,
.settings-grid p {
  margin: 0 0 0.75rem;
}

.settings-grid a,
.settings-grid button {
  min-height: 2.7rem;
  display: inline-flex;
  align-items: center;
  border: 0;
  border-radius: 999px;
  padding: 0 1rem;
  color: #fffaf3;
  background: #241611;
  text-decoration: none;
  font-weight: 900;
}

.settings-grid button:disabled {
  opacity: 0.55;
}

@media (max-width: 860px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
