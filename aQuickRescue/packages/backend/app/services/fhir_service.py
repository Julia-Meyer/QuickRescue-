"""
FHIR Service - Mock.Health integration

Moved out of main.py to keep the application module slim.
Provides MockHealthService (config + headers) and FHIRService wrappers used
by the FastAPI endpoints.
"""
from typing import Dict, List
import os
import logging

logger = logging.getLogger(__name__)


class MockHealthService:
    """Service for Mock.Health FHIR API integration"""

    # Load Mock.Health config from env
    MOCK_HEALTH_API_URL = os.getenv("MOCK_HEALTH_API_URL", "https://api.mock.health")
    MOCK_HEALTH_FHIR_URL = os.getenv("MOCK_HEALTH_FHIR_URL", "https://api.mock.health/fhir")
    MOCK_HEALTH_API_KEY = os.getenv("MOCK_HEALTH_API_KEY", "")

    @staticmethod
    def _get_headers():
        """Get HTTP headers with Mock.Health API key"""
        return {
            "Authorization": f"Bearer {MockHealthService.MOCK_HEALTH_API_KEY}",
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        }

    @staticmethod
    def _build_url(resource_type: str):
        """Build FHIR resource URL for Mock.Health"""
        return f"{MockHealthService.MOCK_HEALTH_FHIR_URL}/{resource_type}"


