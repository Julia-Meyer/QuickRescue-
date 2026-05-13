/**
 * Database Service - SQLite/IndexedDB Integration
 * Local metadata and image storage
 */

import initSqlJs from 'sql.js'

let db = null
let SQL = null

/**
 * SQLite Schema
 */
const SCHEMA = {
  metadata: `
    CREATE TABLE IF NOT EXISTS metadata (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      key TEXT UNIQUE NOT NULL,
      value TEXT NOT NULL,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `,

  patients: `
    CREATE TABLE IF NOT EXISTS patients (
      id TEXT PRIMARY KEY,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      date_of_birth TEXT,
      emergency_contact_name TEXT,
      emergency_contact_phone TEXT,
      fhir_patient_id TEXT UNIQUE,
      synced_at DATETIME,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `,

  images: `
    CREATE TABLE IF NOT EXISTS images (
      id TEXT PRIMARY KEY,
      patient_id TEXT NOT NULL,
      type TEXT NOT NULL,
      data BLOB,
      size INTEGER,
      mime_type TEXT,
      thumbnail BLOB,
      synced BOOLEAN DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (patient_id) REFERENCES patients(id)
    )
  `,

  audit_cache: `
    CREATE TABLE IF NOT EXISTS audit_cache (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      patient_id INTEGER,
      action TEXT NOT NULL,
      resource_type TEXT,
      resource_id TEXT,
      reason TEXT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      status TEXT DEFAULT 'PENDING',
      synced BOOLEAN DEFAULT 0
    )
  `,

  cache_responses: `
    CREATE TABLE IF NOT EXISTS cache_responses (
      id TEXT PRIMARY KEY,
      endpoint TEXT NOT NULL,
      response_data TEXT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      expires_at DATETIME,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `,

  indices: [
    'CREATE INDEX IF NOT EXISTS idx_patients_fhir_id ON patients(fhir_patient_id)',
    'CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_cache(timestamp)',
    'CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_responses(expires_at)',
    'CREATE INDEX IF NOT EXISTS idx_images_patient ON images(patient_id)'
  ]
}

/**
 * Initialize SQLite database
 */
export async function initializeDatabase() {
  try {
    SQL = await initSqlJs()

    // Try to load existing database from IndexedDB
    const existing = await loadFromIndexedDB()

    if (existing) {
      db = new SQL.Database(existing)
      console.log('[DB] Loaded database from IndexedDB')
    } else {
      // Create new database
      db = new SQL.Database()
      console.log('[DB] Created new SQLite database')

      // Initialize schema
      initializeSchema()
    }

    // Save to IndexedDB periodically
    setInterval(saveToIndexedDB, 60000) // Every 60 seconds

    return true
  } catch (error) {
    console.error('[DB] Initialization failed:', error)
    throw error
  }
}

/**
 * Initialize database schema
 */
function initializeSchema() {
  try {
    Object.values(SCHEMA).forEach((sql) => {
      if (Array.isArray(sql)) return
      db.run(sql)
    })

    SCHEMA.indices.forEach((sql) => {
      db.run(sql)
    })

    console.log('[DB] ✓ Schema initialized')
  } catch (error) {
    console.error('[DB] Schema initialization failed:', error)
    throw error
  }
}

/**
 * Execute raw SQL query
 */
export function query(sql, params = []) {
  try {
    const stmt = db.prepare(sql)
    stmt.bind(params)
    const result = []
    while (stmt.step()) {
      result.push(stmt.getAsObject())
    }
    stmt.free()
    return result
  } catch (error) {
    console.error('[DB] Query error:', error, sql)
    throw error
  }
}

/**
 * Execute raw SQL command
 */
export function execute(sql, params = []) {
  try {
    const stmt = db.prepare(sql)
    stmt.bind(params)
    stmt.step()
    stmt.free()
    return true
  } catch (error) {
    console.error('[DB] Execute error:', error, sql)
    throw error
  }
}

/**
 * Save metadata to database
 */
export async function saveMetadata(key, value) {
  const sql = `
    INSERT OR REPLACE INTO metadata (key, value, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
  `
  execute(sql, [key, value])
  await saveToIndexedDB()
}

/**
 * Get metadata from database
 */
export function getMetadata(key) {
  const result = query(
    'SELECT value FROM metadata WHERE key = ?',
    [key]
  )
  return result.length > 0 ? result[0].value : null
}

/**
 * Save patient locally
 */
export async function savePatient(patient) {
  const sql = `
    INSERT OR REPLACE INTO patients
    (id, first_name, last_name, date_of_birth, emergency_contact_name,
     emergency_contact_phone, fhir_patient_id, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
  `

  const params = [
    patient.id,
    patient.first_name,
    patient.last_name,
    patient.date_of_birth,
    patient.emergency_contact_name,
    patient.emergency_contact_phone,
    patient.fhir_patient_id
  ]

  execute(sql, params)
  await saveToIndexedDB()
}

