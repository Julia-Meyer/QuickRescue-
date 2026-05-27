"""
FHIR Medication & MedicationDispense Service
Handles patient medications with dosage information
TASK-3.7 Implementation
"""

import logging
from typing import Dict, List, Optional, Any
from app.services.fhir_client import get_fhir_client

logger = logging.getLogger(__name__)


class FHIRMedicationService:
    """
    Service for FHIR Medication and MedicationDispense resources
    """

    @staticmethod
    async def get_patient_medications(
        patient_id: str,
        status: Optional[str] = None,
        effective_time_ge: Optional[str] = None,
        effective_time_le: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get patient medications from MedicationDispense

        Args:
            patient_id: FHIR Patient ID
            status: Filter by status (completed, in-progress, on-hold, cancelled)
            effective_time_ge: Start date (YYYY-MM-DD)
            effective_time_le: End date (YYYY-MM-DD)

        Returns:
            List of medications with dosage info
        """
        client = get_fhir_client()

        # Build search parameters
        params = {"patient": f"Patient/{patient_id}"}

        if status:
            params["status"] = status
        else:
            # Default: completed and in-progress
            params["status"] = "completed,in-progress"

        if effective_time_ge:
            params["effective-time"] = f"ge{effective_time_ge}"

        if effective_time_le:
            if "effective-time" in params:
                # Add as separate parameter
                params["effective-time-le"] = f"le{effective_time_le}"
            else:
                params["effective-time"] = f"le{effective_time_le}"

        logger.info(f"Getting medications for patient {patient_id}")

        try:
            bundle = await client.search("MedicationDispense", **params)

            medications = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                formatted = await _format_medication_dispense(resource, client)
                medications.append(formatted)

            return {
                "success": True,
                "patient_id": patient_id,
                "total": len(medications),
                "medications": medications
            }

        except Exception as e:
            logger.error(f"Error getting medications for patient {patient_id}: {str(e)}")
            return {
                "success": False,
                "patient_id": patient_id,
                "total": 0,
                "medications": [],
                "error": str(e)
            }

    @staticmethod
    async def get_medication(medication_id: str) -> Dict[str, Any]:
        """
        Get single medication by ID

        Args:
            medication_id: FHIR Medication ID

        Returns:
            Formatted medication object
        """
        client = get_fhir_client()

        logger.info(f"Getting medication: {medication_id}")

        try:
            resource = await client.get_resource("Medication", medication_id)
            return _format_medication(resource)

        except Exception as e:
            logger.error(f"Error getting medication {medication_id}: {str(e)}")
            raise

    @staticmethod
    async def get_medication_dispense(dispense_id: str) -> Dict[str, Any]:
        """
        Get single medication dispense by ID

        Args:
            dispense_id: FHIR MedicationDispense ID

        Returns:
            Formatted dispense object
        """
        client = get_fhir_client()

        logger.info(f"Getting medication dispense: {dispense_id}")

        try:
            resource = await client.get_resource("MedicationDispense", dispense_id)
            return await _format_medication_dispense(resource, client)

        except Exception as e:
            logger.error(f"Error getting dispense {dispense_id}: {str(e)}")
            raise


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def _format_medication(resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format FHIR Medication resource
    """
    code = resource.get("code", {})
    coding = code.get("coding", [{}])[0]

    # Extract strength
    strength = resource.get("strength", {})
    strength_info = {}
    if strength:
        numerator = strength.get("numerator", {})
        strength_info = {
            "value": numerator.get("value"),
            "unit": numerator.get("unit")
        }

    return {
        "id": resource.get("id"),
        "code": coding.get("code"),
        "system": coding.get("system"),
        "display": coding.get("display"),
        "text": code.get("text"),
        "strength": strength_info
    }


async def _format_medication_dispense(
    resource: Dict[str, Any],
    client
) -> Dict[str, Any]:
    """
    Format FHIR MedicationDispense resource
    Resolves medication reference and extracts dosage info
    """

    # Get medication reference
    med_ref = resource.get("medicationReference", {})
    med_id = med_ref.get("reference", "").split("/")[-1] if med_ref.get("reference") else None
    medication = {}

    if med_id:
        try:
            medication = await client.get_resource("Medication", med_id)
            medication = _format_medication(medication)
        except Exception as e:
            logger.warning(f"Could not resolve medication reference: {str(e)}")

    # Extract dosage instructions
    dosages = []
    for dosage in resource.get("dosageInstruction", []):
        dosage_info = {
            "text": dosage.get("text"),
            "timing": _extract_timing(dosage.get("timing", {})),
            "route": _extract_coding(dosage.get("route")),
            "dose": _extract_dose(dosage.get("doseAndRate", [{}])[0])
        }
        dosages.append(dosage_info)

    return {
        "id": resource.get("id"),
        "status": resource.get("status"),
        "medication": medication,
        "dispense_date": resource.get("whenPrepared"),
        "handed_over_date": resource.get("whenHandedOver"),
        "quantity": {
            "value": resource.get("quantity", {}).get("value"),
            "unit": resource.get("quantity", {}).get("unit")
        },
        "days_supply": resource.get("daysSupply", {}).get("value"),
        "dosage_instructions": dosages,
        "performer": resource.get("performer", [{}])[0].get("actor", {}).get("display")
    }


def _extract_timing(timing: Dict[str, Any]) -> Dict[str, Any]:
    """Extract timing from Dosage"""
    repeat = timing.get("repeat", {})

    return {
        "frequency": repeat.get("frequency"),
        "period": repeat.get("period"),
        "period_unit": repeat.get("periodUnit"),
        "text": timing.get("code", {}).get("text")
    }


def _extract_coding(coding_obj: Optional[Dict]) -> Optional[Dict]:
    """Extract first coding from CodeableConcept"""
    if not coding_obj:
        return None

    coding = coding_obj.get("coding", [{}])[0] if coding_obj else {}
    return {
        "code": coding.get("code"),
        "system": coding.get("system"),
        "display": coding.get("display")
    } if coding else None


def _extract_dose(dose_info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract dose from DoseAndRate"""
    dose_qty = dose_info.get("doseQuantity", {})

    return {
        "value": dose_qty.get("value"),
        "unit": dose_qty.get("unit")
    }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_medication_service: Optional[FHIRMedicationService] = None

def get_medication_service() -> FHIRMedicationService:
    """Get singleton medication service"""
    global _medication_service
    if _medication_service is None:
        _medication_service = FHIRMedicationService()
    return _medication_service

