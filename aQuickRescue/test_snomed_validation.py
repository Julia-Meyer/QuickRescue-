#!/usr/bin/env python3
"""
Manual test to validate SNOMED CT code mapping in fhir_allergy.py
"""

import sys
import json
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "backend"))

def test_snomed_config_loading():
    """Test that SNOMED config loads correctly"""
    from app.services.fhir_allergy import _load_snomed_config

    print("=" * 70)
    print("Test 1: Loading SNOMED Configuration")
    print("=" * 70)

    config = _load_snomed_config()

    assert config is not None, "Config should not be None"
    assert "snomed_system" in config, "Config should have snomed_system"
    assert config["snomed_system"] == "http://snomed.info/sct", "System URL should match"
    assert "critical_codes" in config, "Config should have critical_codes"
    assert "critical_reaction_codes" in config, "Config should have critical_reaction_codes"

    print("✓ Config loaded successfully")
    print(f"✓ SNOMED System: {config['snomed_system']}")
    print(f"✓ Critical code categories: {len(config['critical_codes'])}")
    print(f"✓ Critical reaction codes: {len(config['critical_reaction_codes'])}")
    print()


def test_snomed_penicillin_flag():
    """Test that penicillin allergy generates correct flags"""
    from app.services.fhir_allergy import _generate_critical_flags

    print("=" * 70)
    print("Test 2: Penicillin Allergy Flag Generation")
    print("=" * 70)

    # SNOMED 2670000 = Penicillin allergy
    penicillin_resource = {
        "resourceType": "AllergyIntolerance",
        "id": "allergy-001",
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",  # Explicit SNOMED system
                "code": "2670000",
                "display": "Penicillin allergy (disorder)"
            }]
        },
        "criticality": "high",
        "reaction": []
    }

    flags = _generate_critical_flags(penicillin_resource)

    assert "ANTIBIOTIC_ALLERGY_PENICILLIN" in flags, f"Expected flag not found. Got: {flags}"
    assert "CRITICAL_ALLERGY" in flags, f"Expected CRITICAL_ALLERGY. Got: {flags}"

    print(f"✓ Generated flags: {flags}")
    print(f"✓ Contains ANTIBIOTIC_ALLERGY_PENICILLIN: ✓")
    print(f"✓ Contains CRITICAL_ALLERGY: ✓")
    print()


def test_snomed_anaphylaxis_reaction():
    """Test that anaphylaxis reaction generates correct flags"""
    from app.services.fhir_allergy import _generate_critical_flags

    print("=" * 70)
    print("Test 3: Anaphylaxis Reaction Flag Generation")
    print("=" * 70)

    # SNOMED 39579001 = Anaphylaxis
    anaphylaxis_resource = {
        "resourceType": "AllergyIntolerance",
        "id": "allergy-002",
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "2670000",
                "display": "Penicillin allergy"
            }]
        },
        "criticality": "high",
        "reaction": [{
            "manifestation": [{
                "coding": [{
                    "system": "http://snomed.info/sct",  # Explicit SNOMED system
                    "code": "39579001",  # Anaphylaxis
                    "display": "Anaphylaxis"
                }]
            }],
            "severity": "severe",
            "onset": "1990-06-15"
        }]
    }

    flags = _generate_critical_flags(anaphylaxis_resource)

    assert "ANAPHYLAXIS_RISK" in flags, f"Expected ANAPHYLAXIS_RISK. Got: {flags}"
    assert "SEVERE_REACTION" in flags, f"Expected SEVERE_REACTION. Got: {flags}"

    print(f"✓ Generated flags: {flags}")
    print(f"✓ Contains ANAPHYLAXIS_RISK: ✓")
    print(f"✓ Contains SEVERE_REACTION: ✓")
    print()


def test_non_snomed_system_ignored():
    """Test that non-SNOMED codes are ignored"""
    from app.services.fhir_allergy import _generate_critical_flags

    print("=" * 70)
    print("Test 4: Non-SNOMED System Validation")
    print("=" * 70)

    # Using LOINC system (not SNOMED)
    non_snomed_resource = {
        "resourceType": "AllergyIntolerance",
        "id": "allergy-003",
        "code": {
            "coding": [{
                "system": "http://loinc.org",  # LOINC, NOT SNOMED
                "code": "2670000",
                "display": "Penicillin allergy"
            }]
        },
        "criticality": "high",
        "reaction": []
    }

    flags = _generate_critical_flags(non_snomed_resource)

    # Should NOT generate ANTIBIOTIC_ALLERGY_PENICILLIN since system is wrong
    assert "ANTIBIOTIC_ALLERGY_PENICILLIN" not in flags, \
        f"Should not generate SNOMED flag for non-SNOMED system. Got: {flags}"
    # But should still have CRITICAL_ALLERGY from criticality check
    assert "CRITICAL_ALLERGY" in flags, f"Should have CRITICAL_ALLERGY. Got: {flags}"

    print(f"✓ Generated flags: {flags}")
    print(f"✓ Correctly ignored non-SNOMED code mappings")
    print(f"✓ Still generated CRITICAL_ALLERGY from criticality field")
    print()


def test_latex_allergy_flag():
    """Test latex allergy flag generation"""
    from app.services.fhir_allergy import _generate_critical_flags

    print("=" * 70)
    print("Test 5: Latex Allergy Flag Generation")
    print("=" * 70)

    # SNOMED 294505007 = Latex allergy
    latex_resource = {
        "resourceType": "AllergyIntolerance",
        "id": "allergy-004",
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "294505007",
                "display": "Latex allergy"
            }]
        },
        "criticality": "low",
        "reaction": []
    }

    flags = _generate_critical_flags(latex_resource)

    assert "LATEX_ALLERGY" in flags, f"Expected LATEX_ALLERGY. Got: {flags}"

    print(f"✓ Generated flags: {flags}")
    print(f"✓ Contains LATEX_ALLERGY: ✓")
    print()


def test_multiple_categories():
    """Test that multiple flags can be generated for complex allergies"""
    from app.services.fhir_allergy import _generate_critical_flags

    print("=" * 70)
    print("Test 6: Multiple Flag Generation")
    print("=" * 70)

    resource = {
        "resourceType": "AllergyIntolerance",
        "id": "allergy-005",
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "2670000",  # Penicillin
                "display": "Penicillin allergy"
            }]
        },
        "criticality": "high",  # High criticality
        "reaction": [{
            "manifestation": [{
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "39579001",  # Anaphylaxis
                    "display": "Anaphylaxis"
                }]
            }],
            "severity": "severe"  # Severe reaction
        }]
    }

    flags = _generate_critical_flags(resource)

    assert "ANTIBIOTIC_ALLERGY_PENICILLIN" in flags
    assert "CRITICAL_ALLERGY" in flags
    assert "ANAPHYLAXIS_RISK" in flags
    assert "SEVERE_REACTION" in flags

    print(f"✓ Generated {len(flags)} flags: {flags}")
    print(f"✓ All expected flags present ✓")
    print()


if __name__ == "__main__":
    try:
        test_snomed_config_loading()
        test_snomed_penicillin_flag()
        test_snomed_anaphylaxis_reaction()
        test_non_snomed_system_ignored()
        test_latex_allergy_flag()
        test_multiple_categories()

        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nSummary:")
        print("✓ SNOMED configuration loads correctly")
        print("✓ SNOMED code mapping works as expected")
        print("✓ Explicit SNOMED system validation works")
        print("✓ Non-SNOMED codes are properly ignored")
        print("✓ Multiple flags can be generated simultaneously")
        print("\n✅ SNOMED CT integration is robust and production-ready!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

