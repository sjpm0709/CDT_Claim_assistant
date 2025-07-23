
import pandas as pd
import random

# Sample mock data
mock_patients = [
    {
        "PatientID": f"PMS00{i}",
        "Name": f"Patient {i}",
        "DOB": f"199{i}-0{i+1}-15",
        "Gender": random.choice(["Male", "Female"]),
        "ToothNumber": random.choice(["14", "22", "30", "3"]),
        "Surface": random.choice(["MO", "DO", "O", "MOD"]),
        "ClinicalNote": random.choice([
            "Patient has distal caries with pain on chewing.",
            "Old composite filling fractured, replacement needed.",
            "Deep occlusal decay noted during exam.",
            "Crown margin leaking, sensitivity present.",
            "Routine cleaning and checkup, no issues found.",
            "Patient complains of sensitivity on biting, fractured cusp suspected.",
            "Recurrent decay under old amalgam filling.",
            "Composite restoration worn out, needs replacement."
        ]),
        "TreatmentNote": random.choice([
            "Tooth requires composite restoration.",
            "Recommended crown placement after buildup.",
            "Simple occlusal composite sufficient.",
            "Scaling and polishing done.",
            "Consulted for fractured tooth restoration.",
            "Amalgam filling planned for deep decay.",
            "Tooth isolated and composite placed."
        ]),
        "Insurance": random.choice(["Aetna", "Cigna", "Delta Dental", "MetLife"]),
        "Provider": random.choice(["Dr. Smith", "Dr. Patel", "Dr. Johnson"])
    }
    for i in range(1, 11)
]

def generate_mock_patients_csv(file_path="mock_pms_patients.csv"):
    df = pd.DataFrame(mock_patients)
    df.to_csv(file_path, index=False)
    print(f"✅ Mock PMS patient data generated and saved at:\n{file_path}")

def get_mock_patients():
    return pd.read_csv("mock_pms_patients.csv")

if __name__ == "__main__":
    generate_mock_patients_csv()



