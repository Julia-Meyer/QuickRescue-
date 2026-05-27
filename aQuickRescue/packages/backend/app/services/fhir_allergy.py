"""
FHIR AllergyIntolerance Service
Handles patient allergies with critical severity highlighting
TASK-3.8 Implementation - CRITICAL for Emergency Responders
"""

import logging
from typing import Dict, List, Optional, Any
from app.services.fhir_client import get_fhir_client
from app.utils.errors import PatientNotFoundError

logger = logging.getLogger(__name__)


class FHIRAllergyService:
    """
    Service for FHIR AllergyIntolerance resource operations
    Critical: Used by emergency responders to identify severe allergies
    """

    @staticmethod
    async def get_patient_allergies(
        patient_id: str,
        clinical_status: Optional[str] = "active",
        criticality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get patient allergies with severity highlighting

        Args:
            patient_id: FHIR Patient ID
            clinical_status: Filter by status (active, inactive, resolved)
            criticality: Filter by criticality (low, high, unable-to-assess)

        Returns:
            List of allergies with critical flags
        """
        client = get_fhir_client()

        # Build search parameters
        params = {"patient": f"Patient/{patient_id}"}

        if clinical_status:
            params["clinical-status"] = clinical_status

        if criticality:
            params["criticality"] = criticality

        logger.info(f"Getting allergies for patient {patient_id}: {params}")

        try:
            bundle = await client.search("AllergyIntolerance", **params)

            allergies = []
            critical_allergies = []

            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                formatted = _format_allergy(resource)
                allergies.append(formatted)

                # Track critical allergies
                if (formatted.get("severity") == "severe" or
                    formatted.get("criticality") == "high"):
                    critical_allergies.append(formatted)

            return {
                "success": True,
                "patient_id": patient_id,
                "total": len(allergies),
                "critical_count": len(critical_allergies),
                "allergies": allergies,
                "critical_allergies": critical_allergies,
                "has_critical": len(critical_allergies) > 0
            }

        except Exception as e:
            logger.error(f"Error getting allergies for patient {patient_id}: {str(e)}")
            # Return empty on error (don't fail emergency access)
            return {
                "success": False,
                "patient_id": patient_id,
                "total": 0,
                "allergies": [],
                "critical_allergies": [],
                "error": str(e)
            }

    @staticmethod
    async def get_allergy(allergy_id: str) -> Dict[str, Any]:
        """
        Get single allergy by ID

        Args:
            allergy_id: FHIR AllergyIntolerance ID

        Returns:
            Formatted allergy object
        """
        client = get_fhir_client()

        logger.info(f"Getting allergy: {allergy_id}")

        try:
            resource = await client.get_resource("AllergyIntolerance", allergy_id)
            return _format_allergy(resource)

        except Exception as e:
            logger.error(f"Error getting allergy {allergy_id}: {str(e)}")
            raise

    @staticmethod
    async def create_allergy(allergy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new allergy in FHIR server

        Args:
            allergy_data: AllergyIntolerance resource data

        Returns:
            Created allergy with ID
        """
        client = get_fhir_client()

        allergy_data["resourceType"] = "AllergyIntolerance"

        logger.info(f"Creating allergy for patient {allergy_data.get('patient', {}).get('reference')}")

        try:
            created = await client.create_resource(allergy_data)
            return _format_allergy(created)

        except Exception as e:
            logger.error(f"Error creating allergy: {str(e)}")
            raise


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def _format_allergy(resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format FHIR AllergyIntolerance for API response
    Extracts critical information for emergency responders
    """

    # Extract allergen code
    code = resource.get("code", {})
    coding = code.get("coding", [{}])[0]

    # Extract reactions
    reactions = []
    for reaction in resource.get("reaction", []):
        manifestations = []
        for manifestation in reaction.get("manifestation", []):
            manifest_coding = manifestation.get("coding", [{}])[0]
            manifestations.append({
                "code": manifest_coding.get("code"),
                "display": manifest_coding.get("display")
            })

        reactions.append({
            "manifestations": manifestations,
            "severity": reaction.get("severity", "unknown"),
            "onset": reaction.get("onset"),
            "exposure_route": reaction.get("exposureRoute", {}).get("coding", [{}])[0].get("display")
        })

    # Extract clinical status
    clinical_status = resource.get("clinicalStatus", {})
    clinical_coding = clinical_status.get("coding", [{}])[0] if clinical_status else {}

    # Extract criticality (CRITICAL for emergency)
    criticality = resource.get("criticality", "unable-to-assess")

    # Determine if critical (for highlighting in UI)
    is_critical = (
        criticality == "high" or
        any(r.get("severity") == "severe" for r in reactions)
    )

    return {
        "id": resource.get("id"),
        "code": coding.get("code"),
        "display": coding.get("display"),
        "text": code.get("text"),
        "status": clinical_coding.get("code", "unknown"),
        "verification_status": resource.get("verificationStatus", {}).get("coding", [{}])[0].get("code"),
        "category": resource.get("category", []),
        "criticality": criticality,
        "reactions": reactions,
        "onset_date": resource.get("onsetDate"),
        "last_occurrence": resource.get("lastOccurrence"),
        "notes": [note.get("text") for note in resource.get("note", [])],
        "is_critical": is_critical,
        "critical_flags": _generate_critical_flags(resource)
    }


def _generate_critical_flags(resource: Dict[str, Any]) -> List[str]:
    """
    Generate critical flags for emergency responders
    """
    flags = []

    # Check criticality
    if resource.get("criticality") == "high":
        flags.append("CRITICAL_ALLERGY")

    # Check severity
    reactions = resource.get("reaction", [])
    if any(r.get("severity") == "severe" for r in reactions):
        flags.append("SEVERE_REACTION")

    # Check for anaphylaxis
    for reaction in reactions:
        for manifestation in reaction.get("manifestation", []):
            coding = manifestation.get("coding", [{}])[0]
            if coding.get("code") == "39579001":  # Anaphylaxis
                flags.append("ANAPHYLAXIS_RISK")
            if "shock" in coding.get("display", "").lower():
                flags.append("SHOCK_RISK")

    # Check allergen type
    code = resource.get("code", {})
    coding = code.get("coding", [{}])[0]
    if coding.get("code") == "2670000":  # Penicillin
        flags.append("ANTIBIOTIC_ALLERGY")

    return flags


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_allergy_service: Optional[FHIRAllergyService] = None

def get_allergy_service() -> FHIRAllergyService:
    """Get singleton allergy service"""
    global _allergy_service
    if _allergy_service is None:
        _allergy_service = FHIRAllergyService()
    return _allergy_service

