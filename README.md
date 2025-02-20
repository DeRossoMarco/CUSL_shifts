# CUSL Shifts - Weekly Shift Generator

A Python application for generating and managing weekly shifts for CUSL.

## Features

- Automatic weekly shift generation
- GUI for viewing and modifying shifts
- CSV availability import
- Configurable minimum and maximum people per shift
- Save shifts as image

## Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)
- Pillow (PIL) for image generation

## Installation

1. Clone the repository or download the files
2. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Usage

1. Prepare a CSV file with availabilities in the required format:
   - First column: "Name"
   - Following columns: see structure.csv
   - Use "SI" to indicate availability

2. Launch the application:
   ```bash
   python3 Turni_CUSL.py
   ```

3. In the configuration window:
   - Set minimum and maximum people per shift
   - Select the CSV availability file
   - Choose to view availabilities only or generate shifts

4. In the main window:
   - Edit shifts using checkboxes
   - View unassigned people
   - Regenerate shifts with "Ricalcola" button
   - Save shifts as image

## CSV Format

Example CSV structure:
```csv
Nome,lunedi_m,lunedi_pr,lunedi_po,martedi_m,...
Mario,SI,,SI,,...
Laura,,SI,SI,SI,...
```

## Notes

- Shifts are generated respecting minimum and maximum people per shift
- System automatically assigns people avoiding overlaps
- Interface shows colored indicators for shift validity:
  - Green: valid shift
  - Yellow: below minimum required
  - Red: above maximum allowed