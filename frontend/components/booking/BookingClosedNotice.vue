<template>
  <main class="book-closed" aria-labelledby="book-closed-title">
    <div class="book-closed__inner">
      <p class="book-closed__eyebrow">Shee Aesthetics · Meru</p>
      <h1 id="book-closed-title">Online booking is paused</h1>
      <p class="book-closed__lead">
        The public booking desk is closed until launch. Existing appointments stay on file.
        Privacy requests and the staff desk remain available.
      </p>
    </div>
  </main>
</template>

<style scoped>
.book-closed {
  min-height: 55vh;
  display: grid;
  place-items: center;
  padding: 4rem 1.25rem 5rem;
}
.book-closed__inner {
  max-width: 36rem;
  text-align: center;
}
.book-closed__eyebrow {
  margin: 0 0 0.75rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font: 0.72rem/1.4 var(--font-body);
  color: var(--color-muted);
}
h1 {
  margin: 0 0 0.85rem;
  font: 2rem/1.15 var(--font-display);
  color: var(--color-ink);
}
.book-closed__lead {
  margin: 0;
  font: 1rem/1.6 var(--font-body);
  color: var(--color-muted);
}
</style>