class FHIRService:
    """Service for FHIR server integration (delegates to MockHealthService)"""

    FHIR_BASE_URL = MockHealthService.MOCK_HEALTH_FHIR_URL
    # cache TTLs (seconds)
    TTL_PATIENT = int(os.getenv("CACHE_TTL_PATIENT", 3600))
    TTL_MEDICATIONS = int(os.getenv("CACHE_TTL_MEDICATIONS", 1800))
    TTL_ALLERGIES = int(os.getenv("CACHE_TTL_ALLERGIES", 1800))
    TTL_CONDITIONS = int(os.getenv("CACHE_TTL_CONDITIONS", 3600))
    TTL_RELATED = int(os.getenv("CACHE_TTL_RELATED", 3600))

    @staticmethod
    def search_patient(first_name: str, last_name: str, dob: str) -> dict:
        """
        Search Mock.Health FHIR server for patient
        Performance: Target < 2 seconds
        """
        import httpx

        try:
            query = MockHealthService._build_url("Patient")
            params = {}
            if first_name:
                params["given"] = first_name
            if last_name:
                params["family"] = last_name
            if dob:
                params["birthdate"] = dob

            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params, headers=headers)
                response.raise_for_status()

            bundle = response.json()

            if bundle.get("total", 0) == 0:
                return {"found": False, "patients": []}

            patients = []
            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                patients.append({
                    "id": resource.get("id"),
                    "name": " ".join([
                        name.get("given", [""])[0]
                        for name in resource.get("name", [])
                    ]),
                    "birthDate": resource.get("birthDate")
                })

            logger.info(f"Found {len(patients)} patients matching criteria")
            return {"found": True, "patients": patients}
        except Exception as e:
            logger.error(f"Mock.Health FHIR search error: {str(e)}")
            return {"found": False, "error": str(e)}

    @staticmethod
    def get_patient_allergies(patient_id: str) -> List[dict]:
        """Get patient allergies from Mock.Health FHIR server"""
        import httpx

        try:
            query = MockHealthService._build_url("AllergyIntolerance")
            params = {"patient": patient_id}
            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params, headers=headers)
                response.raise_for_status()

            bundle = response.json()
            allergies = []

            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                code = resource.get("code", {}).get("coding", [{}])[0]
                allergies.append({
                    "code": code.get("code"),
                    "display": code.get("display"),
                    "criticality": resource.get("criticality", "unknown")
                })

            logger.info(f"Retrieved {len(allergies)} allergies for patient {patient_id}")
            return allergies
        except Exception as e:
            logger.error(f"Error fetching allergies from Mock.Health: {str(e)}")
            return []

    @staticmethod
    def get_patient_medications(patient_id: str) -> List[dict]:
        """Get patient medications (MedicationStatement) from Mock.Health FHIR server"""
        import httpx

        try:
            query = MockHealthService._build_url("MedicationStatement")
            params = {"patient": patient_id}
            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=params, headers=headers)
                response.raise_for_status()

            bundle = response.json()
            medications = []

            for entry in bundle.get("entry", []):
                resource = entry.get("resource", {})
                medications.append({
                    "id": resource.get("id"),
                    "medication": resource.get("medicationReference", {}).get("display", "Unknown"),
                    "dosage": resource.get("dosage", [{}])[0].get("text", ""),
                    "status": resource.get("status", "unknown")
                })

            logger.info(f"Retrieved {len(medications)} medications for patient {patient_id}")
            return medications
        except Exception as e:
            logger.error(f"Error fetching medications from Mock.Health: {str(e)}")
            return []

    @staticmethod
    def get_patient(patient_id: str) -> dict:
        """Get a single Patient resource from Mock.Health FHIR"""
        import httpx
        try:
            key = f"patient:{patient_id}"
            # Try cache if available
            try:
                from packages.backend.app.services.cache import cache
                cached = cache.get(key)
                if cached:
                    logger.info(f"Cache hit for patient {patient_id}")
                    return cached
            except Exception:
                cached = None

            query = MockHealthService._build_url(f"Patient/{patient_id}")
            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, headers=headers)
                response.raise_for_status()

            resource = response.json()

            # Cache
            try:
                from packages.backend.app.services.cache import cache
                cache.set(key, resource, FHIRService.TTL_PATIENT)
            except Exception:
                pass

            logger.info(f"Retrieved patient {patient_id} from Mock.Health")
            return resource
        except Exception as e:
            logger.error(f"Error fetching patient {patient_id} from Mock.Health: {str(e)}")
            return {}

    @staticmethod
    def get_medication_statements(patient_id: str, params: Dict = None) -> dict:
        import httpx
        try:
            key = f"meds:{patient_id}:{str(params)}"
            try:
                from packages.backend.app.services.cache import cache
                cached = cache.get(key)
                if cached:
                    logger.info(f"Cache hit for medication statements {patient_id}")
                    return cached
            except Exception:
                cached = None

            query = MockHealthService._build_url("MedicationStatement")
            query_params = {"patient": patient_id}
            if params:
                query_params.update(params)

            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=query_params, headers=headers)
                response.raise_for_status()

            bundle = response.json()

            try:
                from packages.backend.app.services.cache import cache
                cache.set(key, bundle, FHIRService.TTL_MEDICATIONS)
            except Exception:
                pass

            logger.info(f"Retrieved {bundle.get('total', 0)} medication statements for patient {patient_id}")
            return bundle
        except Exception as e:
            logger.error(f"Error fetching medication statements for {patient_id}: {str(e)}")
            return {"entry": []}

    @staticmethod
    def get_conditions(patient_id: str, params: Dict = None) -> dict:
        import httpx
        try:
            key = f"conds:{patient_id}:{str(params)}"
            try:
                from packages.backend.app.services.cache import cache
                cached = cache.get(key)
                if cached:
                    logger.info(f"Cache hit for conditions {patient_id}")
                    return cached
            except Exception:
                cached = None

            query = MockHealthService._build_url("Condition")
            query_params = {"patient": patient_id}
            if params:
                query_params.update(params)

            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=query_params, headers=headers)
                response.raise_for_status()

            bundle = response.json()

            try:
                from packages.backend.app.services.cache import cache
                cache.set(key, bundle, FHIRService.TTL_CONDITIONS)
            except Exception:
                pass

            logger.info(f"Retrieved {bundle.get('total', 0)} conditions for patient {patient_id}")
            return bundle
        except Exception as e:
            logger.error(f"Error fetching conditions for {patient_id}: {str(e)}")
            return {"entry": []}

    @staticmethod
    def get_related_persons(patient_id: str, params: Dict = None) -> dict:
        import httpx
        try:
            key = f"related:{patient_id}:{str(params)}"
            try:
                from packages.backend.app.services.cache import cache
                cached = cache.get(key)
                if cached:
                    logger.info(f"Cache hit for related persons {patient_id}")
                    return cached
            except Exception:
                cached = None

            query = MockHealthService._build_url("RelatedPerson")
            query_params = {"patient": patient_id}
            if params:
                query_params.update(params)

            headers = MockHealthService._get_headers()

            with httpx.Client(timeout=5.0) as client:
                response = client.get(query, params=query_params, headers=headers)
                response.raise_for_status()

            bundle = response.json()

            try:
                from packages.backend.app.services.cache import cache
                cache.set(key, bundle, FHIRService.TTL_RELATED)
            except Exception:
                pass

            logger.info(f"Retrieved {bundle.get('total', 0)} related persons for patient {patient_id}")
            return bundle
        except Exception as e:
            logger.error(f"Error fetching related persons for {patient_id}: {str(e)}")
            return {"entry": []}

