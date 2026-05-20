# 🏥 FHIR Integration Guide - aQuickRescue

**Project**: aQuickRescue | **Date**: May 20, 2026 | **Version**: 1.0-planning

---

## Overview

This guide details the integration with **HAPI FHIR Server** (R4 Release) for comprehensive patient healthcare data access.

### FHIR Server URL
- **Public Demo**: https://hapi.fhir.org/baseR4
- **Local Development**: http://localhost:8080/fhir (if running locally)

### Authentication
- HAPI FHIR typically uses Bearer tokens or no auth for demo
- Our implementation adds OAuth2 wrapper for security

---

## Implemented FHIR Resources

### 1. 🧑 Patient Resource
**HAPI Swagger**: https://hapi.fhir.org/baseR4/swagger-ui/?page=Patient

#### Endpoints
```
GET    /api/v1/fhir/patients
       ?given=John&family=Doe&birthdate=1980-01-15

GET    /api/v1/fhir/patients/{id}

POST   /api/v1/fhir/patients
       Body: FHIR Patient resource

PUT    /api/v1/fhir/patients/{id}
       Body: FHIR Patient resource (partial update)
```

#### Key Fields
- **id**: Unique patient identifier
- **name**: Given name, family name, use (official/usual)
- **birthDate**: YYYY-MM-DD format
- **gender**: male|female|other|unknown
- **telecom**: Contact info (phone, email, etc.)
- **address**: Complete address
- **contact**: Emergency contacts
- **identifier**: MRN, SSN, etc. (system|value)

#### Search Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| `given` | `given=John` | First name search |
| `family` | `family=Doe` | Last name search |
| `birthdate` | `birthdate=1980-01-15` | Exact date of birth |
| `birthdate` | `birthdate=ge1950&birthdate=le1990` | Date range |
| `email` | `email=john@example.com` | Email search |
| `identifier` | `identifier=mrn\|12345` | MRN or other ID |
| `_count` | `_count=50` | Limit results |
| `_offset` | `_offset=0` | Pagination offset |

---

### 2. 💊 Medication & MedicationDispense Resources
**HAPI Swagger**: https://hapi.fhir.org/baseR4/swagger-ui/?page=MedicationDispense

#### Endpoints
```
GET    /api/v1/fhir/medications
       ?patient=Patient/pat-001

GET    /api/v1/fhir/medications/{id}

GET    /api/v1/fhir/medication-dispenses
       ?patient=Patient/pat-001&status=completed

GET    /api/v1/fhir/medication-dispenses/{id}
```

#### Medication Resource
```json
{
  "resourceType": "Medication",
  "id": "med-123",
  "code": {
    "coding": [{
      "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
      "code": "207106",
      "display": "Ibuprofen 200 mg"
    }],
    "text": "Ibuprofen 200mg"
  }
}
```

#### MedicationDispense Resource (Prescription Fill)
```json
{
  "resourceType": "MedicationDispense",
  "id": "md-456",
  "status": "completed",
  "medicationReference": {"reference": "Medication/med-123"},
  "subject": {"reference": "Patient/pat-001"},
  "performer": [{
    "actor": {"reference": "Practitioner/prac-789"}
  }],
  "authorizingPrescription": [{
    "reference": "MedicationRequest/mr-001"
  }],
  "quantity": {
    "value": 30,
    "unit": "tablet"
  },
  "daysSupply": {"value": 30},
  "whenPrepared": "2024-06-01",
  "whenHandedOver": "2024-06-01",
  "dosageInstruction": [{
    "text": "Take 1 tablet by mouth twice daily",
    "timing": {
      "repeat": {
        "frequency": 2,
        "period": 1,
        "periodUnit": "d"
      }
    },
    "route": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "26643006",
        "display": "Oral use"
      }]
    },
    "doseAndRate": [{
      "doseQuantity": {
        "value": 1,
        "unit": "tablet"
      }
    }]
  }]
}
```

#### Search Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| `patient` | `patient=Patient/pat-001` | Patient reference |
| `status` | `status=completed,in-progress` | completed, in-progress, on-hold, cancelled |
| `effective-time` | `effective-time=ge2024-01-01` | Dispense date range |
| `code` | `code=rxnorm\|207106` | Medication code |
| `_count` | `_count=50` | Limit results |

#### Application Notes
- Cache for **30 minutes**
- Support medication reference resolution
- Extract dosage as structured data
- Handle multiple dosage instructions
- Include frequency calculations

---

### 3. 🚨 AllergyIntolerance Resource
**HAPI Swagger**: https://hapi.fhir.org/baseR4/swagger-ui/?page=AllergyIntolerance

