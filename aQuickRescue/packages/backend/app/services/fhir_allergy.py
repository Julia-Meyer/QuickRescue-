"""
FHIR AllergyIntolerance Service
Handles patient allergies with critical severity highlighting
TASK-3.8 Implementation - CRITICAL for Emergency Responders

Uses SNOMED CT codes for critical allergy flag detection.
Configuration: packages/backend/app/config/snomed_flags.json
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from app.services.fhir_client import get_fhir_client
from app.utils.errors import PatientNotFoundError

logger = logging.getLogger(__name__)

# Load SNOMED code mapping configuration
_SNOMED_CONFIG = None

def _load_snomed_config() -> Dict[str, Any]:
    """Load SNOMED CT code to critical flag mapping"""
    global _SNOMED_CONFIG
    if _SNOMED_CONFIG is not None:
        return _SNOMED_CONFIG

    config_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "config",
        "snomed_flags.json"
    )

    try:
        with open(config_path, 'r') as f:
            _SNOMED_CONFIG = json.load(f)
        logger.info(f"Loaded SNOMED configuration from {config_path}")
    except FileNotFoundError:
        logger.warning(f"SNOMED config not found at {config_path}, using defaults")
        _SNOMED_CONFIG = {
            "snomed_system": "http://snomed.info/sct",
            "critical_codes": {},
            "critical_reaction_codes": {}
        }

    return _SNOMED_CONFIG


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
    Generate critical flags for emergency responders using SNOMED CT code mapping

    Explicit SNOMED system validation ensures flags only generated from
    recognized clinical coding systems.
    """
    config = _load_snomed_config()
    snomed_system = config.get("snomed_system", "http://snomed.info/sct")
    critical_codes_map = config.get("critical_codes", {})
    critical_reaction_codes = config.get("critical_reaction_codes", {})

    flags = []

    # Check allergen code (main allergen)
    code = resource.get("code", {})
    coding = code.get("coding", [{}])[0]

    # EXPLICIT CHECK: Verify this is SNOMED CT coding
    if coding.get("system") == snomed_system:
        allergen_code = coding.get("code")

        # Look up allergen code in mapping
        for category, category_info in critical_codes_map.items():
            if allergen_code in category_info.get("codes", []):
                flag = category_info.get("flag")
                if flag:
                    flags.append(flag)
                logger.debug(f"SNOMED allergen {allergen_code} mapped to {flag}")
    else:
        logger.debug(f"Allergen code uses non-SNOMED system: {coding.get('system')}")

    # Check severity
    criticality = resource.get("criticality", "unable-to-assess")
    if criticality == "high":
        flags.append("CRITICAL_ALLERGY")

    # Check reaction severity and manifestations
    reactions = resource.get("reaction", [])
    for reaction in reactions:
        severity = reaction.get("severity", "unknown")
        if severity == "severe":
            flags.append("SEVERE_REACTION")

        # Check reaction manifestations (symptoms)
        for manifestation in reaction.get("manifestation", []):
            manifest_coding = manifestation.get("coding", [{}])[0]

            # EXPLICIT CHECK: Verify manifestation is SNOMED coded
            if manifest_coding.get("system") == snomed_system:
                reaction_code = manifest_coding.get("code")

                # Check if this reaction code has critical mapping
                if reaction_code in critical_reaction_codes:
                    critical_info = critical_reaction_codes[reaction_code]
                    reaction_flag = critical_info.get("flag")
                    if reaction_flag:
                        flags.append(reaction_flag)
                    logger.debug(f"SNOMED reaction {reaction_code} mapped to {reaction_flag}")

    return sorted(list(set(flags)))  # Remove duplicates and sort


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

