/**
 * Vitest Setup File
 */

import { vi } from 'vitest'

// Mock localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// Mock indexedDB
global.indexedDB = {
  open: vi.fn(() => ({
    onerror: null,
    onsuccess: null,
    onupgradeneeded: null
  }))
}

// Mock fetch
global.fetch = vi.fn()

// Mock navigator.geolocation
global.navigator.geolocation = {
  getCurrentPosition: vi.fn()
}

// Suppress console warnings in tests
global.console.warn = vi.fn()

