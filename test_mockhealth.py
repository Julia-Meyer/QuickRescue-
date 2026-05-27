#!/usr/bin/env python3
"""
Mock.Health Integration Test Script
Run this to verify Mock.Health API connectivity and test the implementation
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test Mock.Health integration"""

    # Load env
    load_dotenv("env/env.mockhealth")

    api_key = os.getenv("MOCK_HEALTH_API_KEY")
    if not api_key:
        logger.error("❌ MOCK_HEALTH_API_KEY not set in env/env.mockhealth")
        return False

    logger.info("✅ Mock.Health API Key loaded")

    try:
        # Import client
        from app.services.mockhealth_client import MockHealthClient, demo_search_and_load
        logger.info("✅ MockHealthClient imported successfully")

        # Test 1: Demo function from user's code snippet
        logger.info("\n🔍 TEST 1: Running demo (patient search + diagnostic reports)")
        logger.info("=" * 60)

        result = demo_search_and_load()
        if result:
            logger.info(f"✅ Found patient: {result['patient_id']}")
            logger.info(f"✅ Diagnostic reports: {result['reports'].get('total', 0)}")
        else:
            logger.warning("⚠️  Demo returned no results (possibly no test data)")

        # Test 2: Direct client methods
        logger.info("\n🔍 TEST 2: Testing individual resource methods")
        logger.info("=" * 60)

        client = MockHealthClient()

        # Search
        logger.info("\nSearching for patients...")
        patients_bundle = client.search_patients(family="Smith")
        total = patients_bundle.get("total", 0)
        logger.info(f"✅ Patient search returned: {total} results")

        if total > 0:
            patient_id = patients_bundle["entry"][0]["resource"]["id"]
            logger.info(f"✅ Using patient ID: {patient_id}")

            # Get each resource type
            logger.info("\nFetching resources for patient...")

            meds = client.get_medication_statements(patient_id)
            logger.info(f"✅ MedicationStatement: {meds.get('total', 0)}")

            allergies = client.get_allergies(patient_id)
            logger.info(f"✅ AllergyIntolerance: {allergies.get('total', 0)}")

            conditions = client.get_conditions(patient_id)
            logger.info(f"✅ Condition: {conditions.get('total', 0)}")

            related = client.get_related_persons(patient_id)
            logger.info(f"✅ RelatedPerson: {related.get('total', 0)}")
        else:
            logger.warning("⚠️  No patients found for testing")

        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests passed!")
        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure you're running from project root with correct Python path")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

