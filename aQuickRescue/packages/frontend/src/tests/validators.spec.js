/**
 * Validators Tests
 */

import { describe, it, expect } from 'vitest'
import {
  validateEmail,
  validatePassword,
  validatePhone,
  validateDateOfBirth,
  validateReason,
  validateLoginForm
} from '../utils/validators.js'

describe('Validators', () => {
  describe('validateEmail', () => {
    it('should validate correct email', () => {
      expect(validateEmail('user@example.com')).toBe(true)
    })

    it('should reject invalid email', () => {
      expect(validateEmail('invalid')).toBe(false)
    })
  })

  describe('validatePassword', () => {
    it('should validate strong password', () => {
      expect(validatePassword('MyPassword123!')).toBe(true)
    })

    it('should reject weak password', () => {
      expect(validatePassword('weak')).toBe(false)
    })
  })

  describe('validatePhone', () => {
    it('should validate phone number', () => {
      expect(validatePhone('+49 123 456789')).toBe(true)
    })

    it('should reject invalid phone', () => {
      expect(validatePhone('abc')).toBe(false)
    })
  })

  describe('validateDateOfBirth', () => {
    it('should validate valid DOB', () => {
      const dob = new Date(2000, 0, 1).toISOString().split('T')[0]
      expect(validateDateOfBirth(dob)).toBe(true)
    })

    it('should reject future date', () => {
      const futureDate = new Date(2099, 0, 1).toISOString().split('T')[0]
      expect(validateDateOfBirth(futureDate)).toBe(false)
    })
  })

  describe('validateReason', () => {
    it('should validate reason with minimum length', () => {
      expect(validateReason('This is a valid reason')).toBe(true)
    })

    it('should reject reason too short', () => {
      expect(validateReason('Short')).toBe(false)
    })
  })

  describe('validateLoginForm', () => {
    it('should validate correct form', () => {
      const result = validateLoginForm({
        username: 'testuser',
        password: 'TestPass123!'
      })
      expect(result.isValid).toBe(true)
      expect(Object.keys(result.errors)).toHaveLength(0)
    })

    it('should reject form with missing fields', () => {
      const result = validateLoginForm({
        username: '',
        password: ''
      })
      expect(result.isValid).toBe(false)
      expect(result.errors.username).toBeDefined()
      expect(result.errors.password).toBeDefined()
    })
  })
})

