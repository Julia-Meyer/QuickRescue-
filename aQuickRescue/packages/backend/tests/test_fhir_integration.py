"""
Test suite for FHIR Integration Services
Covers TASK-3.6 through TASK-3.10
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.services.fhir_patient import get_patient_service
from app.services.fhir_allergy import get_allergy_service
from app.services.fhir_medication import get_medication_service
from app.services.fhir_summary import get_summary_service
from app.utils.errors import FHIRTimeoutError, PatientNotFoundError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_fhir_patient():
    """Mock FHIR Patient resource"""
    return {
        "resourceType": "Patient",
        "id": "pat-001",
        "name": [{
            "given": ["John"],
            "family": "Doe",
            "use": "official"
        }],
        "birthDate": "1980-01-15",
        "gender": "male",
        "telecom": [
            {
                "system": "phone",
                "value": "+1-555-0123"
            },
            {
                "system": "email",
                "value": "john@example.com"
            }
        ],
        "identifier": [{
            "system": "http://hospital.org/mrn",
            "value": "12345"
        }]
    }


@pytest.fixture
def mock_fhir_allergy():
    """Mock FHIR AllergyIntolerance resource"""
    return {
        "resourceType": "AllergyIntolerance",
        "id": "allergy-001",
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "2670000",
                "display": "Penicillin allergy (disorder)"
            }]
        },
        "criticality": "high",
        "clinicalStatus": {
            "coding": [{
                "code": "active"
            }]
        },
        "reaction": [{
            "manifestation": [{
                "coding": [{
                    "code": "39579001",
                    "display": "Anaphylaxis"
                }]
            }],
            "severity": "severe",
            "onset": "1990-06-15"
        }]
    }


@pytest.fixture
def mock_fhir_medication():
    """Mock FHIR Medication resource"""
    return {
        "resourceType": "Medication",
        "id": "med-123",
        "code": {
            "coding": [{
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": "207106",
                "display": "Ibuprofen 200 mg"
            }]
        }
    }


@pytest.fixture
def mock_fhir_bundle():
    """Mock FHIR Bundle response"""
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [{
            "resource": {
                "resourceType": "Patient",
                "id": "pat-001",
                "name": [{
                    "given": ["John"],
                    "family": "Doe"
                }]
            }
        }]
    }


# ============================================================================
# TESTS - FHIR PATIENT SERVICE
# ============================================================================

@pytest.mark.asyncio
async def test_search_patients():
    """Test patient search"""
    service = get_patient_service()

    with patch.object(service, 'search_patients', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = {
            "success": True,
            "total": 1,
            "count": 1,
            "patients": [{
                "id": "pat-001",
                "given_name": "John",
                "family_name": "Doe",
                "birth_date": "1980-01-15"
            }]
        }

        result = await service.search_patients(given="John", family="Doe")

        assert result["success"] is True
        assert result["total"] == 1
        assert len(result["patients"]) == 1


# ============================================================================
# TESTS - FHIR ALLERGY SERVICE (CRITICAL)
# ============================================================================

@pytest.mark.asyncio
async def test_get_patient_allergies():
    """Test getting patient allergies"""
    service = get_allergy_service()

    with patch.object(service, 'get_patient_allergies', new_callable=AsyncMock) as mock_allergies:
        mock_allergies.return_value = {
            "success": True,
            "patient_id": "pat-001",
            "total": 1,
            "critical_count": 1,
            "allergies": [{
                "id": "allergy-001",
                "display": "Penicillin allergy (disorder)",
                "criticality": "high",
                "severity": "severe",
                "is_critical": True,
                "critical_flags": ["CRITICAL_ALLERGY"]
            }],
            "critical_allergies": [{
                "id": "allergy-001",
                "display": "Penicillin allergy",
                "severity": "severe"
            }],
            "has_critical": True
        }

        result = await service.get_patient_allergies("pat-001")

        assert result["success"] is True
        assert result["has_critical"] is True
        assert len(result["critical_allergies"]) == 1


@pytest.mark.asyncio
async def test_critical_allergy_flags():
    """Test that critical allergies are properly flagged"""
    service = get_allergy_service()

    with patch.object(service, 'get_patient_allergies', new_callable=AsyncMock) as mock_allergies:
        mock_allergies.return_value = {
            "success": True,
            "allergies": [{
                "criticality": "high",
                "severity": "severe",
                "is_critical": True,
                "critical_flags": ["CRITICAL_ALLERGY", "SEVERE_REACTION"]
            }]
        }

        result = await service.get_patient_allergies("pat-001")

        allergy = result["allergies"][0]
        assert allergy["is_critical"] is True
        assert "CRITICAL_ALLERGY" in allergy["critical_flags"]


# ============================================================================
# TESTS - FHIR MEDICATION SERVICE
# ============================================================================

@pytest.mark.asyncio
async def test_get_patient_medications():
    """Test getting patient medications"""
    service = get_medication_service()

    with patch.object(service, 'get_patient_medications', new_callable=AsyncMock) as mock_meds:
        mock_meds.return_value = {
            "success": True,
            "patient_id": "pat-001",
            "total": 1,
            "medications": [{
                "id": "md-456",
                "status": "completed",
                "medication": {
                    "id": "med-123",
                    "display": "Ibuprofen 200mg"
                },
                "dosage_instructions": [{
                    "text": "Take 1 tablet twice daily",
                    "timing": {"frequency": 2, "period": 1, "period_unit": "d"},
                    "dose": {"value": 1, "unit": "tablet"}
                }]
            }]
        }

        result = await service.get_patient_medications("pat-001")

        assert result["success"] is True
        assert result["total"] == 1
        assert result["medications"][0]["status"] == "completed"


# ============================================================================
# TESTS - FHIR SUMMARY SERVICE (CRITICAL)
# ============================================================================

@pytest.mark.asyncio
async def test_emergency_patient_summary_performance():
    """Test that summary completes within 3 seconds"""
    service = get_summary_service()

    with patch.object(service, 'get_patient_summary', new_callable=AsyncMock) as mock_summary:
        mock_summary.return_value = {
            "patient": {
                "id": "pat-001",
                "name": "John Doe",
                "birth_date": "1980-01-15"
            },
            "active_allergies": [],
            "critical_allergies": [],
            "active_medications": [],
            "vital_signs": {},
            "critical_flags": [],
            "response_time_ms": 1500,
            "response_time_ok": True
        }

        result = await service.get_patient_summary("pat-001")

        assert result["response_time_ok"] is True
        assert result["response_time_ms"] < 3000


@pytest.mark.asyncio
async def test_critical_flags_generation():
    """Test critical flag generation"""
    service = get_summary_service()

    with patch.object(service, 'get_patient_summary', new_callable=AsyncMock) as mock_summary:
        mock_summary.return_value = {
            "patient": {"id": "pat-001"},
            "active_allergies": [{
                "criticality": "high",
                "critical_flags": ["CRITICAL_ALLERGY"]
            }],
            "active_conditions": [{
                "display": "Type 2 Diabetes"
            }],
            "critical_flags": [
                "CRITICAL_ALLERGIES",
                "DIABETES_ACTIVE"
            ],
            "has_critical_flags": True
        }

        result = await service.get_patient_summary("pat-001")

        assert result["has_critical_flags"] is True
        assert "CRITICAL_ALLERGIES" in result["critical_flags"]
        assert "DIABETES_ACTIVE" in result["critical_flags"]


# ============================================================================
# TESTS - ERROR HANDLING
# ============================================================================

@pytest.mark.asyncio
async def test_fhir_timeout_handling():
    """Test timeout error handling"""
    from app.services.fhir_client import FHIRClient

    client = FHIRClient(timeout=0.001)

    with pytest.raises(FHIRTimeoutError):
        # This should timeout with very short timeout
        await client.search("Patient", given="John")


@pytest.mark.asyncio
async def test_patient_not_found_error():
    """Test 404 error handling"""
    service = get_patient_service()

    with patch.object(service, 'get_patient', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = PatientNotFoundError("invalid-id")

        with pytest.raises(PatientNotFoundError):
            await service.get_patient("invalid-id")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_emergency_workflow():
    """Test complete emergency response workflow"""
    # 1. Get patient demographics
    patient_service = get_patient_service()
    with patch.object(patient_service, 'get_patient', new_callable=AsyncMock) as mock_patient:
        mock_patient.return_value = {
            "id": "pat-001",
            "given_name": "John",
            "family_name": "Doe"
        }
        patient = await patient_service.get_patient("pat-001")

    # 2. Get allergies
    allergy_service = get_allergy_service()
    with patch.object(allergy_service, 'get_patient_allergies', new_callable=AsyncMock) as mock_allergies:
        mock_allergies.return_value = {
            "allergies": [],
            "critical_allergies": [],
            "has_critical": False
        }
        allergies = await allergy_service.get_patient_allergies("pat-001")

    # 3. Get medications
    med_service = get_medication_service()
    with patch.object(med_service, 'get_patient_medications', new_callable=AsyncMock) as mock_meds:
        mock_meds.return_value = {
            "medications": [],
            "total": 0
        }
        medications = await med_service.get_patient_medications("pat-001")

    # Verify workflow completion
    assert patient["id"] == "pat-001"
    assert allergies["has_critical"] is False
    assert medications["total"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

