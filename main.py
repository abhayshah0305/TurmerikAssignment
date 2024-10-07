import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import openai
import json
import time
import xml.etree.ElementTree as ET

# Define the namespace for parsing the XML file
namespaces = {'hl7': 'urn:hl7-org:v3'}

# ---- 1.Loading the patient data from the Synthea XML file ---- #
def load_patient_data(xml_path):
    """
    I'll parse the XML file and extract relevant patient data, such as patient ID, gender, birth date, and medications.

    Args:
        xml_path (str): Path to the XML file containing patient data.

    Returns:
        dict: I'll return a dictionary with the patient's information.
    """
    tree = ET.parse("patient1.xml")
    root = tree.getroot()

    #Extracting key patient information like ID, gender, and birthdate
    patient_id_element = root.find(".//hl7:patientRole/hl7:id", namespaces)
    patient_id = patient_id_element.attrib['extension'] if patient_id_element is not None else "Unknown"

    gender_element = root.find(".//hl7:administrativeGenderCode", namespaces)
    gender_code = gender_element.attrib.get('code', 'Unknown') if gender_element is not None else "Unknown"
    gender = 'Female' if gender_code == 'F' else 'Male' if gender_code == 'M' else 'Unknown'

    birth_date_element = root.find(".//hl7:birthTime", namespaces)
    birth_date = birth_date_element.attrib['value'][:8] if birth_date_element is not None else "Unknown"

    #Collecting the patient's medications to match later with clinical trials
    medications = []
    for med in root.findall(".//hl7:substanceAdministration", namespaces):
        med_name_element = med.find(".//hl7:manufacturedMaterial/hl7:name", namespaces)
        if med_name_element is not None:
            medications.append(med_name_element.text)

    # Now, I'll create and return a dictionary to store all the patient details
    patient_data = {
        "patientId": patient_id,
        "age": 2024 - int(birth_date[:4]) if birth_date != "Unknown" else "Unknown",
        "gender": gender,
        "conditions": medications,  # I'm assuming medications represent conditions for simplicity
        "medications": medications
    }

    return patient_data

