import { describe, expect, it } from 'vitest'

import { firstNameFromEmail, welcomeHeadline } from './staffGreeting'

describe('staff greeting', () => {
  it('builds a first name from an email local-part', () => {
    expect(firstNameFromEmail('amina.k@example.com')).toBe('Amina')
    expect(firstNameFromEmail('')).toBe('')
  })

  it('starts plain then personalizes from typed email before stored name', () => {
    expect(welcomeHeadline('', '')).toBe('Welcome back')
    expect(welcomeHeadline('Desk', '')).toBe('Welcome back, Desk')
    expect(welcomeHeadline('Desk', 'amina.k@example.com')).toBe('Welcome back, Amina')
  })
})
