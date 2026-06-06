import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import StaffLoginPanel from './StaffLoginPanel.vue'
import {
  buildStaffGoogleLoginUrl,
  buildStaffLoginUrl,
  staffPasswordLogin,
  storageContainsStaffSecrets,
} from './staffAuth'

describe('staff auth client security contract', () => {
  it('builds bounded backend URLs without exposing tokens in browser storage', async () => {
    expect(buildStaffLoginUrl('https://api.example.com/')).toBe('https://api.example.com/api/staff/auth/login/')
    expect(buildStaffGoogleLoginUrl('https://api.example.com/', '/staff/portal')).toBe(
      'https://api.example.com/api/staff/auth/google/start/?next=%2Fstaff%2Fportal',
    )
    expect(buildStaffGoogleLoginUrl('https://api.example.com/', 'https://evil.example')).toBe(
      'https://api.example.com/api/staff/auth/google/start/?next=%2Fstaff%2Fportal',
    )
    expect(buildStaffGoogleLoginUrl('http://web:8000', '/staff/portal')).toBe(
      '/api/staff/auth/google/start/?next=%2Fstaff%2Fportal',
    )
    expect(buildStaffLoginUrl('http://web:8000')).toBe('/api/staff/auth/login/')

    localStorage.clear()
    sessionStorage.clear()
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
    expect(storageContainsStaffSecrets(sessionStorage)).toBe(false)
  })

  it('posts password login with cookie credentials and CSRF but returns generic failures', async () => {
    const fetcher = vi.fn().mockResolvedValue({
      ok: false,
      json: vi.fn(),
    })

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
})

describe('staff login panel', () => {
  it('renders password login, Google SSO, reset, and accessibility status surfaces', () => {
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
    expect(wrapper.find('a.staff-login__google').attributes('href')).toContain('/api/staff/auth/google/start/')
    expect(wrapper.text()).toContain('Forgot your staff password?')
  })
})
