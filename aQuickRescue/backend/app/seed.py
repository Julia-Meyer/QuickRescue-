from main import PatientProfile, SessionLocal  # Importiert deine Klasse und DB-Session
from faker import Faker
import random

fake = Faker("de_DE")


def seed_patients(n=100):
    db = SessionLocal()
    print(f"Generiere {n} PatientProfile-Einträge...")

    for _ in range(n):
        # Passe diese Felder an deine Spalten in PatientProfile an!
        patient = PatientProfile(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            allergies=random.choice(["Keine", "Penicillin", "Nüsse", "Ibuprofen"]),
            medications="Metoprolol 50mg (1x täglich), ASS 100 (1x täglich)",
            conditions="Bluthochdruck",
            gp_name="Dr. med. " + fake.last_name(),
            gp_phone=fake.phone_number(),
            emergency_contact_phone="+49 17656781893"
        )
        db.add(patient)

    db.commit()
    db.close()
    print("Datenbank erfolgreich gefüttert! 🎉")


if __name__ == "__main__":
    seed_patients(100)
    #