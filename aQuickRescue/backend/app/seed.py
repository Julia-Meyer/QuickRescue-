from datetime import datetime, date, timezone
import random
from faker import Faker
from main import PatientProfile, SessionLocal  # Stelle sicher, dass der Import zu deiner main.py passt

fake = Faker("de_DE")

# Pools für eine realistische Durchmischung der medizinischen Daten
ALLERGIES_POOL = [
    "Penicillin", "Nüsse", "Ibuprofen", "Bienengift",
    "Laktoseintoleranz", "Latex allergy", "Kontrastmittel (Jod)"
]

MEDICATIONS_POOL = [
    "Metoprolol 50mg (1x täglich)",
    "ASS 100 (1x täglich)",
    "Ramipril 5mg (1x morgens)",
    "Metformin 1000mg (2x täglich)",
    "Pantoprazol 20mg (1x abends)",
    "Atorvastatin 20mg (1x abends)",
    "Salbutamol Spray (bei Bedarf)",
    "Ibuprofen 400mg (bei Schmerzen)"
]

CONDITIONS_POOL = [
    "Bluthochdruck (Hypertonie)",
    "Diabetes Typ 2",
    "Asthma bronchiale",
    "Hypercholesterinämie",
    "Vorhofflimmern",
    "Chronische Rückenschmerzen",
    "Koronare Herzkrankheit (KHK)"
]

# Geschlechter-Pool
GENDERS_POOL = ["Männlich", "Weiblich", "Divers"]


def seed_patients(n=100):
    db = SessionLocal()
    print(f"Generiere {n} komplett durchmischte PatientProfile-Einträge...")

    for i in range(n):
        # 1. Allergien durchmischen
        num_allergies = random.randint(1, 2)
        patient_allergies = ", ".join(random.sample(ALLERGIES_POOL, num_allergies)) if num_allergies > 0 else "Keine bekannt"

        # 2. Medikamente durchmischen
        num_meds = random.randint(1, 3)
        patient_meds = ", ".join(random.sample(MEDICATIONS_POOL, num_meds)) if num_meds > 0 else "Keine Dauermedikation"

        # 3. Vorerkrankungen durchmischen
        num_conditions = random.randint(0, 2)
        patient_conditions = ", ".join(random.sample(CONDITIONS_POOL, num_conditions)) if num_conditions > 0 else "Keine chronischen Erkrankungen"

        # 4. Geschlecht bestimmen und passenden Vornamen wählen
        patient_gender = random.choice(GENDERS_POOL)
        if patient_gender == "Männlich":
            first_name = fake.first_name_male()
        elif patient_gender == "Weiblich":
            first_name = fake.first_name_female()
        else:
            first_name = fake.first_name()

        # 5. Geburtsdatum als echtes, reines Python date-Objekt erzwingen
        pure_birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)
        if isinstance(pure_birth_date, str):
            pure_birth_date = datetime.strptime(pure_birth_date, "%Y-%m-%d").date()

        # PatientProfile-Objekt erstellen (abgestimmt auf dein aktualisiertes Modell)
        patient = PatientProfile(
            user_id=1,  # FEST auf 1 setzen, damit sie DEINEM neuen Benutzer gehören!
            fhir_patient_id=f"fhir-pat-{1000 + i}",
            first_name=first_name,
            last_name=fake.last_name(),
            date_of_birth=pure_birth_date,  # Garantiert ein Python date-Objekt
            blood_type=random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"]),
            gender=patient_gender,

            # Medizinische Daten
            allergies=patient_allergies,
            medications=patient_meds,
            conditions=patient_conditions,

            # Hausarzt-Daten
            gp_name="Dr. med. " + fake.last_name(),
            gp_phone=fake.phone_number(),

            # Notfallkontakt-Daten
            emergency_contact_name=fake.name(),
            emergency_contact_phone=fake.phone_number(),
            emergency_access_enabled=random.choice([True, False]),

            # Zeitstempel (Nutzt jetzt das moderne datetime.now mit UTC)
            created_at=fake.date_time_this_year(),
            updated_at=datetime.now(timezone.utc).replace(tzinfo=None)  # SQLite mag oft keine Zeitzonen-Objekte
        )
        db.add(patient)

    try:
        db.commit()
        print("✅ Datenbank erfolgreich mit durchmischten Daten gefüttert! 🎉")
    except Exception as e:
        print(f"❌ Fehler beim Speichern in der Datenbank: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_patients(300)