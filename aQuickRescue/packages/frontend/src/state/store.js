/**
 * aQuickRescue - Zustand Store (State Management)
 * Lightweight, reactive state management
 */

import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'

/**
 * Main application store
 */
export const store = create(
  subscribeWithSelector((set, get) => ({
    // Auth state
    isAuthenticated: false,
    user: null,
    token: null,
    role: null,

    // UI state
    loading: false,
    error: null,
    notification: null,

    // Patient search state
    searchResults: [],
    selectedPatient: null,

    // Emergency access state
    emergencyAccessHistory: [],
    currentEmergencyAccess: null,

    // Audit trail state
    auditTrail: [],
    auditFilter: { action: null, status: null },

    // Pagination
    pagination: {
      page: 1,
      limit: 50,
      total: 0
    },

    // Auth actions
    setAuth: (token, user) => set({
      isAuthenticated: true,
      token,
      user,
      role: user?.role
    }),

    logout: () => set({
      isAuthenticated: false,
      user: null,
      token: null,
      role: null
    }),

    // Loading actions
    setLoading: (loading) => set({ loading }),

    setError: (error) => set({ error }),

    setNotification: (notification) => set({ notification }),

    clearNotification: () => set({ notification: null }),

    // Search actions
    setSearchResults: (results) => set({ searchResults: results }),

    setSelectedPatient: (patient) => set({ selectedPatient: patient }),

    clearSearchResults: () => set({
      searchResults: [],
      selectedPatient: null
    }),

    // Emergency access actions
    addEmergencyAccess: (access) => set((state) => ({
      emergencyAccessHistory: [access, ...state.emergencyAccessHistory],
      currentEmergencyAccess: access
    })),

    setEmergencyAccessHistory: (history) => set({
      emergencyAccessHistory: history
    }),

    // Audit trail actions
    setAuditTrail: (trail) => set({ auditTrail: trail }),

    setAuditFilter: (filter) => set({ auditFilter: filter }),

    // Pagination actions
    setPagination: (page, limit, total) => set({
      pagination: { page, limit, total }
    }),

    // Helper: Get current state
    getState: () => get(),

    // Helper: Reset to initial state
    reset: () => set({
      isAuthenticated: false,
      user: null,
      token: null,
      role: null,
      loading: false,
      error: null,
      notification: null,
      searchResults: [],
      selectedPatient: null,
      emergencyAccessHistory: [],
      currentEmergencyAccess: null,
      auditTrail: [],
      auditFilter: { action: null, status: null },
      pagination: { page: 1, limit: 50, total: 0 }
    })
  }))
)

/**
 * Selectors for specific state slices (performance optimization)
 */
export const authSelectors = {
  isAuthenticated: () => store((state) => state.isAuthenticated),
  user: () => store((state) => state.user),
  role: () => store((state) => state.role),
  token: () => store((state) => state.token)
}

export const uiSelectors = {
  loading: () => store((state) => state.loading),
  error: () => store((state) => state.error),
  notification: () => store((state) => state.notification)
}

export const searchSelectors = {
  results: () => store((state) => state.searchResults),
  selectedPatient: () => store((state) => state.selectedPatient)
}

export const emergencySelectors = {
  history: () => store((state) => state.emergencyAccessHistory),
  current: () => store((state) => state.currentEmergencyAccess)
}

export const auditSelectors = {
  trail: () => store((state) => state.auditTrail),
  filter: () => store((state) => state.auditFilter)
}

