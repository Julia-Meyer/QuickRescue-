"""
FHIR Importer CLI

Usage examples:

# Import resources for all patients (paginated) - defaults to first 100 patients
python -m app.scripts.fhir_importer --resources Patient AllergyIntolerance MedicationDispense Observation Condition Procedure --limit 100

# Import for a single patient
python -m app.scripts.fhir_importer --patient pat-001 --resources Patient AllergyIntolerance MedicationDispense

The script uses the existing `get_fhir_client()` from `app.services.fhir_client`.
"""

import asyncio
import argparse
import os
import json
from typing import List
from app.services.fhir_client import get_fhir_client
import logging

logger = logging.getLogger("fhir_importer")
logging.basicConfig(level=logging.INFO)

OUTPUT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "fhir_exports")

DEFAULT_RESOURCES = [
    "Patient",
    "AllergyIntolerance",
    "MedicationDispense",
    "Medication",
    "Observation",
    "Condition",
    "Procedure",
]


async def fetch_patient_list(client, limit: int = 100, offset: int = 0) -> List[str]:
    """Fetch list of patient IDs using FHIR search with pagination"""
    patient_ids = []
    current_offset = offset

    while True:
        logger.info(f"Searching patients _count={limit} _offset={current_offset}")
        bundle = await client.search("Patient", **{"_count": limit, "_offset": current_offset})
        entries = bundle.get("entry", []) if isinstance(bundle, dict) else []

        if not entries:
            break

        for entry in entries:
            resource = entry.get("resource", {})
            pid = resource.get("id")
            if pid:
                patient_ids.append(pid)

        # If returned less than requested, end
        if len(entries) < limit:
            break

        current_offset += limit

    return patient_ids


async def fetch_and_save_resource(client, resource_type: str, params: dict, out_path: str):
    """Fetch resource (search) and save JSON to out_path"""
    try:
        logger.info(f"Fetching {resource_type} with params {params}")
        data = await client.search(resource_type, **params)
    except Exception as e:
        logger.error(f"Error fetching {resource_type}: {e}")
        data = {"error": str(e)}

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {resource_type} -> {out_path}")


async def fetch_and_save_single_resource(client, resource_type: str, resource_id: str, out_path: str):
    """Fetch single resource by id and save"""
    try:
        logger.info(f"Getting {resource_type}/{resource_id}")
        data = await client.get_resource(resource_type, resource_id)
    except Exception as e:
        logger.error(f"Error getting {resource_type}/{resource_id}: {e}")
        data = {"error": str(e)}

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {resource_type}/{resource_id} -> {out_path}")


async def import_for_patient(client, patient_id: str, resources: List[str], out_root: str):
    """Import selected resources for a single patient and save under out_root/patient_id/"""
    patient_dir = os.path.join(out_root, patient_id)
    os.makedirs(patient_dir, exist_ok=True)

    # Always save Patient resource
    await fetch_and_save_single_resource(client, "Patient", patient_id, os.path.join(patient_dir, "Patient.json"))

    # For each resource, search by patient reference
    tasks = []
    for res in resources:
        if res == "Patient":
            continue
        # For Medication resource we may need to resolve references; still do a search for Medication where possible
        params = {"patient": f"Patient/{patient_id}", "_count": 200}
        out_file = os.path.join(patient_dir, f"{res}.json")
        tasks.append(fetch_and_save_resource(client, res, params, out_file))

    await asyncio.gather(*tasks)


async def import_all_patients(client, resources: List[str], limit: int, offset: int, out_root: str):
    patient_ids = await fetch_patient_list(client, limit=limit, offset=offset)
    logger.info(f"Found {len(patient_ids)} patients to import")

    for pid in patient_ids:
        await import_for_patient(client, pid, resources, out_root)


def parse_args():
    parser = argparse.ArgumentParser(description="FHIR Importer CLI")
    parser.add_argument("--patient", type=str, help="FHIR Patient ID to import (optional)")
    parser.add_argument("--resources", type=str, nargs="+", default=DEFAULT_RESOURCES,
                        help="List of FHIR resources to import (default: all core resources)")
    parser.add_argument("--limit", type=int, default=100, help="Page size for patient search (default: 100)")
    parser.add_argument("--offset", type=int, default=0, help="Start offset for patient search (default: 0)")
    parser.add_argument("--out", type=str, default=OUTPUT_ROOT, help="Output root directory for exports")
    return parser.parse_args()


def main():
    args = parse_args()
    client = get_fhir_client()

    resources = args.resources
    out_root = os.path.abspath(args.out)
    os.makedirs(out_root, exist_ok=True)

    if args.patient:
        asyncio.run(import_for_patient(client, args.patient, resources, out_root))
    else:
        asyncio.run(import_all_patients(client, resources, args.limit, args.offset, out_root))

    logger.info("FHIR import completed")


if __name__ == "__main__":
    main()

