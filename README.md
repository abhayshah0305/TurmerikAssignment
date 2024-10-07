# Clinical Trial Matching Algorithm

This project implements a patient-to-clinical trial matching algorithm that scrapes clinical trial data from ClinicalTrials.gov, processes patient data from a Synthea XML file, and matches patients to trials based on inclusion/exclusion criteria. The project uses AI to generate explanations for the matches.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Features](#features)
- [File Descriptions](#file-descriptions)
- [Limitations](#limitations)
- [License](#license)

---

## Prerequisites

Before running this project, ensure that you have the following software installed:

- Python 3.10+
- `pip` (Python package installer)

### Python Libraries Required

Install the following libraries using `pip`:

```bash
pip install pandas requests beautifulsoup4 selenium webdriver-manager openai lxml
WebDriver
This project uses Selenium, so you need to install a browser driver (in this case, ChromeDriver):

bash
Copy code
pip install webdriver-manager
Ensure you have Google Chrome installed as this script uses ChromeDriver.

OpenAI API Key
You need an API key to access OpenAI's GPT models. Sign up at OpenAI and get your API key.

Set your OpenAI API key in the code by replacing 'your-openai-api-key' with your actual API key:

python
Copy code
openai.api_key = 'your-openai-api-key'
Setup
1. Clone the repository
First, clone the GitHub repository:

bash
Copy code
git clone https://github.com/yourusername/yourrepository.git
Navigate into the project directory:

bash
Copy code
cd yourrepository
2. Install Dependencies
Install all the required Python libraries by running:

bash
Copy code
pip install -r requirements.txt
If the requirements.txt file is not available, you can manually install the required libraries as shown in the Prerequisites section.

Usage
1. Load Patient Data and Match to Trials
To run the main script that loads patient data from patient1.xml, scrapes clinical trials from ClinicalTrials.gov, matches the patient to relevant trials, and generates AI-based explanations, run:

python main.py

2. Output
The program will generate the following outputs:
Matched Trials JSON: A JSON file named matched_trials.json will be created containing all the trials the patient is eligible for.
Matched Trials Excel: An Excel file named patientID_matched_trials.xlsx will be generated with the list of eligible trials.
Patient History Summary: The patient's summarized medical history will be printed to the terminal.

Example JSON structure:

{
    "patientId": "66e284dc-adc0-fce1-408f-4cdfa2a8e9e1",
    "eligibleTrials": [
        {
            "trialId": "NCT001",
            "trialName": "Sample Clinical Trial",
            "eligibilityCriteriaMet": ["Age criteria met", "No exclusion medications"],
            "explanation": "The patient meets the age criteria and does not have any exclusionary medications."
        }
    ]
}


Features
Patient Data Parsing: Extracts patient information (ID, age, gender, conditions, medications) from a C-CDA Synthea XML file.
Clinical Trial Scraping: Scrapes clinical trial data from ClinicalTrials.gov, filtering for trials actively recruiting patients.
Inclusion/Exclusion Criteria Matching: Matches patients to trials based on their conditions and medications.
AI-Powered Explanations: Uses OpenAI's GPT model to generate explanations for why a patient is eligible for certain trials.
JSON and Excel Output: Saves matched trials to JSON and Excel formats for easy access and review.

File Descriptions
main.py: The main script that performs the patient-to-clinical-trial matching and generates the output files.
patient1.xml: Example XML file containing synthetic patient data generated using Synthea.
matched_trials.json: Output JSON file that contains a list of clinical trials matched for the patient.
requirements.txt: Contains the Python dependencies required to run the project.

Limitations
Exclusion Criteria: Currently, exclusion criteria are a placeholder and not fully implemented. You can extend this feature as needed.
Data Source: The project scrapes clinical trials from ClinicalTrials.gov using Selenium, which may be slow or unreliable if the website's structure changes.
