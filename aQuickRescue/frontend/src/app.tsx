/**
 * aQuickRescue - Emergency Health Data Mobile App
 * React Native (TypeScript) - Emergency Access Flow
 *
 * Speckit Compliance:
 * - Accessibility: WCAG 2.1 AA
 * - Performance: Startup < 3s, interactions < 100ms
 * - Security: OAuth2, encrypted storage
 * - Testing: Jest + React Native Testing Library
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  ScrollView,
  TextInput,
  SafeAreaView,
  AccessibilityInfo,
} from 'react-native';
import { useAuth } from '../hooks/useAuth';
import { PatientAPI } from '../services/api';
import * as SecureStore from 'expo-secure-store';

// ============================================================================
// 1. TYPES & INTERFACES
// ============================================================================

interface Patient {
  id: string;
  name: string;
  dob: string;
  emergency_contact?: {
    name: string;
    phone: string;
  };
}

interface PatientData {
  patient: Patient;
  allergies: Array<{ code: string; display: string; criticality: string }>;
  medications: Array<{ medication: string; dosage: string; status: string }>;
  access_timestamp: string;
  access_id: number;
}

interface SearchParams {
  first_name: string;
  last_name: string;
  date_of_birth: string;
}

// ============================================================================
// 2. AUTHENTICATION CONTEXT & HOOK
// ============================================================================

export const AuthContext = React.createContext<any>(null);

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Restore token from secure storage on app launch
  useEffect(() => {
    bootstrapAsync();
  }, []);

  const bootstrapAsync = async () => {
    try {
      const savedToken = await SecureStore.getItemAsync('access_token');
      if (savedToken) {
        setToken(savedToken);
      }
    } catch (e) {
      console.error('Failed to restore token', e);
    } finally {
      setLoading(false);
    }
  };

  const authContext = {
    user,
    token,
    loading,
    login: async (username: string, password: string) => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        });

        if (!response.ok) throw new Error('Login failed');

        const data = await response.json();

        // Store token securely
        await SecureStore.setItemAsync('access_token', data.access_token);

        setToken(data.access_token);
        setUser(data.user);

        // Speckit Compliance: Log authentication event
        console.log('[AUDIT] User login successful', { user: data.user.username });

        return true;
      } catch (error) {
        console.error('Login error:', error);
        return false;
      }
    },
    logout: async () => {
      try {
        await SecureStore.deleteItemAsync('access_token');
        setToken(null);
        setUser(null);
        console.log('[AUDIT] User logout');
      } catch (error) {
        console.error('Logout error:', error);
      }
    },
  };

  return <AuthContext.Provider value={authContext}>{children}</AuthContext.Provider>;
}

// ============================================================================
// 3. SCREEN: PATIENT SEARCH
// ============================================================================

/**
 * PatientSearchScreen
 *
 * First responder searches for patient by name and DOB
 * Speckit: Performance target < 2 seconds search response
 */