#### Endpoints
```
GET    /api/v1/fhir/allergies
       ?patient=Patient/pat-001

GET    /api/v1/fhir/allergies/{id}
```

#### AllergyIntolerance Resource
```json
{
  "resourceType": "AllergyIntolerance",
  "id": "allergy-001",
  "clinicalStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
      "code": "active"
    }]
  },
  "verificationStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
      "code": "confirmed"
    }]
  },
  "type": "allergy",
  "category": ["medication"],
  "criticality": "high",
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "2670000",
      "display": "Penicillin allergy (disorder)"
    }]
  },
  "patient": {"reference": "Patient/pat-001"},
  "recordedDate": "2020-01-15",
  "lastOccurrence": "2024-06-15",
  "note": [{
    "text": "Patient reports anaphylaxis on last exposure"
  }],
  "reaction": [{
    "substance": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "373270004",
        "display": "Penicillin (substance)"
      }]
    },
    "manifestation": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "39579001",
        "display": "Anaphylaxis (disorder)"
      }]
    }],
    "description": "Anaphylactic shock",
    "onset": "2000-06-01",
    "severity": "severe",
    "exposureRoute": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "26643006",
        "display": "Oral use"
      }]
    }
  }, {
    "manifestation": [{
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "271807003",
        "display": "Rash of skin (disorder)"
      }]
    }],
    "severity": "moderate"
  }]
}
```

#### Search Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| `patient` | `patient=Patient/pat-001` | Patient reference |
| `clinical-status` | `clinical-status=active` | active, inactive, resolved |
| `verification-status` | `verification-status=confirmed` | unconfirmed, confirmed, refuted |
| `criticality` | `criticality=high` | low, high, unable-to-assess |
| `category` | `category=medication` | food, medication, environment |
| `code` | `code=snomed\|2670000` | Allergen code |

#### Critical Handling
- **Always check**: `criticality` field (HIGH = emergency!)
- **Always check**: `reaction[].severity` (SEVERE = immediate risk!)
- **Index allergies**: For rapid emergency access
- **Cache**: 30 minutes
- **Audit**: Every allergy access for compliance

---

### 4. 📊 Observation Resource (Vitals & Labs)
**HAPI Swagger**: https://hapi.fhir.org/baseR4/swagger-ui/?page=Observation

#### Endpoints
```
GET    /api/v1/fhir/observations
       ?patient=Patient/pat-001
       &category=vital-signs
       &date=ge2024-06-01

GET    /api/v1/fhir/observations/{id}
```

#### Observation Categories
| Category | Examples | Cache TTL |
|----------|----------|-----------|
| `vital-signs` | BP, HR, Temp, RR, O2 Sat | 15 min |
| `laboratory` | Blood work, urinalysis | 1 hour |
| `imaging` | X-ray findings, MRI | 4 hours |
| `social-history` | Smoking, alcohol use | 24 hours |

#### Common LOINC Codes
| Code | Description | Normal Range |
|------|-------------|--------------|
| `8480-6` | Systolic BP | 90-139 mmHg |
| `8462-4` | Diastolic BP | 60-89 mmHg |
| `8867-4` | Heart rate | 60-100 bpm |
| `8310-5` | Body temperature | 36.1-37.2°C |
| `59408-5` | Oxygen saturation | 95-100% |
| `3141-9` | Body weight | varies |
| `2085-9` | Cholesterol | <200 mg/dL |
| `2345-7` | Glucose | 70-100 mg/dL |

#### Example: Blood Pressure Observation
```json
{
  "resourceType": "Observation",
  "id": "obs-10001",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/observation-category",
      "code": "vital-signs"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "85354-9",
      "display": "Blood pressure panel with all children optional"
    }],
    "text": "Blood Pressure"
  },
  "subject": {"reference": "Patient/pat-001"},
  "effectiveDateTime": "2024-06-15T10:30:00Z",
  "component": [
    {
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "8480-6",
          "display": "Systolic blood pressure"
        }]
      },
      "valueQuantity": {
        "value": 135,
        "unit": "mmHg"
      },
      "interpretation": [{
        "coding": [{
          "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
          "code": "H",
          "display": "High"
        }]
      }]
    },
    {
      "code": {
        "coding": [{
          "system": "http://loinc.org",
          "code": "8462-4",
          "display": "Diastolic blood pressure"
        }]
      },
      "valueQuantity": {
        "value": 88,
        "unit": "mmHg"
      }
    }
  ]
}
```

---

### 5. 🏥 Condition Resource (Diagnoses)
**HAPI Swagger**: https://hapi.fhir.org/baseR4/swagger-ui/?page=Condition

