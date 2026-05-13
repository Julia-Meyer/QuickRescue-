/**
 * State Store Tests
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { store } from '../state/store.js'

describe('Store - State Management', () => {
  beforeEach(() => {
    store.getState().reset()
  })

  describe('Authentication', () => {
    it('should set auth state', () => {
      const user = { id: 1, username: 'testuser', role: 'PATIENT' }
      const token = 'test-token'

      store.getState().setAuth(token, user)

      const state = store.getState()
      expect(state.isAuthenticated).toBe(true)
      expect(state.token).toBe(token)
      expect(state.user).toEqual(user)
      expect(state.role).toBe('PATIENT')
    })

    it('should logout user', () => {
      store.getState().setAuth('token', { id: 1, username: 'user', role: 'PATIENT' })
      store.getState().logout()

      const state = store.getState()
      expect(state.isAuthenticated).toBe(false)
      expect(state.token).toBeNull()
      expect(state.user).toBeNull()
      expect(state.role).toBeNull()
    })
  })

  describe('Loading & Errors', () => {
    it('should set loading state', () => {
      store.getState().setLoading(true)
      expect(store.getState().loading).toBe(true)

      store.getState().setLoading(false)
      expect(store.getState().loading).toBe(false)
    })

    it('should set error state', () => {
      const error = 'Test error'
      store.getState().setError(error)
      expect(store.getState().error).toBe(error)
    })

    it('should set notification', () => {
      const notification = 'Test notification'
      store.getState().setNotification(notification)
      expect(store.getState().notification).toBe(notification)

      store.getState().clearNotification()
      expect(store.getState().notification).toBeNull()
    })
  })

  describe('Patient Search', () => {
    it('should set search results', () => {
      const results = [
        { id: '1', name: 'John Doe', birthDate: '1990-01-01' },
        { id: '2', name: 'Jane Smith', birthDate: '1992-05-15' }
      ]

      store.getState().setSearchResults(results)

      const state = store.getState()
      expect(state.searchResults).toEqual(results)
      expect(state.searchResults.length).toBe(2)
    })

    it('should set selected patient', () => {
      const patient = { id: '1', name: 'John Doe', birthDate: '1990-01-01' }
      store.getState().setSelectedPatient(patient)

      expect(store.getState().selectedPatient).toEqual(patient)
    })

    it('should clear search results', () => {
      store.getState().setSearchResults([{ id: '1', name: 'Test' }])
      store.getState().setSelectedPatient({ id: '1', name: 'Test' })

      store.getState().clearSearchResults()

      const state = store.getState()
      expect(state.searchResults.length).toBe(0)
      expect(state.selectedPatient).toBeNull()
    })
  })

  describe('Emergency Access', () => {
    it('should add emergency access', () => {
      const access = {
        id: 1,
        patient_id: 1,
        responder_id: 1,
        status: 'GRANTED'
      }

      store.getState().addEmergencyAccess(access)

      const state = store.getState()
      expect(state.currentEmergencyAccess).toEqual(access)
      expect(state.emergencyAccessHistory.length).toBe(1)
    })

    it('should set emergency access history', () => {
      const history = [
        { id: 1, status: 'GRANTED' },
        { id: 2, status: 'DENIED' }
      ]

      store.getState().setEmergencyAccessHistory(history)

      expect(store.getState().emergencyAccessHistory).toEqual(history)
    })
  })

  describe('Audit Trail', () => {
    it('should set audit trail', () => {
      const trail = [
        { id: 1, action: 'READ', status: 'SUCCESS' },
        { id: 2, action: 'UPDATE', status: 'SUCCESS' }
      ]

      store.getState().setAuditTrail(trail)

      expect(store.getState().auditTrail).toEqual(trail)
    })

    it('should set audit filter', () => {
      const filter = { action: 'READ', status: 'SUCCESS' }
      store.getState().setAuditFilter(filter)

      expect(store.getState().auditFilter).toEqual(filter)
    })
  })

  describe('Reset', () => {
    it('should reset all state', () => {
      store.getState().setAuth('token', { id: 1, username: 'user', role: 'PATIENT' })
      store.getState().setError('Error')
      store.getState().setSearchResults([{ id: '1', name: 'Test' }])

      store.getState().reset()

      const state = store.getState()
      expect(state.isAuthenticated).toBe(false)
      expect(state.error).toBeNull()
      expect(state.searchResults.length).toBe(0)
    })
  })
})

