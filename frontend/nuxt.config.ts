// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-01-01",
  srcDir: "src/",

  devtools: { enabled: true },

  modules: ["@pinia/nuxt", "@nuxtjs/i18n", "@nuxt/fonts", "@nuxt/eslint"],

  css: ["~/styles/tokens.css"],

  runtimeConfig: {
    public: {
      // TS section 5: Vue3/Nuxt3 SPA talks to the Django backend over REST/JSON.
      apiBase: "http://127.0.0.1:8000/api",
    },
  },

  fonts: {
    families: [{ name: "DM Sans", provider: "google" }],
  },

  i18n: {
    // @nuxtjs/i18n resolves restructureDir against the Nuxt rootDir, not
    // srcDir — point it explicitly at src/i18n so locale files stay under
    // frontend/src/ per TS section 3.
    restructureDir: "src/i18n",
    // DS section 1, principle 3-4 / TS section 1: RU/EN switch without losing
    // context — same URL for both languages, no locale-prefixed routes.
    strategy: "no_prefix",
    defaultLocale: "ru",
    locales: [
      { code: "ru", name: "Русский", file: "ru.json" },
      { code: "en", name: "English", file: "en.json" },
    ],
    langDir: "locales/",
    lazy: false,
  },

  app: {
    head: {
      title: "Научный журнал ВолгГТУ",
    },
  },
});
