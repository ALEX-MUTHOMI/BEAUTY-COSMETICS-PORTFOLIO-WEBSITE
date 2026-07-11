import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import StaffLoginPanel from './StaffLoginPanel.vue'
import {
  buildStaffAppleLoginUrl,
  buildStaffGoogleLoginUrl,
  buildStaffLoginUrl,
  confirmStaffPasswordReset,
  requestStaffPasswordReset,
  sanitizeNextPath,
  staffPasswordLogin,
  storageContainsStaffSecrets,
} from './staffAuth'
import { createClickGate } from './botGuard'

describe('staff auth client security contract', () => {
  it('builds bounded backend URLs without exposing tokens in browser storage', async () => {
    expect(buildStaffLoginUrl('https://api.example.com/')).toBe('https://api.example.com/api/staff/auth/login/')
    expect(buildStaffGoogleLoginUrl('https://api.example.com/', '/staff/dashboard')).toBe(
      'https://api.example.com/api/staff/auth/google/start/?next=%2Fstaff%2Fdashboard',
    )
    expect(buildStaffAppleLoginUrl('https://api.example.com/', '/staff/settings/security')).toBe(
      'https://api.example.com/api/staff/auth/apple/start/?next=%2Fstaff%2Fsettings%2Fsecurity',
    )
    expect(buildStaffGoogleLoginUrl('https://api.example.com/', 'https://evil.example')).toBe(
      'https://api.example.com/api/staff/auth/google/start/?next=%2Fstaff%2Fdashboard',
    )
    expect(buildStaffGoogleLoginUrl('http://web:8000', '/staff/dashboard')).toBe(
      '/api/staff/auth/google/start/?next=%2Fstaff%2Fdashboard',
    )
    expect(buildStaffLoginUrl('http://web:8000')).toBe('/api/staff/auth/login/')
    expect(sanitizeNextPath('/staff/bookings/BK-1001')).toBe('/staff/bookings/BK-1001')
    expect(sanitizeNextPath('/customer/bookings')).toBe('/staff/dashboard')
    expect(sanitizeNextPath('//evil.example/staff/dashboard')).toBe('/staff/dashboard')
    expect(sanitizeNextPath('/staff/dashboard\r\nLocation:https://evil.example')).toBe('/staff/dashboard')

    localStorage.clear()
    sessionStorage.clear()
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
    expect(storageContainsStaffSecrets(sessionStorage)).toBe(false)
  })

  it('posts password login with cookie credentials and CSRF but returns generic failures', async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      json: vi.fn<() => Promise<unknown>>(),
    } as unknown as Response)

    const result = await staffPasswordLogin(
      'https://api.example.com',
      {
        email: ' BEAUTICIAN@EXAMPLE.COM ',
        password: 'correct horse battery staple',
        csrfToken: 'csrf-token',
      },
      fetcher,
    )

    expect(result).toEqual({ ok: false, nextPath: '', message: 'Invalid credentials.' })
    expect(fetcher).toHaveBeenCalledWith(
      'https://api.example.com/api/staff/auth/login/',
      expect.objectContaining({
        credentials: 'include',
        method: 'POST',
        headers: expect.objectContaining({ 'X-CSRFToken': 'csrf-token' }),
      }),
    )
    const firstCall = fetcher.mock.calls.at(0)
    expect(firstCall).toBeDefined()
    const requestOptions = firstCall?.[1] as RequestInit
    expect(JSON.parse(String(requestOptions.body))).toEqual({
      email: 'beautician@example.com',
      password: 'correct horse battery staple',
      turnstile_token: '',
    })
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
  })

  it('client-side click gate blocks rapid duplicate actions without being the security boundary', () => {
    const gate = createClickGate(1200)

    expect(gate.canRun('staff-login', 10_000)).toBe(true)
    expect(gate.canRun('staff-login', 10_100)).toBe(false)
    expect(gate.isRunning('staff-login')).toBe(true)
    gate.finish('staff-login')
    expect(gate.canRun('staff-login', 10_100)).toBe(false)
    expect(gate.canRun('staff-login', 11_201)).toBe(true)
  })
})

describe('staff login panel', () => {
  const logoStub = {
    StaffSheeBrand: { template: '<div class="shee-logo-stub">Shee Aesthetics</div>' },
  }

  it('renders password login, brand-first Melis desk, reset, and accessibility status surfaces', async () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
      },
      global: { stubs: logoStub },
    })

    expect(wrapper.text()).toContain('Shee Aesthetics')
    expect(wrapper.text()).toContain('Staff desk')
    expect(wrapper.text()).not.toContain('Continue with Google')
    expect(wrapper.text()).not.toContain('Continue with Apple')
    expect(wrapper.find('input[type="email"]').attributes('autocomplete')).toBe('username')
    expect(wrapper.find('input[type="password"]').attributes('autocomplete')).toBe('current-password')
    expect(wrapper.find('input[type="password"]').attributes('minlength')).toBe('15')
    expect(wrapper.text()).toContain('Forgot your staff password?')
    expect(wrapper.find('.staff-login__reset').attributes('href')).toBe('/staff/forgot-password')
  })

  it('only exposes provider start URLs when provider auth is explicitly enabled', () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
        googleEnabled: true,
        appleEnabled: true,
        nextPath: '/staff/dashboard',
      },
      global: { stubs: logoStub },
    })

    const links = wrapper.findAll('a.staff-login__provider')
    expect(links).toHaveLength(2)
    const [googleLink, appleLink] = links
    expect(googleLink?.attributes('href')).toContain('/api/staff/auth/google/start/?next=%2Fstaff%2Fdashboard')
    expect(appleLink?.attributes('href')).toContain('/api/staff/auth/apple/start/?next=%2Fstaff%2Fdashboard')
  })

  it('shows and hides password input without persisting secrets', async () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
      },
      global: { stubs: logoStub },
    })

    expect(wrapper.find('input[name="password"]').attributes('type')).toBe('password')
    await wrapper.find('button.staff-login__ghost').trigger('click')
    expect(wrapper.find('input[name="password"]').attributes('type')).toBe('text')
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
    expect(storageContainsStaffSecrets(sessionStorage)).toBe(false)
  })
})

describe('staff password reset client', () => {
  it('posts reset request and confirm with CSRF and generic messages', async () => {
    const requestFetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn<() => Promise<{ detail: string }>>().mockResolvedValue({ detail: 'ok' }),
    } as unknown as Response)
    const requestResult = await requestStaffPasswordReset(
      'https://api.example.com',
      'beautician@example.com',
      'csrf-token',
      requestFetcher,
    )
    expect(requestResult.ok).toBe(true)
    expect(requestResult.message).toContain('reset instructions')
    expect(requestFetcher).toHaveBeenCalledWith(
      'https://api.example.com/api/staff/auth/password-reset/request/',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        headers: expect.objectContaining({ 'X-CSRFToken': 'csrf-token' }),
      }),
    )

    const confirmFetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      status: 400,
      json: vi.fn<() => Promise<{ detail: string }>>().mockResolvedValue({ detail: 'raw' }),
    } as unknown as Response)
    const confirmResult = await confirmStaffPasswordReset(
      'https://api.example.com',
      'token-value',
      'Nairobi salon passphrase secure 2026!',
      'csrf-token',
      confirmFetcher,
    )
    expect(confirmResult.ok).toBe(false)
    expect(confirmResult.message).toContain('invalid or expired')
    expect(JSON.stringify(confirmResult)).not.toContain('raw')
  })
})
