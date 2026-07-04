<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<style>
html {
  color: var(--color-text);
  background: var(--color-bg);
  font-family: var(--font-body);
  scroll-behavior: smooth;
}

body {
  margin: 0;
}

* {
  box-sizing: border-box;
}

h1,
h2,
h3,
h4 {
  font-family: var(--font-display);
  font-weight: 500;
  color: var(--color-ink);
}

a {
  color: inherit;
}
</style>
