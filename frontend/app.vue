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
  scroll-padding-top: calc(var(--header-height) + 0.75rem);
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  /* clip avoids creating a scrollport that breaks position:sticky (unlike hidden) */
  overflow-x: clip;
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
