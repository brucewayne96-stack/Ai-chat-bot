# AI-Health-Care-ChatBot

**A Tkinter-based Desktop Chatbot for Symptom Checking and Disease Information**

A local desktop chatbot that helps users identify possible conditions based on their symptoms, look up disease information, and book doctor appointments, all through a clean GUI with voice input support.

---

## Problem Statement

People often search for medical information online and get overwhelmed with inaccurate or irrelevant results. There's no simple, offline-friendly tool that lets users describe their symptoms conversationally and get structured, reliable information in return. This project addresses that by providing a lightweight desktop assistant backed by a structured medical database.

---

## Solution

1. User enters symptoms (text or voice) or a disease name
2. App matches symptoms against a JSON medical database
3. Top 3 most likely conditions are returned ranked by symptom match count
4. Each result includes a description and suggested care steps
5. Users can also look up any specific disease directly
6. A button opens an external appointment booking site

---

## Tech Stack

- **Language:** Python 3
- **GUI Framework:** Tkinter (ttk)
- **Database:** JSON (`medical_data.json`)
- **Voice Input:** SpeechRecognition (`speech_recognition`), Google Speech API
- **Threading:** Python `threading` (for non-blocking voice input)

---

## Features

* **Symptom Checker**
  Enter multiple symptoms separated by commas. The bot matches them against the database and returns the top 3 possible conditions, each with a match count, description, and suggested care.

* **Disease Info Lookup**
  Enter a disease name to get its description, symptoms, and care recommendations directly from the database.

* **Voice Input**
  Click the microphone button to speak your symptoms or query, recognized via Google Speech API and processed like typed input.

* **Book Appointment**
  Opens an external doctor appointment booking website in the browser.

* **Medical Disclaimer**
  Automatically appended after every symptom check result, reminding users to consult a real doctor.

* **External JSON Database**
  All 25 conditions are stored in `medical_data.json`, making it easy to add or update diseases without touching the code.

---

## Database

The app loads its data from `medical_data.json` at startup. It contains 25 conditions including:

Common Cold, Influenza, COVID-19, Pneumonia, Bronchitis, Migraine, Sinusitis, Food Poisoning, Gastroenteritis, Anemia, Strep Throat, Allergies, Asthma, GERD, IBS, UTI, Type 2 Diabetes, Hypertension, Eczema, Psoriasis, Arthritis, Muscle Strain, Conjunctivitis, Dehydration, and Tension Headache.

Each entry contains:
```json
{
  "display_name": "...",
  "description": "...",
  "care": "...",
  "symptoms": ["symptom_one", "symptom_two", ...]
}
```

To add a new condition, simply append a new entry to `medical_data.json` following the same structure.

---

## Architecture

```
User Input (Text / Voice)
        ↓
State Manager (NORMAL / CHECK_SYMPTOMS / DISEASE_INFO)
        ↓
Load medical_data.json → Build symptom-to-disease reverse map
        ↓
  Symptom Checker: match symptoms → rank diseases by count → return top 3
  Disease Lookup: direct key lookup → return info
        ↓
Tkinter Chat UI → render response with styled bubbles
```

---

## Installation & Usage

### 1. Install Dependencies

```bash
pip install SpeechRecognition
```

> Tkinter comes pre-installed with Python. No other external installs needed.

### 2. Place Files Together

Ensure both files are in the same directory:

```
project/
├── ai_chatbot.py
└── medical_data.json
```

### 3. Run the App

```bash
python ai_chatbot.py
```

### 4. Using the Chatbot

- Click **Symptom Checker** and type symptoms separated by commas:
  `fever, cough, fatigue`
- Click **Disease Info** and type a disease name:
  `migraine` or `type 2 diabetes`
- Click the **🎤 button** to use voice input instead
- Click **Book Appointment** to open the booking site

---

## Limitations

- Symptom matching is keyword-based, it does not understand natural language descriptions (e.g., "my head hurts" won't match `headache`).
- Voice input requires an active internet connection (Google Speech API).
- Not a substitute for professional medical advice.

---

## Future Improvements

- **NLP Input Parsing:** Use NLP to map natural language descriptions to symptom keywords.
- **Expanded Database:** Add more conditions and symptoms to improve coverage.
- **Severity Triage:** Ask follow-up questions to assess symptom severity before suggesting care.
- **Offline Voice Recognition:** Replace Google Speech API with a local model (e.g., Vosk) for offline use.
