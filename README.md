# Supplemental Report Generation (cr180b_2)

This project automates the process of filling out the North Carolina Victim Notification Request PDF form (cr180b_2.pdf) using data pulled from a Supabase database and Azure OpenAI for intelligent field mapping.

## What does this code do?

- **Connects to Supabase**: Retrieves data from multiple tables related to a police report (e.g., property items, reports, crime incidents, persons involved, suspects, offenders, drug items, vehicles involved).
- **Maps Data to PDF Fields**: Uses Azure OpenAI to intelligently map database values to the required PDF fields, handling data types (strings, booleans, dates, phone numbers) and formatting as needed.
- **Fills and Flattens PDF**: Overlays the mapped data onto the official PDF template, then flattens the PDF to make it non-editable.
- **Outputs a Ready-to-Use PDF**: Saves the completed, non-editable PDF to the `PDF_Output` directory.

## How does PDF mapping work?

- The code defines a `field_map_template` that describes the expected data type for each PDF field (e.g., string, boolean, date).
- A `field_map` dictionary links these logical field names to the actual PDF form field names.
- Data from the database is processed and mapped to these fields using Azure OpenAI, ensuring correct formatting and type conversion.
- The overlay is generated using ReportLab, and merged with the original PDF using pdfrw.

## Quickstart

1. **Clone this repository**
2. **Install dependencies**:

```bash
pip install -r req.txt
```

3. **Set up your environment**:
   - Ensure you have valid Supabase and Azure OpenAI credentials (see code for where to set keys).
   - Place your PDF templates in the `PDF_Template` directory.

4. **Run the script**:

```bash
python fillPDF_cr180b_2.py
```

5. **Find your output**:
   - The filled, non-editable PDF will be saved in the `PDF_Output` directory.

## Requirements
See `req.txt` for all required Python packages.

## Notes
- The code is designed for the North Carolina Victim Notification Request form (cr180b_2.pdf), but can be adapted for other forms by updating the field maps and template.
- Ensure your Supabase and Azure OpenAI credentials are kept secure.
