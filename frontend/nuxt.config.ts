// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ['@nuxt/ui','@nuxtjs/google-fonts'],
  googleFonts: {
    families: {
      Roboto: true,
      'Open Sans': true
    }
  },
  colorMode: {
    preference: 'light'
  }
})
