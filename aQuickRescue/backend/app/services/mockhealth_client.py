"""
Mock.Health API Client
Direct integration with mock.health FHIR API
Based on the user's provided code snippet
"""

import os
import requests
import logging
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env/env.mockhealth")

logger = logging.getLogger(__name__)

class MockHealthClient:
    """Direct client for Mock.Health FHIR API"""

    def __init__(self):
        """Initialize with Mock.Health credentials"""
        self.api_key = os.getenv("MOCK_HEALTH_API_KEY")
        self.api_url = os.getenv("MOCK_HEALTH_API_URL", "https://api.mock.health")
        self.fhir_url = os.getenv("MOCK_HEALTH_FHIR_URL", "https://api.mock.health/fhir")

        if not self.api_key:
            logger.warning("MOCK_HEALTH_API_KEY not set - Mock.Health API calls may fail")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        }

    def search_patients(self, given: Optional[str] = None, family: Optional[str] = None,
                       birthdate: Optional[str] = None) -> dict:
        """
        Search for patients on Mock.Health FHIR server

        Args:
            given: Patient given name (first name)
            family: Patient family name (last name)
            birthdate: Patient date of birth (YYYY-MM-DD)

        Returns:
            FHIR Bundle or dict with error info
        """
        try:
            params = {}
            if given:
                params["given"] = given
            if family:
                params["family"] = family
            if birthdate:
                params["birthdate"] = birthdate

            url = f"{self.fhir_url}/Patient"
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            bundle = response.json()
            total = bundle.get("total", 0)
            logger.info(f"Found {total} patients matching criteria")

            return bundle
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return {"resourceType": "Bundle", "total": 0, "entry": [], "error": str(e)}

    def get_patient(self, patient_id: str) -> dict:
        """
        Get single patient by ID

        Args:
            patient_id: FHIR Patient ID

        Returns:
            FHIR Patient resource
        """
        try:
            url = f"{self.fhir_url}/Patient/{patient_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            patient = response.json()
            logger.info(f"Retrieved patient {patient_id}")
            return patient
        except Exception as e:
            logger.error(f"Error fetching patient {patient_id}: {str(e)}")
            return {"error": str(e)}

    def get_medication_statements(self, patient_id: str) -> dict:
        """
        Get medication statements for a patient

        Args:
            patient_id: FHIR Patient ID (or reference like "Patient/123")

        Returns:
            FHIR Bundle of MedicationStatement resources
        """
        try:
            # Normalize patient reference
            if not patient_id.startswith("Patient/"):
                patient_id = f"Patient/{patient_id}"

            url = f"{self.fhir_url}/MedicationStatement"
            params = {"patient": patient_id}
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            bundle = response.json()
            total = bundle.get("total", 0)
            logger.info(f"Found {total} medication statements for patient {patient_id}")

            return bundle
        except Exception as e:
            logger.error(f"Error fetching medication statements: {str(e)}")
            return {"resourceType": "Bundle", "total": 0, "entry": [], "error": str(e)}

    def get_allergies(self, patient_id: str) -> dict:
        """
        Get allergies for a patient

        Args:
            patient_id: FHIR Patient ID

        Returns:
            FHIR Bundle of AllergyIntolerance resources
        """
        try:
            if not patient_id.startswith("Patient/"):
                patient_id = f"Patient/{patient_id}"

            url = f"{self.fhir_url}/AllergyIntolerance"
            params = {"patient": patient_id}
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            bundle = response.json()
            total = bundle.get("total", 0)
            logger.info(f"Found {total} allergies for patient {patient_id}")

            return bundle
        except Exception as e:
            logger.error(f"Error fetching allergies: {str(e)}")
            return {"resourceType": "Bundle", "total": 0, "entry": [], "error": str(e)}

    def get_conditions(self, patient_id: str) -> dict:
        """
        Get conditions (diagnoses) for a patient

        Args:
            patient_id: FHIR Patient ID

        Returns:
            FHIR Bundle of Condition resources
        """
        try:
            if not patient_id.startswith("Patient/"):
                patient_id = f"Patient/{patient_id}"

            url = f"{self.fhir_url}/Condition"
            params = {"patient": patient_id}
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            bundle = response.json()
            total = bundle.get("total", 0)
            logger.info(f"Found {total} conditions for patient {patient_id}")

            return bundle
        except Exception as e:
            logger.error(f"Error fetching conditions: {str(e)}")
            return {"resourceType": "Bundle", "total": 0, "entry": [], "error": str(e)}

    def get_related_persons(self, patient_id: str) -> dict:
        """
        Get related persons (emergency contacts) for a patient

        Args:
            patient_id: FHIR Patient ID

        Returns:
            FHIR Bundle of RelatedPerson resources
        """
        try:
            if not patient_id.startswith("Patient/"):
                patient_id = f"Patient/{patient_id}"

            url = f"{self.fhir_url}/RelatedPerson"
            params = {"patient": patient_id}
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            bundle = response.json()
            total = bundle.get("total", 0)
            logger.info(f"Found {total} related persons for patient {patient_id}")

            return bundle
        except Exception as e:
            logger.error(f"Error fetching related persons: {str(e)}")
            return {"resourceType": "Bundle", "total": 0, "entry": [], "error": str(e)}

    def get_diagnostic_reports(self, patient_id: str, category: Optional[str] = None) -> dict:
        """
        Get diagnostic reports for a patient (as shown in user's
        code snippet - radiology reports with category=RAD)

        Args:
            patient_id: FHIR Patient ID
            category: Optional category filter (e.g., "RAD" for radiology)

        Returns:
            FHIR Bundle of DiagnosticReport resources
        """
        try:
            if not patient_id.startswith("Patient/"):
                patient_id = f"Patient/{patient_id}"

            url = f"{self.fhir_url}/DiagnosticReport"
            params = {"patient": patient_id}
            if category:
                params["category"] = category

            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            bundle = response.json()
            total = bundle.get("total", 0)
            logger.info(f"Found {total} diagnostic reports for patient {patient_id} (category={category})")

            return bundle
        except Exception as e:
            logger.error(f"Error fetching diagnostic reports: {str(e)}")
            return {"resourceType": "Bundle", "total": 0, "entry": [], "error": str(e)}


# Convenience function (mimics the user's code snippet execution)
def demo_search_and_load():
    """
    Demonstration function - matches the user's provided code snippet
    1. Search for patients
    2. Get first patient's diagnostic reports
    """
    client = MockHealthClient()

    # Search patients
    bundle = client.search_patients()
    total = bundle.get("total", 0)
    print(f"Found {total} patients")

    entries = bundle.get("entry", [])

    if not entries:
        print("No patients found.")
        return

    # Get first patient
    patient_id = entries[0]["resource"]["id"]
    print(f"First patient ID: {patient_id}")

    # Get radiology reports
    reports = client.get_diagnostic_reports(patient_id, category="RAD")
    print(f"Found {reports.get('total', 0)} radiology reports")

    return {"patient_id": patient_id, "reports": reports}


if __name__ == "__main__":
    # Run demo
    result = demo_search_and_load()
    if result:
        print(f"\nDemo completed. Patient ID: {result['patient_id']}")