export function PatientSearchScreen({ navigation }: any) {
  const { token } = useAuth();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [dob, setDob] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  const handleSearch = useCallback(async () => {
    if (!firstName.trim() || !lastName.trim() || !dob.trim()) {
      Alert.alert('Validation', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/patients/search?first_name=${firstName}&last_name=${lastName}&date_of_birth=${dob}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      setSearchResults(data.patients || []);

      // Speckit Compliance: Audit logging
      console.log('[AUDIT] Patient search performed', {
        query: { firstName, lastName, dob },
        results: data.patients?.length || 0,
      });

      if (data.patients?.length === 0) {
        Alert.alert('No Results', 'Patient not found in system');
      }
    } catch (error) {
      console.error('Search error:', error);
      Alert.alert('Error', 'Failed to search patients');
    } finally {
      setLoading(false);
    }
  }, [firstName, lastName, dob, token]);

  const handleSelectPatient = (patient: Patient) => {
    setSelectedPatient(patient);
    AccessibilityInfo.announceForAccessibility(
      `Selected patient: ${patient.name}, DOB ${patient.dob}`
    );
  };

  const handleContinueToEmergencyAccess = () => {
    if (!selectedPatient) {
      Alert.alert('Selection Required', 'Please select a patient first');
      return;
    }

    navigation.navigate('EmergencyAccess', { patient: selectedPatient });
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Search Patient</Text>
          <Text style={styles.headerSubtitle}>
            Enter patient information to locate their health records
          </Text>
        </View>

        {/* Search Form */}
        <View style={styles.formContainer}>
          <Text style={styles.label}>First Name</Text>
          <TextInput
            style={styles.input}
            placeholder="John"
            value={firstName}
            onChangeText={setFirstName}
            editable={!loading}
            accessible={true}
            accessibilityLabel="First Name input"
          />

          <Text style={styles.label}>Last Name</Text>
          <TextInput
            style={styles.input}
            placeholder="Doe"
            value={lastName}
            onChangeText={setLastName}
            editable={!loading}
            accessible={true}
            accessibilityLabel="Last Name input"
          />

          <Text style={styles.label}>Date of Birth (YYYY-MM-DD)</Text>
          <TextInput
            style={styles.input}
            placeholder="1980-05-20"
            value={dob}
            onChangeText={setDob}
            editable={!loading}
            accessible={true}
            accessibilityLabel="Date of Birth input"
          />

          {/* Search Button */}
          <TouchableOpacity
            style={[styles.button, styles.buttonPrimary, loading && styles.buttonDisabled]}
            onPress={handleSearch}
            disabled={loading}
            accessible={true}
            accessibilityRole="button"
            accessibilityLabel="Search patient button"
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={styles.buttonText}>Search Patient</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <View style={styles.resultsContainer}>
            <Text style={styles.resultsTitle}>Search Results ({searchResults.length})</Text>

            {searchResults.map((patient) => (
              <TouchableOpacity
                key={patient.id}
                style={[
                  styles.resultCard,
                  selectedPatient?.id === patient.id && styles.resultCardSelected,
                ]}
                onPress={() => handleSelectPatient(patient)}
                accessible={true}
                accessibilityRole="button"
                accessibilityLabel={`Patient: ${patient.name}, DOB: ${patient.dob}`}
              >
                <View style={styles.resultContent}>
                  <Text style={styles.resultName}>{patient.name}</Text>
                  <Text style={styles.resultDob}>DOB: {patient.dob}</Text>
                </View>
                {selectedPatient?.id === patient.id && (
                  <View style={styles.resultCheck} />
                )}
              </TouchableOpacity>
            ))}

            {/* Continue Button */}
            <TouchableOpacity
              style={[styles.button, styles.buttonSuccess]}
              onPress={handleContinueToEmergencyAccess}
              accessible={true}
              accessibilityRole="button"
              accessibilityLabel="Continue to emergency access"
            >
              <Text style={styles.buttonText}>Continue to Emergency Access</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// 4. SCREEN: EMERGENCY ACCESS
// ============================================================================

/**
 * EmergencyAccessScreen
 *
 * Execute emergency access to patient data
 * Speckit: Automatic audit logging on access
 */
export function EmergencyAccessScreen({ route, navigation }: any) {
  const { token } = useAuth();
  const { patient } = route.params;

  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [patientData, setPatientData] = useState<PatientData | null>(null);
  const [gpsLocation, setGpsLocation] = useState<string | null>(null);

  // Get GPS location on mount (with permission)
  useEffect(() => {
    getLocationAsync();
  }, []);

  const getLocationAsync = async () => {
    try {
      // In production, use expo-location for actual GPS
      // For now, mock location
      setGpsLocation('47.3769,8.5472'); // Zurich
    } catch (error) {
      console.error('Location error:', error);
    }
  };

  const handleRequestAccess = useCallback(async () => {
    if (!reason.trim() || reason.length < 10) {
      Alert.alert('Validation', 'Please provide a detailed reason (min 10 characters)');
      return;
    }

    setLoading(true);
    try {
      const requestedData = ['Allergies', 'Medications', 'EmergencyContact'];

      const response = await fetch(
        'http://localhost:8000/api/v1/emergency-access',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_id: patient.id,
            reason,
            requested_data: requestedData,
            gps_location: gpsLocation,
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Access denied');
      }

      const data = await response.json();
      setPatientData(data);

      // Speckit Compliance: Log emergency access (automatic on server side)
      console.log('[AUDIT] Emergency access granted', {
        patient_id: patient.id,
        access_id: data.access_id,
        timestamp: data.access_timestamp,
      });

      // Show success toast
      Alert.alert('Success', 'Emergency access granted. Patient notified.');
    } catch (error) {
      console.error('Access error:', error);
      Alert.alert('Access Denied', error instanceof Error ? error.message : 'Failed to access patient data');
    } finally {
      setLoading(false);
    }
  }, [reason, patient.id, token, gpsLocation]);

  // If data retrieved, show data view instead of form
  if (patientData) {
    return <EmergencyDataView data={patientData} />;
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Emergency Access Request</Text>
          <Text style={styles.headerSubtitle}>
            Patient: {patient.name} (DOB: {patient.dob})
          </Text>
        </View>

        {/* Access Form */}
        <View style={styles.formContainer}>
          <Text style={styles.label}>Medical Emergency Reason</Text>
          <Text style={styles.labelHint}>
            Describe the medical emergency that requires access to this patient's records
          </Text>

          <TextInput
            style={[styles.input, styles.textAreaInput]}
            placeholder="e.g. Unconscious patient - checking for allergies before administering epinephrine"
            value={reason}
            onChangeText={setReason}
            multiline={true}
            numberOfLines={4}
            editable={!loading}
            accessible={true}
            accessibilityLabel="Emergency reason text input"
            accessibilityHint="Minimum 10 characters required"
          />

          <Text style={styles.characterCount}>
            {reason.length}/500 characters
          </Text>

          {/* Warning Box */}
          <View style={styles.warningBox}>
            <Text style={styles.warningTitle}>⚠️ Important Notice</Text>
            <Text style={styles.warningText}>
              This access request will be:
            </Text>
            <Text style={styles.warningText}>
              • Logged in patient's audit trail
            </Text>
            <Text style={styles.warningText}>
              • Reviewed for compliance
            </Text>
            <Text style={styles.warningText}>
              • Reported to the patient in real-time
            </Text>
          </View>

          {/* Access Button */}
          <TouchableOpacity
            style={[
              styles.button,
              styles.buttonEmergency,
              loading && styles.buttonDisabled,
            ]}
            onPress={handleRequestAccess}
            disabled={loading || reason.length < 10}
            accessible={true}
            accessibilityRole="button"
            accessibilityLabel="Request emergency access"
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={styles.buttonText}>Grant Emergency Access</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.buttonSecondary]}
            onPress={() => navigation.goBack()}
            disabled={loading}
          >
            <Text style={styles.buttonText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// 5. COMPONENT: EMERGENCY DATA VIEW
// ============================================================================

/**
 * EmergencyDataView
 *
 * Display retrieved patient health data
 * Speckit: Read-only, secure display
 */
function EmergencyDataView({ data }: { data: PatientData }) {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Patient Header */}
        <View style={[styles.header, styles.headerSuccess]}>
          <Text style={styles.headerTitle}>✓ Emergency Access Active</Text>
          <Text style={styles.headerSubtitle}>
            Patient: {data.patient.name}
          </Text>
          <Text style={styles.headerSubtitle}>
            Access ID: {data.access_id}
          </Text>
        </View>

        {/* Contact Information */}
        {data.patient.emergency_contact && (
          <View style={styles.dataSection}>
            <Text style={styles.sectionTitle}>Emergency Contact</Text>
            <View style={styles.dataCard}>
              <Text style={styles.dataLabel}>Name:</Text>
              <Text style={styles.dataValue}>{data.patient.emergency_contact.name}</Text>
              <Text style={styles.dataLabel}>Phone:</Text>
              <Text style={styles.dataValue}>{data.patient.emergency_contact.phone}</Text>
            </View>
          </View>
        )}

        {/* Allergies */}
        <View style={styles.dataSection}>
          <Text style={styles.sectionTitle}>
            🚨 Allergies ({data.allergies.length})
          </Text>
          {data.allergies.length > 0 ? (
            data.allergies.map((allergy, idx) => (
              <View
                key={idx}
                style={[
                  styles.dataCard,
                  allergy.criticality === 'high' && styles.allergyHighCriticality,
                ]}
              >
                <Text style={styles.allergyDisplayName}>{allergy.display}</Text>
                <Text style={styles.allergyInfo}>
                  Severity: {allergy.criticality.toUpperCase()}
                </Text>
              </View>
            ))
          ) : (
            <Text style={styles.emptyText}>No known allergies</Text>
          )}
        </View>

        {/* Medications */}
        <View style={styles.dataSection}>
          <Text style={styles.sectionTitle}>
            💊 Current Medications ({data.medications.length})
          </Text>
          {data.medications.length > 0 ? (
            data.medications.map((med, idx) => (
              <View key={idx} style={styles.dataCard}>
                <Text style={styles.medicationName}>{med.medication}</Text>
                <Text style={styles.medicationInfo}>
                  Dosage: {med.dosage}
                </Text>
                <Text style={styles.medicationStatus}>
                  Status: {med.status}
                </Text>
              </View>
            ))
          ) : (
            <Text style={styles.emptyText}>No active medications</Text>
          )}
        </View>

        {/* Metadata */}
        <View style={styles.metadataSection}>
          <Text style={styles.metadataLabel}>
            Access Time: {new Date(data.access_timestamp).toLocaleString()}
          </Text>
          <Text style={styles.metadataLabel}>
            This access is being logged for patient privacy protection
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// 6. SCREEN: AUDIT TRAIL (PATIENT VIEW)
// ============================================================================

/**
 * AuditTrailScreen
 *
 * Patient can view who accessed their health data
 * Speckit: Full transparency, 100% audit logging
 */
export function AuditTrailScreen() {
  const { token } = useAuth();
  const [auditEvents, setAuditEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditTrail();
  }, []);

  const fetchAuditTrail = async () => {
    try {
      const response = await fetch(
        'http://localhost:8000/api/v1/audit-trail',
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error('Failed to fetch audit trail');

      const data = await response.json();
      setAuditEvents(data);
    } catch (error) {
      console.error('Audit trail error:', error);
      Alert.alert('Error', 'Failed to load audit trail');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Privacy Center</Text>
          <Text style={styles.headerSubtitle}>
            Who has accessed your health data?
          </Text>
        </View>

        {auditEvents.length > 0 ? (
          <View>
            {auditEvents.map((event, idx) => (
              <View key={idx} style={styles.auditCard}>
                <View style={styles.auditHeader}>
                  <Text style={styles.auditTime}>
                    {new Date(event.timestamp).toLocaleString()}
                  </Text>
                  <Text style={[
                    styles.auditStatus,
                    event.status === 'SUCCESS' ? styles.statusSuccess : styles.statusDenied,
                  ]}>
                    {event.status}
                  </Text>
                </View>
                <Text style={styles.auditUser}>Accessed by: {event.user}</Text>
                <Text style={styles.auditAction}>Action: {event.action}</Text>
                <Text style={styles.auditReason}>Reason: {event.reason || 'Not specified'}</Text>
              </View>
            ))}
          </View>
        ) : (
          <Text style={styles.emptyText}>
            No access events yet. Your privacy is protected!
          </Text>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// 7. STYLES
// ============================================================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  scrollContent: {
    paddingBottom: 20,
  },
  header: {
    backgroundColor: '#007AFF',
    padding: 20,
    paddingTop: 40,
  },
  headerSuccess: {
    backgroundColor: '#34C759',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    marginBottom: 4,
  },
  formContainer: {
    padding: 16,
    marginTop: 12,
    backgroundColor: '#FFF',
    marginHorizontal: 12,
    borderRadius: 12,
    marginBottom: 12,
  },
  label: {
    fontSize:14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  labelHint: {
    fontSize: 12,
    color: '#666',
    marginBottom: 12,
    fontStyle: 'italic',
  },
  input: {
    borderWidth: 1,
    borderColor: '#DDD',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 14,
    backgroundColor: '#F9F9F9',
  },
  textAreaInput: {
    minHeight: 100,
    textAlignVertical: 'top',
  },
  characterCount: {
    fontSize: 12,
    color: '#999',
    marginBottom: 16,
  },
  button: {
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  buttonPrimary: {
    backgroundColor: '#007AFF',
  },
  buttonSuccess: {
    backgroundColor: '#34C759',
  },
  buttonEmergency: {
    backgroundColor: '#FF3B30',
  },
  buttonSecondary: {
    backgroundColor: '#CCCCCC',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  },
  resultsContainer: {
    padding: 16,
    backgroundColor: '#FFF',
    marginHorizontal: 12,
    borderRadius: 12,
    marginBottom: 12,
  },
  resultsTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  resultCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderWidth: 1,
    borderColor: '#DDD',
    borderRadius: 8,
    marginBottom: 8,
    backgroundColor: '#F9F9F9',
  },
  resultCardSelected: {
    backgroundColor: '#E3F2FD',
    borderColor: '#007AFF',
  },
  resultContent: {
    flex: 1,
  },
  resultName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  resultDob: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  resultCheck: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#007AFF',
  },
  warningBox: {
    backgroundColor: '#FFF3CD',
    borderLeftWidth: 4,
    borderLeftColor: '#FF9800',
    padding: 12,
    borderRadius: 4,
    marginBottom: 16,
  },
  warningTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FF6F00',
    marginBottom: 8,
  },
  warningText: {
    fontSize: 13,
    color: '#E65100',
    marginBottom: 4,
  },
  dataSection: {
    padding: 16,
    marginBottom: 12,
    backgroundColor: '#FFF',
    marginHorizontal: 12,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 12,
    color: '#333',
  },
  dataCard: {
    padding: 12,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  allergyHighCriticality: {
    borderLeftColor: '#FF3B30',
    backgroundColor: '#FFEBEE',
  },
  allergyDisplayName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  allergyInfo: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  medicationName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  medicationInfo: {
    fontSize: 13,
    color: '#666',
    marginTop: 4,
  },
  medicationStatus: {
    fontSize: 12,
    color: '#34C759',
    marginTop: 4,
  },
  dataLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    marginTop: 8,
  },
  dataValue: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    padding: 20,
    fontStyle: 'italic',
  },
  metadataSection: {
    padding: 12,
    backgroundColor: '#F0F0F0',
    marginHorizontal: 12,
    borderRadius: 8,
    marginBottom: 20,
  },
  metadataLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  auditCard: {
    padding: 12,
    backgroundColor: '#FFF',
    marginHorizontal: 12,
    marginBottom: 8,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  auditHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  auditTime: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
  },
  auditStatus: {
    fontSize: 12,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusSuccess: {
    backgroundColor: '#D4EDDA',
    color: '#155724',
  },
  statusDenied: {
    backgroundColor: '#F8D7DA',
    color: '#721C24',
  },
  auditUser: {
    fontSize: 13,
    color: '#333',
    marginBottom: 4,
    fontWeight: '500',
  },
  auditAction: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  auditReason: {
    fontSize: 12,
    color: '#666',
    fontStyle: 'italic',
  },
});