#### Endpoints
```
GET    /api/v1/fhir/conditions
       ?patient=Patient/pat-001
       &clinical-status=active

GET    /api/v1/fhir/conditions/{id}
```

#### Condition Resource
```json
{
  "resourceType": "Condition",
  "id": "cond-001",
  "clinicalStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
      "code": "active"
    }]
  },
  "verificationStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
      "code": "confirmed"
    }]
  },
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-category",
      "code": "problem-list-item"
    }]
  }],
  "severity": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "255604002",
      "display": "Mild"
    }]
  },
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "44054006",
      "display": "Diabetes mellitus type 2 (disorder)"
    }],
    "text": "Type 2 Diabetes"
  },
  "subject": {"reference": "Patient/pat-001"},
  "onsetDateTime": "2015-05-15",
  "abatementString": "Resolved 2024-01-15",
  "recordedDate": "2015-05-15",
  "stage": [{
    "summary": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "264907004",
        "display": "Stage 2 (qualifier value)"
      }]
    }
  }]
}
```

#### Search Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| `patient` | `patient=Patient/pat-001` | Patient reference |
| `clinical-status` | `clinical-status=active` | active, recurrence, remission, inactive |
| `verification-status` | `verification-status=confirmed` | unconfirmed, confirmed, refuted |
| `code` | `code=snomed\|44054006` | Condition code (ICD-10, SNOMED) |

---

### 6. 🏨 Procedure Resource
**HAPI Swagger**: https://hapi.fhir.org/baseR4/swagger-ui/?page=Procedure

#### Endpoints
```
GET    /api/v1/fhir/procedures
       ?patient=Patient/pat-001
       &date=ge2024-01-01

GET    /api/v1/fhir/procedures/{id}
```

#### Procedure Resource
```json
{
  "resourceType": "Procedure",
  "id": "proc-001",
  "status": "completed",
  "statusReason": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "182992009",
      "display": "Treatment completed"
    }]
  },
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "8238003",
      "display": "Appendicectomy (procedure)"
    }]
  },
  "subject": {"reference": "Patient/pat-001"},
  "performedDateTime": "2023-06-15",
  "performer": [{
    "actor": {"reference": "Practitioner/prac-123"}
  }],
  "location": {
    "reference": "Location/loc-456"
  },
  "reasonCode": [{
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "85189001",
      "display": "Acute appendicitis (disorder)"
    }]
  }],
  "outcome": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "385668004",
      "display": "Done"
    }]
  }
}
```

---

## Emergency Patient Summary Endpoint

### GET /api/v1/fhir/patient-summary/{patient_id}

Comprehensive patient overview for emergency responders (< 3 seconds).

#### Response Structure
```json
{
  "patient": {
    "id": "pat-001",
    "name": "John Doe",
    "birthDate": "1980-01-15",
    "gender": "male",
    "contact": {"phone": "+1-555-0123"}
  },
  "blood_type": "O+",
  "emergency_contact": {
    "name": "Jane Doe",
    "phone": "+1-555-0124"
  },
  "active_allergies": [
    {
      "code": "2670000",
      "display": "Penicillin allergy",
      "criticality": "high",
      "severity": "severe",
      "reactions": ["Anaphylaxis", "Rash"]
    }
  ],
  "critical_allergies": [
    {
      "code": "2670000",
      "display": "Penicillin allergy",
      "severity": "severe"
    }
  ],
  "active_medications": [
    {
      "name": "Metformin 500mg",
      "frequency": "Twice daily",
      "status": "completed"
    }
  ],
  "active_conditions": [
    {
      "code": "44054006",
      "display": "Type 2 Diabetes",
      "status": "active"
    }
  ],
  "recent_procedures": [
    {
      "code": "8238003",
      "display": "Appendicectomy",
      "date": "2023-06-15"
    }
  ],
  "vital_signs": {
    "blood_pressure_systolic": 135,
    "blood_pressure_diastolic": 88,
    "heart_rate": 72,
    "last_measured": "2024-06-15T10:30:00Z"
  },
  "recent_labs": [
    {
      "test": "Fasting Glucose",
      "value": 125,
      "unit": "mg/dL",
      "reference_range": "70-100",
      "date": "2024-06-10"
    }
  ],
  "critical_flags": [
    "SEVERE_ALLERGY_PENICILLIN",
    "DIABETES_ACTIVE",
    "BP_ELEVATED"
  ],
  "summary_generated_at": "2024-06-15T11:00:00Z",
  "summary_cached": true,
  "cache_expires_at": "2024-06-15T11:15:00Z"
}
```