/**
 * Get patient from cache
 */
export function getPatient(patientId) {
  const result = query(
    'SELECT * FROM patients WHERE id = ?',
    [patientId]
  )
  return result[0] || null
}

/**
 * Get all patients
 */
export function getAllPatients() {
  return query('SELECT * FROM patients ORDER BY updated_at DESC')
}

/**
 * Save image locally
 */
export async function saveImage(image) {
  const sql = `
    INSERT OR REPLACE INTO images
    (id, patient_id, type, data, size, mime_type, thumbnail, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
  `

  const params = [
    image.id,
    image.patient_id,
    image.type,
    image.data,
    image.size,
    image.mime_type,
    image.thumbnail
  ]

  execute(sql, params)
  await saveToIndexedDB()
}

/**
 * Get images for patient
 */
export function getPatientImages(patientId) {
  return query(
    'SELECT id, type, mime_type, size, created_at FROM images WHERE patient_id = ? ORDER BY created_at DESC',
    [patientId]
  )
}

/**
 * Save audit event locally
 */
export async function saveAuditEvent(event) {
  const sql = `
    INSERT INTO audit_cache
    (user_id, patient_id, action, resource_type, resource_id, reason, status)
    VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
  `

  const params = [
    event.user_id,
    event.patient_id,
    event.action,
    event.resource_type,
    event.resource_id,
    event.reason
  ]

  execute(sql, params)
  await saveToIndexedDB()
}

/**
 * Get pending audit events to sync
 */
export function getPendingAuditEvents() {
  return query(
    'SELECT * FROM audit_cache WHERE synced = 0 AND status = "PENDING" ORDER BY timestamp'
  )
}

/**
 * Mark audit event as synced
 */
export async function markAuditEventSynced(eventId) {
  execute('UPDATE audit_cache SET synced = 1 WHERE id = ?', [eventId])
  await saveToIndexedDB()
}

/**
 * Cache API response
 */
export async function cacheResponse(endpoint, data, ttl = 3600) {
  const expiresAt = new Date(Date.now() + ttl * 1000).toISOString()
  const sql = `
    INSERT OR REPLACE INTO cache_responses
    (id, endpoint, response_data, expires_at)
    VALUES (?, ?, ?, ?)
  `

  execute(sql, [endpoint, endpoint, JSON.stringify(data), expiresAt])
  await saveToIndexedDB()
}

/**
 * Get cached response
 */
export function getCachedResponse(endpoint) {
  const result = query(
    'SELECT response_data FROM cache_responses WHERE endpoint = ? AND expires_at > CURRENT_TIMESTAMP',
    [endpoint]
  )

  if (result.length > 0) {
    return JSON.parse(result[0].response_data)
  }
  return null
}

/**
 * Clear expired cache
 */
export async function clearExpiredCache() {
  execute('DELETE FROM cache_responses WHERE expires_at < CURRENT_TIMESTAMP')
  await saveToIndexedDB()
}

/**
 * Save database to IndexedDB
 */
async function saveToIndexedDB() {
  return new Promise((resolve, reject) => {
    try {
      const data = db.export()
      const blob = new Blob([data], { type: 'application/octet-stream' })

      const request = indexedDB.open('aQuickRescue', 1)

      request.onupgradeneeded = () => {
        request.result.createObjectStore('database')
      }

      request.onsuccess = () => {
        const database = request.result
        const transaction = database.transaction(['database'], 'readwrite')
        const store = transaction.objectStore('database')
        store.put(blob, 'sqlite_db')

        transaction.oncomplete = () => {
          database.close()
          resolve()
        }
      }

      request.onerror = () => reject(request.error)
    } catch (error) {
      reject(error)
    }
  })
}

/**
 * Load database from IndexedDB
 */
async function loadFromIndexedDB() {
  return new Promise((resolve) => {
    try {
      const request = indexedDB.open('aQuickRescue', 1)

      request.onerror = () => resolve(null)

      request.onsuccess = () => {
        const database = request.result
        const transaction = database.transaction(['database'], 'readonly')
        const store = transaction.objectStore('database')
        const getRequest = store.get('sqlite_db')

        getRequest.onsuccess = () => {
          const blob = getRequest.result
          database.close()

          if (blob) {
            blob.arrayBuffer().then((buffer) => {
              resolve(new Uint8Array(buffer))
            })
          } else {
            resolve(null)
          }
        }
      }
    } catch (error) {
      console.error('[DB] Failed to load from IndexedDB:', error)
      resolve(null)
    }
  })
}

/**
 * Export database data (for debugging/backup)
 */
export function exportDatabase() {
  return db.export()
}

/**
 * Clear all data
 */
export async function clearDatabase() {
  execute('DELETE FROM patients')
  execute('DELETE FROM images')
  execute('DELETE FROM audit_cache')
  execute('DELETE FROM cache_responses')
  execute('DELETE FROM metadata')
  await saveToIndexedDB()
}