# ---- 2. Let's scrape the clinical trials from ClinicalTrials.gov ---- #
def scrape_clinical_trials(condition="cancer"):
    """
    Here, I'll scrape clinical trials data from ClinicalTrials.gov based on a condition (default is "cancer").

    Args:
        condition (str): I'll search for clinical trials using this condition.

    Returns:
        list: I'll return a list of dictionaries with trial information (title, NCT number, status, conditions).
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(f"https://clinicaltrials.gov/ct2/results?cond={condition}&recrs=open")

    # I'm giving it time to fully load the page before scraping
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Now I'll extract the trial data from the table rows
    trials = []
    table_rows = soup.select("table tbody tr")

    for row in table_rows:
        study_title = row.select_one("td:nth-child(2)").get_text(strip=True)
        nct_number = row.select_one("td:nth-child(3)").get_text(strip=True)
        status = row.select_one("td:nth-child(4)").get_text(strip=True)
        conditions = row.select_one("td:nth-child(5)").get_text(strip=True)
        trials.append({
            "study_title": study_title,
            "nct_number": nct_number,
            "status": status,
            "conditions": conditions
        })

    # I'll close the browser after scraping
    driver.quit()
    return trials

# ---- 3. Check if the patient meets the trial's inclusion and exclusion criteria ---- #
def check_inclusion_criteria(trial, patient):
    """
    I’ll check if the patient meets the inclusion criteria for a given trial.

    Args:
        trial (dict): Information about the trial.
        patient (dict): The patient's details.

    Returns:
        list: A list of criteria that the patient met for this trial.
    """
    criteria_met = []

    # I’ll see if the patient’s condition matches any of the trial conditions
    if any(cond in trial['conditions'] for cond in patient['conditions']):
        criteria_met.append("Condition criteria met")

    return criteria_met if criteria_met else None

def check_exclusion_criteria(trial, patient):
    """
    Similarly, I'll check if the patient violates any exclusion criteria for the trial.

    Args:
        trial (dict): The trial's information.
        patient (dict): The patient's details.

    Returns:
        bool: True if the patient doesn't violate exclusion criteria; False otherwise.
    """
    # Right now, I assume no exclusion violations, but this can be extended later
    return True

# ---- 4. Generating an AI-based explanation for the match ---- #
def generate_explanation(patient, trial, inclusion_criteria):
    """
    I'll use GPT to generate an explanation for why the patient is matched to the trial.

    Args:
        patient (dict): The patient's information.
        trial (dict): The trial's details.
        inclusion_criteria (list): The inclusion criteria the patient met.

    Returns:
        str: The AI-generated explanation.
    """
    trial_info = f"Trial Name: {trial['study_title']}, NCT Number: {trial['nct_number']}, Conditions: {trial['conditions']}"
    patient_info = f"Patient age: {patient['age']}, Gender: {patient['gender']}, Conditions: {', '.join(patient['conditions'])}"

    prompt = f"Explain why this patient is matched to the trial based on the inclusion criteria met.\n\nPatient Info: {patient_info}\n\nTrial Info: {trial_info}\n\nInclusion Criteria Met: {', '.join(inclusion_criteria)}"

    # I’m asking GPT to generate an explanation based on the prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert clinical trial assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content'].strip()

# ---- 5. Matching the patient to eligible trials ---- #
def match_patient_to_trials(patient, trials):
    """
    I'll match the patient to trials based on the inclusion/exclusion criteria and also generate AI explanations for the matches.

    Args:
        patient (dict): The patient’s information.
        trials (list): A list of clinical trials.

    Returns:
        list: A list of matched trials, with AI explanations.
    """
    eligible_trials = []

    for trial in trials:
        inclusion_criteria_met = check_inclusion_criteria(trial, patient)
        exclusion_criteria_met = check_exclusion_criteria(trial, patient)

        if inclusion_criteria_met and exclusion_criteria_met:
            explanation = generate_explanation(patient, trial, inclusion_criteria_met)
            eligible_trials.append({
                "trialId": trial['nct_number'],
                "trialName": trial['study_title'],
                "eligibilityCriteriaMet": inclusion_criteria_met,
                "explanation": explanation  # Add the AI-generated explanation
            })

    return eligible_trials

# Set the wOpenAI API key, KEY REMOVED FOR SECREACY PURPOSES
openai.api_key = '#'

# ---- 6. summarizing the patient's history using AI ---- #
def summarize_patient_history(patient):
    """
    I'll summarize the patient’s medical history using GPT.

    Args:
        patient (dict): The patient's information.

    Returns:
        str: A brief summary of the patient’s medical history.
    """
    history = f"Patient is a {patient['age']} year old {patient['gender']}. "
    history += f"Conditions: {', '.join(patient['conditions'])}. "
    history += f"Medications: {', '.join(patient['medications'])}."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following patient history: {history}"}
        ]
    )

    return response['choices'][0]['message']['content'].strip()


# ---- 7. Let’s save the matched trials as JSON ---- #
def save_matched_trials_to_json(patient_id, matched_trials):
    """
    I'll save the matched trials to a JSON file.

    Args:
        patient_id (str): The patient’s ID.
        matched_trials (list): A list of matched trials.
    """
    output = {
        "patientId": patient_id,
        "eligibleTrials": matched_trials
    }

    with open("matched_trials.json", "w") as f:
        json.dump(output, f, indent=4)


def save_matched_trials_to_excel(patient_id, matched_trials):
    """
    Save the matched trials to an Excel file.

    Args:
        patient_id (str): The patient ID.
        matched_trials (list): A list of matched trials.
    """
    # Convert the matched trials to a DataFrame
    df = pd.DataFrame(matched_trials)

    # Save the DataFrame to an Excel file
    excel_file_path = f"{patient_id}_matched_trials.xlsx"
    df.to_excel(excel_file_path, index=False)

    print(f"Matched trials saved to {excel_file_path}")
    return excel_file_path


# ---- Main Execution ---- #
if __name__ == "__main__":
    # Load patient data from XML
    patient_data = load_patient_data('patient1.xml')

    # Scrape clinical trials
    trials = scrape_clinical_trials(condition="cancer")

    # Match patient to trials with AI-generated explanations
    matched_trials = match_patient_to_trials(patient_data, trials)

    # Save matched trials to JSON
    save_matched_trials_to_json(patient_data['patientId'], matched_trials)

    # Save matched trials to Excel
    save_matched_trials_to_excel(patient_data['patientId'], matched_trials)

    # Output summary and matched trials with explanations
    print(f"Patient Summary:\n{summarize_patient_history(patient_data)}")
    print(json.dumps(matched_trials, indent=4))


