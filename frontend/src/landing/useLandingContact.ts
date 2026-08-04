/**
 * Runtime landing contact — prefers Nuxt `runtimeConfig.public.whatsappE164`
 * so container/runtime env can enable WhatsApp without rebuilding module constants.
 *
 * Use this in Vue SFCs for WA / tel CTAs. Keep fail-closed when unset.
 */
import { computed } from 'vue'
import {
  LANDING_CALL_LABEL,
  LANDING_WHATSAPP_LABEL,
  landingContactFromE164,
} from './landingContent'

export function useLandingContact() {
  const config = useRuntimeConfig()
  const contact = computed(() =>
    landingContactFromE164(config.public.whatsappE164 || ''),
  )

  return {
    isLive: computed(() => contact.value.isLive),
    phoneDisplay: computed(() => contact.value.phoneDisplay),
    phoneTel: computed(() => contact.value.phoneTel),
    whatsappUrl: computed(() => contact.value.whatsappUrl),
    whatsappLabel: LANDING_WHATSAPP_LABEL,
    callLabel: LANDING_CALL_LABEL,
  }
}
