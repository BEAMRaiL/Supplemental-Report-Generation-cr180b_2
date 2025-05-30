# Supplemental Report Generation (cr180b_2)

This project automates the process of filling out the North Carolina Victim Notification Request PDF form (`cr180b_2.pdf`) using data pulled from a Supabase database and Azure OpenAI for intelligent field mapping.

## What does this code do?

- **Connects to Supabase**: Retrieves data from multiple tables related to a police report (e.g., property items, reports, crime incidents, persons involved, suspects, offenders, drug items, vehicles involved).
- **Maps Data to PDF Fields**: Uses Azure OpenAI to intelligently map database values to the required PDF fields, handling data types (strings, booleans, dates, phone numbers) and formatting as needed.
- **Fills and Flattens PDF**: Overlays the mapped data onto the official PDF template, then flattens the PDF to make it non-editable.
- **Outputs a Ready-to-Use PDF**: Saves the completed, non-editable PDF to the `PDF_Output` directory.

## PDF Template Location

- The template for the `cr180b_2` form is already included in the `PDF_Template` folder. **You do not need to add your own template**—it is provided and will always remain in this folder when you clone the repository.

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
   - Ensure you have valid Supabase and Azure OpenAI credentials (see below for best practices).
   - The PDF template is already present in the `PDF_Template` directory—no action needed.

4. **Run the script**:

```bash
python fillPDF_cr180b_2.py
```

5. **Find your output**:
   - The filled, non-editable PDF will be saved in the `PDF_Output` directory.

## Storing Credentials Securely

**Best Practice:** Store sensitive credentials (like API keys) in environment variables, not directly in your code. This keeps your secrets secure and makes it easier to manage different environments.

### Required Credentials (Internal Use Only)

This is a private internal repository. The following credentials are required and are already set up for internal use:

- **Supabase Key**
  - `SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml5dGtkdW9jdnR6enNhc2xwdGhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQyNTE5MDksImV4cCI6MjA1OTgyNzkwOX0.y202xCHsYxTOms68Dv3i7oxE8-e1STh6kQ_93KwwHj4"`
- **Azure OpenAI Key**
  - `AZURE_OPENAI_API_KEY = "AQNfwPlSoG1HUWTJCbFrGzZMOhz4PIHFKNIy5musPJYarskzydpnJQQJ99BEACYeBjFXJ3w3AAABACOGbAMx"`

You can find the current values for these keys in the codebase, but for best practice, you should move them to environment variables as described below.

### How to set environment variables (macOS/Linux/zsh):

```bash
export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml5dGtkdW9jdnR6enNhc2xwdGhsIiwicm9zZSI6ImFub24iLCJpYXQiOjE3NDQyNTE5MDksImV4cCI6MjA1OTgyNzkwOX0.y202xCHsYxTOms68Dv3i7oxE8-e1STh6kQ_93KwwHj4"
export AZURE_OPENAI_API_KEY="AQNfwPlSoG1HUWTJCbFrGzZMOhz4PIHFKNIy5musPJYarskzydpnJQQJ99BEACYeBjFXJ3w3AAABACOGbAMx"
```

You can add these lines to your `~/.zshrc` or `~/.bash_profile` to set them automatically on terminal startup.

### How to access environment variables in Python:

```python
import os
supabase_key = os.getenv("SUPABASE_KEY")
openai_key = os.getenv("AZURE_OPENAI_API_KEY")
```

**In the code, replace hardcoded keys with these variables:**

```python
supabase: Client = create_client(url, supabase_key)
openAIClient = AzureOpenAI(
    api_key=openai_key,
    ...
)
```

## Requirements
See `req.txt` for all required Python packages.

## Notes
- The code is designed for the North Carolina Victim Notification Request form (`cr180b_2.pdf`), but can be adapted for other forms by updating the field maps and template.
- Ensure your Supabase and Azure OpenAI credentials are kept secure and never committed to version control.
