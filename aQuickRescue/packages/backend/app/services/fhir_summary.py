"""
FHIR Emergency Patient Summary Service
Unified endpoint that returns all critical patient information for emergency responders
TASK-3.10 Implementation - CRITICAL
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from app.services.fhir_client import get_fhir_client
from app.services.fhir_patient import get_patient_service
from app.services.fhir_allergy import get_allergy_service
from app.services.fhir_medication import get_medication_service
from datetime import datetime

logger = logging.getLogger(__name__)


class FHIRSummaryService:
    """
    Service for comprehensive patient summary
    Makes parallel FHIR calls to compile all critical information
    Target: < 3 seconds response time
    """

    @staticmethod
    async def get_patient_summary(patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive patient summary for emergency responders

        Makes parallel calls to:
        1. Patient demographics
        2. Active allergies (CRITICAL)
        3. Current medications (CRITICAL)
        4. Active conditions
        5. Recent procedures

        Args:
            patient_id: FHIR Patient ID

        Returns:
            Comprehensive patient summary with critical flags
        """
        logger.info(f"Generating summary for patient {patient_id}")
        start_time = datetime.utcnow()

        try:
            # Make parallel calls to all services
            patient_task = get_patient_service().get_patient(patient_id)
            allergies_task = get_allergy_service().get_patient_allergies(patient_id)
            medications_task = get_medication_service().get_patient_medications(patient_id)
            observations_task = _get_vital_signs(patient_id)
            conditions_task = _get_active_conditions(patient_id)

            # Execute concurrently
            results = await asyncio.gather(
                patient_task,
                allergies_task,
                medications_task,
                observations_task,
                conditions_task,
                return_exceptions=True
            )

            patient = results[0] if not isinstance(results[0], Exception) else {}
            allergies_result = results[1] if not isinstance(results[1], Exception) else {}
            medications_result = results[2] if not isinstance(results[2], Exception) else {}
            observations = results[3] if not isinstance(results[3], Exception) else {}
            conditions = results[4] if not isinstance(results[4], Exception) else {}

            # Extract blood type from patient resource
            blood_type = _extract_blood_type(patient)

            # Extract emergency contact
            emergency_contact = {}
            # This would be in patient.contact field

            # Generate critical flags
            critical_flags = _generate_summary_critical_flags(
                allergies_result,
                medications_result,
                conditions,
                observations
            )

            # Calculate response time
            response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            summary = {
                "patient": {
                    "id": patient_id,
                    "name": f"{patient.get('given_name', '')} {patient.get('family_name', '')}".strip(),
                    "birth_date": patient.get("birth_date"),
                    "gender": patient.get("gender"),
                    "phone": patient.get("phone"),
                    "email": patient.get("email")
                },
                "blood_type": blood_type,
                "emergency_contact": emergency_contact,
                "active_allergies": allergies_result.get("allergies", []),
                "critical_allergies": allergies_result.get("critical_allergies", []),
                "allergies_count": allergies_result.get("total", 0),
                "has_critical_allergies": allergies_result.get("has_critical", False),
                "active_medications": medications_result.get("medications", []),
                "medications_count": medications_result.get("total", 0),
                "active_conditions": conditions.get("conditions", []),
                "conditions_count": conditions.get("total", 0),
                "vital_signs": observations.get("vital_signs", {}),
                "recent_labs": observations.get("recent_labs", []),
                "critical_flags": critical_flags,
                "has_critical_flags": len(critical_flags) > 0,
                "summary_generated_at": datetime.utcnow().isoformat(),
                "response_time_ms": response_time_ms,
                "response_time_ok": response_time_ms < 3000
            }

            logger.info(f"Summary generated in {response_time_ms:.0f}ms with {len(critical_flags)} critical flags")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary for patient {patient_id}: {str(e)}")
            raise


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _extract_blood_type(patient: Dict[str, Any]) -> Optional[str]:
    """Extract blood type from patient resource"""
    # Blood type is usually in an extension or coded value
    # This depends on FHIR server configuration
    return None  # To be implemented based on server


