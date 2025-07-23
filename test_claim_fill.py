
import streamlit as st
import pandas as pd
from openai import OpenAI
import mock_pms

# --- Load Data ---
cdt_df = pd.read_csv("C:\\Users\\satis\\PycharmProjects\\Complete_workflow\\CDT_AI_Training_100_New_Rows.csv")
claim_df = pd.read_csv("C:\\Users\\satis\\PycharmProjects\\Complete_workflow\\cdt_claim_fields.csv")
patients = mock_pms.get_mock_patients()

api_key = st.secrets.get("OPENROUTER_API_KEY")
if not api_key:
    st.error("❌ OpenRouter API key not found in secrets. Please check your `.streamlit/secrets.toml` file.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")
MODEL = "mistralai/mistral-7b-instruct"

# --- Session State ---
if "selected_cdt_code" not in st.session_state:
    st.session_state.selected_cdt_code = None
if "suggestion_confirmed" not in st.session_state:
    st.session_state.suggestion_confirmed = False
if "last_suggestion" not in st.session_state:
    st.session_state.last_suggestion = ""
if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = None

# --- UI Header ---
st.title("CDT Code + ADA Claim Assistant")

# --- Patient Selection ---
selected_name = st.selectbox("Select Patient", patients["Name"].tolist())
patient = patients[patients["Name"] == selected_name].iloc[0]
st.session_state.selected_patient = patient

# --- CDT Suggestion Phase ---
if not st.session_state.suggestion_confirmed:
    st.subheader("Step 1: CDT Code Suggestion")
    st.subheader(f"Patient Clinical Info")

    clinical_df = pd.DataFrame({
        "Field": [
            "Patient Name", "DOB", "Gender",
            "Tooth Number", "Surface", "Clinical Note",
            "Treatment"
        ],
        "Value": [
            str(patient["Name"]),
            str(patient["DOB"]),
            str(patient["Gender"]),
            str(patient["Tooth Number"]),
            str(patient["Surface"]),
            str(patient["Clinical Notes"]),
            str(patient["Procedure"]),
        ]
    })

    st.dataframe(clinical_df, use_container_width=True, hide_index=True)

    clinical_note = patient["Clinical Notes"]
    tooth_number = patient["Tooth Number"]
    surface = patient["Surface"]

    if st.button("Suggest CDT Code"):
        prompt = f"""You are a CDT coding assistant. Given the clinical note, suggest the most accurate CDT code.

Clinical Note: {clinical_note}
Tooth Number: {tooth_number}
Surface: {surface}

Return format:
CDT Code: <code>
Reason: <why this fits>
"""
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful CDT coding assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            suggestion = response.choices[0].message.content.strip()
            st.session_state.last_suggestion = suggestion
            if "CDT Code:" in suggestion:
                code = suggestion.split("CDT Code:")[1].strip().split()[0]
                st.session_state.selected_cdt_code = code

            st.success("Suggested CDT Code")
            st.markdown(f"```\n{suggestion}\n```")
        except Exception as e:
            st.error(f"❌ Could not generate a suggestion.\n\n{e}")

    if st.session_state.last_suggestion:
        st.info("Do you want to continue with the suggested code?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, continue"):
                st.session_state.suggestion_confirmed = True
        with col2:
            if st.button("🔁 Start Over"):
                st.session_state.selected_cdt_code = None
                st.session_state.last_suggestion = ""
                st.session_state.suggestion_confirmed = False

# --- ADA Form Phase ---
if st.session_state.suggestion_confirmed:
    st.subheader("Step 2: Auto-Filled ADA Claim Form")

    # Map patient data to claim fields
    field_data = {}
    for _, row in claim_df.iterrows():
        field = row["Field Name"]
        instr = row["Instructions"]
        field_lower = field.strip().lower()

        # Matching known fields with mock patient data
        if "cdt code" in field_lower or "procedure code" in field_lower:
            value = st.session_state.selected_cdt_code
        elif "patient name" in field_lower:
            value = patient["Name"]
        elif "relationship" in field_lower:
            value = patient["Relationship"]
        elif "patient date of birth" in field_lower:
            value = patient["DOB"]
        elif "gender" in field_lower:
            value = patient["Gender"]
        elif "address" in field_lower and "billing" not in field_lower:
            value = patient["Address"]
        elif "subscriber name" in field_lower:
            value = patient["Subscriber Name"]
        elif "subscriber id" in field_lower:
            value = patient["Subscriber ID"]
        elif "tooth number" in field_lower:
            value = patient["Tooth Number"]
        elif "surface" in field_lower:
            value = patient["Surface"]
        elif "fee" in field_lower:
            value = patient["Fee"]
        elif "address" in field_lower and "billing" in field_lower:
            value = patient["Address"]
        elif "treating dentist" in field_lower:
            value = patient["Subscriber Name"]  # Placeholder
        elif "phone number" in field_lower:
            value = "555-123-4567"  # Dummy placeholder
        else:
            value = ""  # Leave blank for manual input

        field_data[field] = value

    # Show editable fields
    edited_fields = {}
    for field, value in field_data.items():
        edited_fields[field] = st.text_input(field, value=value)

    # CSV Download Button
    if st.button("📥 Generate Claim CSV", key="generate_csv_button"):
        claim_output_df = pd.DataFrame([edited_fields])
        csv_path = "filled_ada_claim.csv"
        claim_output_df.to_csv(csv_path, index=False)

        with open(csv_path, "rb") as f:
            st.download_button("Download ADA Claim CSV", f, file_name="filled_ada_claim.csv", mime="text/csv",
                               key="download_csv_button")

    if st.button("🔁 Start Over", key="restart_button"):
        st.session_state.suggestion_confirmed = False
        st.session_state.selected_cdt_code = None
        st.session_state.last_suggestion = ""


