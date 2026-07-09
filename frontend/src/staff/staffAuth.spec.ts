import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import StaffLoginPanel from './StaffLoginPanel.vue'
import {
  buildStaffAppleLoginUrl,
  buildStaffGoogleLoginUrl,
  buildStaffLoginUrl,
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
    } as Response)

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
  it('renders password login, disabled OAuth surfaces, reset, and accessibility status surfaces', async () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
      },
    })

    expect(wrapper.find('input[type="email"]').attributes('autocomplete')).toBe('username')
    expect(wrapper.find('input[type="password"]').attributes('autocomplete')).toBe('current-password')
    expect(wrapper.find('input[type="password"]').attributes('minlength')).toBe('15')
    expect(wrapper.text()).toContain('Continue with Google')
    expect(wrapper.text()).toContain('Continue with Apple')
    expect(wrapper.find('a.staff-login__google').attributes('href')).toBe('#')
    expect(wrapper.find('a.staff-login__google').attributes('aria-disabled')).toBe('true')
    expect(wrapper.text()).toContain('Forgot your staff password?')
    expect(wrapper.find('.staff-login__reset').attributes('href')).toBe('/staff/forgot-password')

    await wrapper.find('a.staff-login__google').trigger('click')
    expect(wrapper.text()).toContain('Google sign-in is not available yet.')
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
    })

    const links = wrapper.findAll('a.staff-login__google')
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
    })

    expect(wrapper.find('input[name="password"]').attributes('type')).toBe('password')
    await wrapper.find('button.staff-login__ghost').trigger('click')
    expect(wrapper.find('input[name="password"]').attributes('type')).toBe('text')
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
    expect(storageContainsStaffSecrets(sessionStorage)).toBe(false)
  })
})
