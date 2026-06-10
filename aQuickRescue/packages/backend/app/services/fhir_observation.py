"""
FHIR Observation Service
Handles vital signs, laboratory results, and other observations using LOINC codes
Uses config: packages/backend/app/config/loinc_mapping.json

⚠️  MVP STATUS: NOT REQUIRED FOR MVP
This module is DEPRECATED for QuickRescue MVP (Phase 1).
The system focuses on: Allergies, Medications, and Emergency Contacts.
Observation support (vital signs, lab results) is reserved for Phase 2+.

Reference: SPECIFICATION.md - Core emergency data includes ONLY:
  - AllergyIntolerance (allergies)
  - MedicationStatement (current medications)
  - Patient.contact (emergency contacts)
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from app.services.fhir_client import get_fhir_client

logger = logging.getLogger(__name__)

# Load LOINC code mapping configuration
_LOINC_CONFIG = None

def _load_loinc_config() -> Dict[str, Any]:
    """Load LOINC code to observation mapping"""
    global _LOINC_CONFIG
    if _LOINC_CONFIG is not None:
        return _LOINC_CONFIG

    config_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "config",
        "loinc_mapping.json"
    )

    try:
        with open(config_path, 'r') as f:
            _LOINC_CONFIG = json.load(f)
        logger.info(f"Loaded LOINC configuration from {config_path}")
    except FileNotFoundError:
        logger.warning(f"LOINC config not found at {config_path}, using minimal defaults")
        _LOINC_CONFIG = {
            "fhir_system": "http://loinc.org",
            "vital_signs": {},
            "laboratory_tests": {},
            "critical_flags": {}
        }

    return _LOINC_CONFIG


class FHIRObservationService:
    """
    Service for FHIR Observation resource operations
    Handles vital signs, lab results, and other observations
    """

    @staticmethod
    async def get_patient_vital_signs(
        patient_id: str,
        category: str = "vital-signs",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        ⚠️  DEPRECATED: Not used in MVP
        Get patient vital signs (latest observations)

        Reserved for Phase 2+ when Observation support is needed.

        Args:
            patient_id: FHIR Patient ID
            category: Observation category (vital-signs, laboratory, etc.)
            limit: Maximum number of results

        Returns:
            Dictionary with formatted vital signs
        """
        logger.warning(f"get_patient_vital_signs() called - feature not in MVP scope for patient {patient_id}")
        client = get_fhir_client()
        config = _load_loinc_config()

        logger.info(f"Getting {category} observations for patient {patient_id}")

        try:
            bundle = await client.search(
                "Observation",
                **{
                    "patient": f"Patient/{patient_id}",
                    "category": category,
                    "_sort": "-date",
                    "_count": limit
                }
            )

            observations = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                formatted = _format_observation(resource, config)
                observations.append(formatted)

            return {
                "success": True,
                "patient_id": patient_id,
                "category": category,
                "total": len(observations),
                "observations": observations
            }

        except Exception as e:
            logger.error(f"Error getting {category} for patient {patient_id}: {str(e)}")
            return {
                "success": False,
                "patient_id": patient_id,
                "category": category,
                "total": 0,
                "observations": [],
                "error": str(e)
            }

    @staticmethod
    async def get_patient_lab_results(
        patient_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        ⚠️  DEPRECATED: Not used in MVP
        Get patient laboratory results

        Reserved for Phase 2+ when Observation support is needed.

        Args:
            patient_id: FHIR Patient ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum results

        Returns:
            Laboratory test results
        """
        logger.warning(f"get_patient_lab_results() called - feature not in MVP scope for patient {patient_id}")
        client = get_fhir_client()
        config = _load_loinc_config()

        params = {
            "patient": f"Patient/{patient_id}",
            "category": "laboratory",
            "_sort": "-date",
            "_count": limit
        }

        if date_from:
            params["date"] = f"ge{date_from}"
        if date_to:
            params["date-end"] = f"le{date_to}"

        logger.info(f"Getting lab results for patient {patient_id}")

        try:
            bundle = await client.search("Observation", **params)

            labs = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                formatted = _format_observation(resource, config)
                labs.append(formatted)

            return {
                "success": True,
                "patient_id": patient_id,
                "total": len(labs),
                "results": labs
            }

        except Exception as e:
            logger.error(f"Error getting lab results: {str(e)}")
            return {
                "success": False,
                "patient_id": patient_id,
                "total": 0,
                "results": [],
                "error": str(e)
            }

    @staticmethod
    async def get_observation_by_loinc(
        patient_id: str,
        loinc_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        ⚠️  DEPRECATED: Not used in MVP
        Get specific observation by LOINC code

        Reserved for Phase 2+ when Observation support is needed.

        Args:
            patient_id: FHIR Patient ID
            loinc_code: LOINC code (e.g., "2345-7" for glucose)

        Returns:
            Observation or None
        """
        logger.warning(f"get_observation_by_loinc() called with code {loinc_code} - feature not in MVP scope")
        client = get_fhir_client()
        config = _load_loinc_config()

        logger.info(f"Getting observation {loinc_code} for patient {patient_id}")

        try:
            bundle = await client.search(
                "Observation",
                **{
                    "patient": f"Patient/{patient_id}",
                    "code": f"http://loinc.org|{loinc_code}",
                    "_sort": "-date",
                    "_count": 1
                }
            )

            if bundle.get("entry"):
                resource = bundle["entry"][0].get("resource", {})
                return _format_observation(resource, config)

            return None

        except Exception as e:
            logger.error(f"Error getting observation {loinc_code}: {str(e)}")
            return None


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def _format_observation(resource: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format FHIR Observation resource
    Extracts LOINC codes and critical values
    """

    # Extract LOINC code
    code_obj = resource.get("code", {})
    loinc_system = config.get("fhir_system", "http://loinc.org")

    # Find LOINC coding
    loinc_code = None
    loinc_display = None

    for coding in code_obj.get("coding", []):
        if coding.get("system") == loinc_system:
            loinc_code = coding.get("code")
            loinc_display = coding.get("display")
            break

    # Extract value
    value = None
    unit = None

    if "valueQuantity" in resource:
        qty = resource.get("valueQuantity", {})
        value = qty.get("value")
        unit = qty.get("unit") or qty.get("code")
    elif "valueCodeableConcept" in resource:
        concept = resource.get("valueCodeableConcept", {})
        coding = concept.get("coding", [{}])[0]
        value = coding.get("display")
    elif "valueString" in resource:
        value = resource.get("valueString")

    # Get critical flags and reference range
    critical_flags = _get_critical_flags(loinc_code, value, config)
    ref_range = _get_reference_range(loinc_code, config)

    return {
        "id": resource.get("id"),
        "loinc_code": loinc_code,
        "display": loinc_display,
        "category": resource.get("category", [{}])[0].get("coding", [{}])[0].get("code"),
        "value": value,
        "unit": unit,
        "reference_range": ref_range,
        "status": resource.get("status"),
        "effective_time": resource.get("effectiveDateTime"),
        "method": resource.get("method", {}).get("coding", [{}])[0].get("display"),
        "critical_flags": critical_flags,
        "is_critical": len(critical_flags) > 0,
        "notes": [note.get("text") for note in resource.get("note", [])]
    }


def _get_reference_range(loinc_code: Optional[str], config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract reference range for LOINC code"""
    if not loinc_code:
        return None

    # Search in vital_signs
    for key, obs_config in config.get("vital_signs", {}).items():
        if obs_config.get("loinc") == loinc_code:
            return {
                "normal_low": obs_config.get("critical_low"),
                "normal_high": obs_config.get("critical_high"),
                "warning_low": obs_config.get("warning_low"),
                "warning_high": obs_config.get("warning_high")
            }

    # Search in laboratory_tests
    for key, obs_config in config.get("laboratory_tests", {}).items():
        if obs_config.get("loinc") == loinc_code:
            return {
                "normal_range": obs_config.get("normal_range"),
                "critical_low": obs_config.get("critical_low"),
                "critical_high": obs_config.get("critical_high"),
                "warning_low": obs_config.get("warning_low"),
                "warning_high": obs_config.get("warning_high")
            }

    return None


def _get_critical_flags(
    loinc_code: Optional[str],
    value: Optional[Any],
    config: Dict[str, Any]
) -> List[str]:
    """
    Generate critical flags based on LOINC code and value
    """
    flags = []

    if not loinc_code or value is None:
        return flags

    critical_flags_map = config.get("critical_flags", {})

    try:
        # Convert value to float for comparison
        numeric_value = float(value) if isinstance(value, (int, float, str)) else None

        if numeric_value is None:
            return flags

        # Check each critical flag definition
        for flag_key, flag_config in critical_flags_map.items():
            if flag_config.get("loinc") == loinc_code:
                threshold = flag_config.get("threshold")
                if threshold is not None:
                    # Determine if critical based on threshold
                    if flag_key in ["hypoglycemia", "hypotension", "bradycardia", "hypothermia", "anemia", "leukopenia", "thrombocytopenia", "acute_kidney_injury"]:
                        # Low-side critical
                        if numeric_value < threshold:
                            flags.append(flag_config.get("flag"))
                    else:
                        # High-side critical
                        if numeric_value > threshold:
                            flags.append(flag_config.get("flag"))

    except (ValueError, TypeError) as e:
        logger.debug(f"Could not evaluate critical flags for {loinc_code}: {str(e)}")

    return flags


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_observation_service: Optional[FHIRObservationService] = None

def get_observation_service() -> FHIRObservationService:
    """Get singleton observation service"""
    global _observation_service
    if _observation_service is None:
        _observation_service = FHIRObservationService()
    return _observation_service