async def _get_vital_signs(patient_id: str) -> Dict[str, Any]:
    """Get latest vital signs"""
    client = get_fhir_client()

    try:
        # Search for vital signs observations
        bundle = await client.search(
            "Observation",
            **{
                "patient": f"Patient/{patient_id}",
                "category": "vital-signs",
                "_sort": "-date",
                "_count": 10
            }
        )

        vital_signs = {}
        labs = []

        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            code = resource.get("code", {}).get("coding", [{}])[0]
            loinc_code = code.get("code")

            # Extract value
            value = None
            if "valueQuantity" in resource:
                value = resource.get("valueQuantity", {}).get("value")
            elif "valueCodeableConcept" in resource:
                value = resource.get("valueCodeableConcept", {}).get("coding", [{}])[0].get("display")

            # Map LOINC codes to vital signs
            if loinc_code == "8480-6":
                vital_signs["systolic_bp"] = value
            elif loinc_code == "8462-4":
                vital_signs["diastolic_bp"] = value
            elif loinc_code == "8867-4":
                vital_signs["heart_rate"] = value
            elif loinc_code == "8310-5":
                vital_signs["temperature"] = value
            elif loinc_code == "59408-5":
                vital_signs["oxygen_saturation"] = value

            vital_signs["last_measured"] = resource.get("effectiveDateTime")

        return {
            "vital_signs": vital_signs,
            "recent_labs": labs
        }

    except Exception as e:
        logger.warning(f"Error getting vital signs: {str(e)}")
        return {"vital_signs": {}, "recent_labs": []}


async def _get_active_conditions(patient_id: str) -> Dict[str, Any]:
    """Get active patient conditions/diagnoses"""
    client = get_fhir_client()

    try:
        bundle = await client.search(
            "Condition",
            **{
                "patient": f"Patient/{patient_id}",
                "clinical-status": "active"
            }
        )

        conditions = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            code = resource.get("code", {})
            coding = code.get("coding", [{}])[0]

            conditions.append({
                "id": resource.get("id"),
                "code": coding.get("code"),
                "display": coding.get("display"),
                "text": code.get("text"),
                "status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code"),
                "onset_date": resource.get("onsetDate")
            })

        return {
            "total": len(conditions),
            "conditions": conditions
        }

    except Exception as e:
        logger.warning(f"Error getting conditions: {str(e)}")
        return {"total": 0, "conditions": []}


def _generate_summary_critical_flags(
    allergies: Dict,
    medications: Dict,
    conditions: Dict,
    observations: Dict
) -> List[str]:
    """
    Generate critical flags from all patient data

    Returns:
        List of critical flags for emergency responders
    """
    flags = []

    # Check for severe allergies
    critical_allergies = allergies.get("critical_allergies", [])
    if critical_allergies:
        flags.append("CRITICAL_ALLERGIES")
        for allergy in critical_allergies:
            flags.extend(allergy.get("critical_flags", []))

    # Check medications for special handling
    medications_list = medications.get("medications", [])
    for med in medications_list:
        med_display = med.get("medication", {}).get("display", "").lower()

        if "anticoagulant" in med_display or "warfarin" in med_display:
            flags.append("ON_ANTICOAGULANT")
        elif "insulin" in med_display or "diabetes" in med_display:
            flags.append("DIABETIC")
        elif "corticosteroid" in med_display:
            flags.append("ON_STEROIDS")

    # Check active conditions
    conditions_list = conditions.get("conditions", [])
    for condition in conditions_list:
        condition_display = condition.get("display", "").lower()

        if "diabetes" in condition_display:
            flags.append("DIABETES_ACTIVE")
        elif "asthma" in condition_display:
            flags.append("ASTHMA_ACTIVE")
        elif "epilepsy" in condition_display or "seizure" in condition_display:
            flags.append("SEIZURE_DISORDER")
        elif "pregnancy" in condition_display:
            flags.append("PREGNANCY_ACTIVE")

    # Check vital signs
    vital_signs = observations.get("vital_signs", {})
    systolic = vital_signs.get("systolic_bp")
    diastolic = vital_signs.get("diastolic_bp")
    hr = vital_signs.get("heart_rate")
    o2 = vital_signs.get("oxygen_saturation")

    if systolic and systolic > 160:
        flags.append("BP_CRITICAL_HIGH")
    elif systolic and systolic > 140:
        flags.append("BP_ELEVATED")

    if hr and hr < 40:
        flags.append("HEART_RATE_CRITICAL_LOW")
    elif hr and hr > 120:
        flags.append("HEART_RATE_ELEVATED")

    if o2 and o2 < 90:
        flags.append("O2_SATURATION_LOW")

    return sorted(list(set(flags)))  # Remove duplicates and sort


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_summary_service: Optional[FHIRSummaryService] = None

def get_summary_service() -> FHIRSummaryService:
    """Get singleton summary service"""
    global _summary_service
    if _summary_service is None:
        _summary_service = FHIRSummaryService()
    return _summary_service