#### Critical Flags
Flags that should trigger special handling:
- `SEVERE_ALLERGY_*` - High severity allergies
- `CRITICAL_VALUE_*` - Lab values outside critical range
- `BP_ELEVATED` - Systolic > 160 or Diastolic > 100
- `HEART_RATE_ABNORMAL` - HR < 40 or HR > 120
- `TEMP_ABNORMAL` - Temp < 36°C or > 38.5°C
- `O2_SAT_LOW` - SpO2 < 90%
- `DIABETES_UNCONTROLLED` - Recent glucose > 250
- `ON_ANTICOAGULANT` - Patient on blood thinners
- `PREGNANCY_ACTIVE` - For safe medication selection

---

## Caching Strategy

### Cache TTL by Resource Type

| Resource | TTL | Key Pattern | Invalidation |
|----------|-----|-------------|--------------|
| Patient | 1 hour | `fhir:patient:{id}` | On update |
| Medication | 1 hour | `fhir:medication:{id}` | On MedicationDispense change |
| MedicationDispense | 30 min | `fhir:med-disp:{patient_id}:{status}` | Daily refresh |
| AllergyIntolerance | **30 min** | `fhir:allergy:{patient_id}` | **Immediate on new** |
| Observation | 15 min (vitals) / 1h (labs) | `fhir:obs:{patient_id}:{category}` | Real-time vitals |
| Condition | 1 hour | `fhir:condition:{patient_id}:active` | On status change |
| Procedure | 4 hours | `fhir:procedure:{patient_id}` | On completion |
| Summary | **15 min** | `fhir:summary:{patient_id}` | **Immediate on allergy** |

### Cache Keys Format
```
fhir:{resource_type}:{patient_id}:{optional_filter_hash}
```

### Redis Setup
```python
# In .env
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
FHIR_CACHE_TTL_PATIENT=3600
FHIR_CACHE_TTL_ALLERGY=1800  # Critical: 30 minutes
FHIR_CACHE_TTL_MEDICATION=1800
FHIR_CACHE_TTL_OBSERVATION_VITALS=900  # 15 minutes
FHIR_CACHE_TTL_OBSERVATION_LABS=3600
FHIR_CACHE_TTL_SUMMARY=900  # Critical: 15 minutes
```

---

## Error Handling

### FHIR OperationOutcome
```json
{
  "resourceType": "OperationOutcome",
  "issue": [{
    "severity": "error|warning|information",
    "code": "invalid|security|processing|timeout|not-found|duplicate|business-rule|conflict|transient|lock-error|no-store|exception|unknown",
    "details": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
        "code": "MSG_NO_MATCH"
      }]
    },
    "diagnostics": "Patient with ID 'invalid' not found"
  }]
}
```

### HTTP Status Mapping
| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success | Use data |
| 201 | Created | Cache result |
| 400 | Bad Request | Validate parameters |
| 401 | Unauthorized | Refresh token |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Return empty/null |
| 408 | Request Timeout | Retry with backoff |
| 429 | Too Many Requests | Rate limit backoff |
| 500 | Server Error | Retry later |
| 503 | Service Unavailable | Circuit breaker |

---

## Performance Targets

### Response Time SLAs
| Operation | Target | P95 |
|-----------|--------|-----|
| Single patient search | < 1s | < 1.5s |
| Multiple searches (100) | < 2s | < 3s |
| Get patient allergies | < 1s | < 1.5s |
| Get medications | < 1s | < 1.5s |
| Emergency summary | < 3s | < 4s |
| Cached operations | < 100ms | < 200ms |

### Database Queries
- Max 6 parallel FHIR requests per summary
- Connection timeout: 5 seconds
- Read timeout: 5 seconds

---

## Audit Logging

### All FHIR operations logged:
```json
{
  "timestamp": "2024-06-15T11:00:00Z",
  "user_id": 123,
  "action": "FHIR_PATIENT_SEARCH",
  "resource_type": "Patient",
  "resource_id": "pat-001",
  "query_params": {"given": "John", "family": "Doe"},
  "result_count": 1,
  "response_time_ms": 450,
  "cache_hit": false,
  "status": "SUCCESS"
}
```

---

## Testing Strategy

### Unit Tests
- Mock FHIR server responses
- Test parameter validation
- Test error handling
- Test caching logic

### Integration Tests
- Use public HAPI FHIR demo
- Test full workflows
- Test concurrent requests
- Test cache invalidation

### Performance Tests
- Load test with 100+ patients
- Measure p50, p95, p99 latencies
- Test cache effectiveness
- Test FHIR server downtime handling

---

**Document Version**: 1.0-planning  
**Last Updated**: May 20, 2026  
**Created for aQuickRescue v0.1.0**

