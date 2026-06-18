# 🌿 Plant Specimen MGRS Validator

An AI-powered web application designed for herbarium curators, taxonomists, and botanists to automate the extraction, validation, and verification of geographic data from plant specimen labels.

The application uses Optical Character Recognition (OCR), Large Language Models (LLMs), geocoding services, and MGRS coordinate calculations to detect discrepancies between locality information recorded on specimen labels and the associated Military Grid Reference System (MGRS) coordinates.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Workflow](#workflow)
- [Example Output](#example-output)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Herbarium specimen labels often contain valuable geographic information recorded as free-form text. Manual transcription and validation of this data can be time-consuming and prone to errors.

**Plant Specimen MGRS Validator** automates this process by:

1. Extracting text from specimen images.
2. Parsing locality information using an LLM.
3. Geocoding the extracted locality description.
4. Calculating the corresponding MGRS coordinates.
5. Comparing calculated coordinates with the MGRS recorded on the specimen label.
6. Flagging inconsistencies for curator review.

This helps improve data quality in biodiversity collections and reduces manual verification effort.

---

## Features

### 🔍 Automated OCR

Extracts text directly from herbarium specimen photographs using **Tesseract.js**.

### 🤖 AI-Powered Data Parsing

Uses **Qwen LLM** (via MuleRouter API) to transform unstructured OCR text into structured specimen metadata:

- Scientific Name
- Locality Description
- MGRS Coordinate
- Collection Date
- Collector Name

### 📍 Smart Geocoding

Interprets locality descriptions and converts them into precise geographic coordinates.

Examples:

- "2 km north of Hindi prison"
- "Near Tana River bridge"
- "5 miles west of Garissa town"

### 🗺️ MGRS Validation

Calculates the expected MGRS coordinate from geocoded latitude/longitude values and compares it with the label-recorded MGRS.

Validation includes:

- 100 km grid square comparison
- Coordinate consistency checks
- Error flagging and discrepancy reporting

### 🔒 Secure Backend Proxy

A Flask backend securely manages API requests, protects API keys, and avoids browser CORS limitations.

---

## Architecture

```text
Specimen Image
      │
      ▼
Tesseract.js OCR
      │
      ▼
Extracted Text
      │
      ▼
Qwen LLM (MuleRouter)
      │
      ▼
Structured JSON
      │
      ▼
Geocoding Service
      │
      ▼
Latitude / Longitude
      │
      ▼
MGRS Conversion
      │
      ▼
Validation Engine
      │
      ▼
Error Report / Verification Result
```

---

## Tech Stack

### Frontend

- HTML5
- Tailwind CSS
- Vanilla JavaScript
- Tesseract.js

### Backend

- Python
- Flask
- Flask-CORS
- Requests

### AI & APIs

- MuleRouter API
- Qwen Large Language Model
- OpenStreetMap Nominatim Geocoding API

### Geographic Processing

- MGRS Coordinate Conversion Libraries
- Geospatial Validation Logic

---

## Installation

### Prerequisites

- Python 3.9+
- pip
- Modern web browser
- MuleRouter API key

### Clone the Repository

```bash
git clone https://github.com/yourusername/plant-specimen-mgrs-validator.git

cd plant-specimen-mgrs-validator
```

### Create Virtual Environment

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/macOS

```bash
source venv/bin/activate
```

### Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### Start Flask Server

```bash
python app.py
```

Server will run on:

```text
http://localhost:5000
```

### Launch Frontend

Open:

```text
index.html
```

or serve via:

```bash
python -m http.server 8000
```

Then browse to:

```text
http://localhost:8000
```

---

## Configuration

Create a `.env` file in the project root:

```env
MULEROUTER_API_KEY=your_api_key_here
```

Example Flask configuration:

```python
import os

API_KEY = os.getenv("MULEROUTER_API_KEY")
```

**Important:** Never expose API keys in frontend JavaScript.

---

## Usage

### Step 1: Upload Specimen Image

Upload a herbarium specimen photograph containing label information.

### Step 2: OCR Processing

The application extracts text from the image using Tesseract.js.

### Step 3: Metadata Extraction

Qwen parses the OCR output into structured specimen data.

### Step 4: Geocoding

The locality description is converted into geographic coordinates.

### Step 5: MGRS Validation

The system calculates the expected MGRS coordinate and compares it with the recorded value.

### Step 6: Review Results

The application displays:

- Extracted metadata
- Geocoded coordinates
- Calculated MGRS
- Recorded MGRS
- Validation status
- Error flags

---

## Workflow

### Input Label Text

```text
Acacia tortilis

Kenya, Lamu County
2 km north of Hindi Prison

MGRS: 37MBV1234567890

Collector: J. Smith
Date: 12 May 1985
```

### Parsed Output

```json
{
  "species": "Acacia tortilis",
  "locality": "2 km north of Hindi Prison, Lamu County, Kenya",
  "mgrs_recorded": "37MBV1234567890",
  "collector": "J. Smith",
  "date": "1985-05-12"
}
```

### Validation Result

```json
{
  "latitude": -2.12345,
  "longitude": 40.56789,
  "mgrs_calculated": "37MBU1235567891",
  "mgrs_recorded": "37MBV1234567890",
  "status": "MISMATCH",
  "warning": "100km grid square identifier differs"
}
```

---

## Example Output

| Field | Value |
|---------|---------|
| Species | Acacia tortilis |
| Locality | 2 km north of Hindi Prison |
| Latitude | -2.12345 |
| Longitude | 40.56789 |
| Recorded MGRS | 37MBV1234567890 |
| Calculated MGRS | 37MBU1235567891 |
| Status | ❌ Mismatch |

---



---

## Dependencies

### Backend

```text
Flask
Flask-CORS
Requests
python-dotenv
mgrs
```

### Frontend

```text
Tesseract.js
Tailwind CSS
```

---

## Troubleshooting

### OCR Produces Poor Results

- Use high-resolution specimen photographs.
- Ensure labels are clearly visible.
- Improve image contrast before upload.

### Geocoding Fails

- Verify locality descriptions contain sufficient geographic detail.
- Check internet connectivity.
- Confirm Nominatim service availability.

### Invalid MGRS Conversion

- Verify recorded MGRS format.
- Ensure coordinate conversion library is installed correctly.
- Confirm geocoding returned valid coordinates.

### API Errors

- Verify MuleRouter API key.
- Check Flask backend logs.
- Ensure proxy server is running.

---

## Future Enhancements

- Batch specimen processing
- Interactive map visualization
- Confidence scoring for geocoding results
- Multiple geocoding provider support
- Darwin Core export support
- Herbarium database integration
- CSV and Excel report generation
- User authentication and audit logging

---

## Contributing

Contributions are welcome.

To contribute:

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit changes

```bash
git commit -m "Add new feature"
```

4. Push branch

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) [YEAR]

Permission is hereby granted, free of charge,
to any person obtaining a copy of this software...
```

See the LICENSE file for full details.

---

### Acknowledgements

- OpenStreetMap Nominatim
- Tesseract.js OCR Project
- Qwen Large Language Models
- Flask Community
- Herbarium and biodiversity informatics practitioners who inspired this workflow
