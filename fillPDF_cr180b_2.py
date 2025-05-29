from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
from supabase import create_client, Client
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
import json
import textwrap

# Supabase connection
url = "https://iytkduocvtzzsaslpthl.supabase.co"
key = str(os.getenv("SUPABASE_KEY"))  # Ensure you set this environment variable
supabase: Client = create_client(url, key)

# Initialize Azure OpenAI client
openAIClient = AzureOpenAI(
    api_key= str(os.getenv("AZURE_OPENAI_API_KEY")),

    api_version="2025-01-01-preview",  # Use the latest API version
    azure_endpoint="https://mehuldemo.openai.azure.com/"  # Replace with your Azure endpoint
)


# Configurable inputs
#input_pdf_template_path = "PDF_Template/dci-600f.pdf"
input_pdf_template_path = "PDF_Template/cr180b_2.pdf"
output_directory = "PDF_Output"
output_file_name = "Test-CaseName-cr180b_2"

field_map_template = {
    "FILENO": "NUMBER STRING",
    "COUNTYNAME": "TEXT STRING",
    "VICTIM-INFORMATION_RECEIVE-FURTHER-NOTICES_YES": "BOOLEAN",
    "VICTIM-INFORMATION_RECEIVE-FURTHER-NOTICES_NO": "BOOLEAN",
    "VICTIM-NOTIFICATION-REQUEST_DATE": "DATE STRING",
    "VICTIM-INFORMATION_NAME": "TEXT STRING", 
    "VICTIM-INFORMATION_ADDRESS-STREET": "TEXT STRING",
    "VICTIM-INFORMATION_ADDRESS-CITY-STATE-ZIP": "TEXT STRING",
    "VICTIM-INFORMATION_ADDRESS-ADDRESS-NOT-DISLOSED": "BOOLEAN",
    "VICTIM-INFORMATION_AGENCY": "TEXT STRING",
    "VICTIM-INFORMATION_PHONENO": "PHONE NUMBER STRING",
    "VICTIM-INFORMATION_PHONE-NUMBER-NOT-DISCLOSED": "BOOLEAN",
    "STATE-VERSUS_DEFENDANTNAME": "TEXT STRING",
    "INFORMATION-FOR-VICTIMS_LAWENFORCEMENT-OFFICER": "TEXT STRING",
    "VICTIM-NOTIFICATION-REQUEST_NOT-RECEIVE": "BOOLEAN",
    "VICTIM-NOTIFICATION-REQUEST_TRIAL-PROCEEDINGS": "BOOLEAN",
    "VICTIM-NOTIFICATION-REQUEST_POST-TRIAL-PROCEEDINGS": "BOOLEAN",
    "VICTIM-NOTIFICATION-REQUEST_RECEIVE-NOTICE_NO": "BOOLEAN",
    "VICTIM-NOTIFICATION-REQUEST_RECEIVE-NOTICE_YES": "BOOLEAN",
    "LAW-ENFORCEMENT-PERSONNEL_NAME": "TEXT STRING",
    "LAW-ENFORCEMENT-PERSONNEL_TITLE": "TEXT STRING",
    "LAW-ENFORCEMENT-PERSONNEL_SIGNATURE-DATE": "DATE STRING",
    "VICTIM-INFORMATION_OTHER-CONTACT-INFO": "TEXT STRING",
    "VICTIM-INFORMATION_OTHER-CONTACT-NOT-DISCLOSED": "BOOLEAN"
} 

field_map = {
    "FILENO": "FileNo",
    "COUNTYNAME": "CountyName",
    "VICTIM-INFORMATION_RECEIVE-FURTHER-NOTICES_YES": "Wish",
    "VICTIM-INFORMATION_RECEIVE-FURTHER-NOTICES_NO": "NotWish",
    "VICTIM-NOTIFICATION-REQUEST_DATE": "SignedDate2",
    "VICTIM-INFORMATION_NAME": "Name", 
    "VICTIM-INFORMATION_ADDRESS-STREET": "AddressStreet2",
    "VICTIM-INFORMATION_ADDRESS-CITY-STATE-ZIP": "AddressCity",
    "VICTIM-INFORMATION_ADDRESS-ADDRESS-NOT-DISLOSED": "AddrNoDisclosed",
    "VICTIM-INFORMATION_AGENCY": "Agency",
    "VICTIM-INFORMATION_PHONENO": "TelephoneNo",
    "VICTIM-INFORMATION_PHONE-NUMBER-NOT-DISCLOSED": "TelephoneNoDisclosed",
    "STATE-VERSUS_DEFENDANTNAME": "DefendantName",
    "INFORMATION-FOR-VICTIMS_LAWENFORCEMENT-OFFICER": "LawEnforcement",
    "VICTIM-NOTIFICATION-REQUEST_NOT-RECEIVE": "NotWish2",
    "VICTIM-NOTIFICATION-REQUEST_TRIAL-PROCEEDINGS": "Trial",
    "VICTIM-NOTIFICATION-REQUEST_POST-TRIAL-PROCEEDINGS": "PostTrial",
    "VICTIM-NOTIFICATION-REQUEST_RECEIVE-NOTICE_NO": "NotWish2",
    "VICTIM-NOTIFICATION-REQUEST_RECEIVE-NOTICE_YES": "Wish2",
    "LAW-ENFORCEMENT-PERSONNEL_NAME": "PersonnelName",
    "LAW-ENFORCEMENT-PERSONNEL_TITLE": "Title",
    "LAW-ENFORCEMENT-PERSONNEL_SIGNATURE-DATE": "SignedDate1",
    "VICTIM-INFORMATION_OTHER-CONTACT-INFO": "ContactInfo",
    "VICTIM-INFORMATION_OTHER-CONTACT-NOT-DISCLOSED": "ContactNoDisclosed"
} 

def list_pdf_fields(pdf_path):
    pdf = PdfReader(pdf_path)
    fields = set()

    if not hasattr(pdf, "pages") or not isinstance(pdf.pages, (list, tuple)) or not pdf.pages:
        raise ValueError("Invalid PDF file or no pages found.")
    

    for page in pdf.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                if annotation['/Subtype'] == '/Widget' and annotation['/T']:
                    fields.add(annotation['/T'][1:-1])  # Remove parentheses
    return fields


def create_overlay(data_dict, field_map, template_pdf):
    overlay = BytesIO()
    c = canvas.Canvas(overlay, pagesize=letter)

    pdf = PdfReader(template_pdf)

    if not hasattr(pdf, "pages") or not isinstance(pdf.pages, (list, tuple)) or not pdf.pages:
        raise ValueError("Invalid PDF file or no pages found.")

    for page_number, page in enumerate(pdf.pages):
        annotations = page.Annots
        if not annotations:
            c.showPage()
            continue

        for annot in annotations:
            if not annot or not annot.T:
                continue

            field = annot.T.to_unicode()
            rect = annot.Rect
            x, y = float(rect[0]), float(rect[1])


            for label, pdf_field in field_map.items():
                if pdf_field == field and label in data_dict:
                    #c.drawString(x + 2, y + 2, str(data_dict[label]))

                    value = data_dict[label]
                    
                    if isinstance(value, bool):  # Checkbox logic
                        if value:
                            c.drawString(x + 2, y + 2, "✔")  # or use "X"
                    else:
                        #c.drawString(x + 2, y + 2, str(value))
                        # lines = str(value).split('\n')
                        # line_height = 12  # or adjust for your font size
                        # for i, line in enumerate(lines):
                        #     c.drawString(x + 2, y + 2 - i * line_height, line)

                        if label == "VICTIM-INFORMATION_OTHER-CONTACT-INFO":
                            wrapped_lines = textwrap.wrap(str(value), width=50)  # 50 chars per line
                        else:
                            wrapped_lines = str(value).split('\n')

                        lines = str(value).split('\n')
                        line_height = 10  # or adjust for your font size

                        # Use the top of the field box as the starting y position
                        top_y = float(rect[3])

                        # Start from the top of the box (higher y)
                        start_y = y + (len(lines)) * line_height

                        for i, line in enumerate(lines):
                            y_pos = top_y - (i + 1) * line_height
                            if y_pos < float(rect[1]):
                                break
                            c.drawString(x + 2, y_pos - 1, line)

                            #c.drawString(x + 2, start_y - i * line_height, line)

        c.showPage()  # Move to the next page in the overlay

    c.save()
    overlay.seek(0)
    return overlay


def flatten_pdf(template_path, overlay_stream, output_path):
    template_pdf = PdfReader(template_path)
    overlay_pdf = PdfReader(overlay_stream)

    if not hasattr(template_pdf, "pages") or not isinstance(template_pdf.pages, (list, tuple)) or not template_pdf.pages:
        raise ValueError("Invalid PDF file or no pages found.")
    if not hasattr(overlay_pdf, "pages") or not isinstance(overlay_pdf.pages, (list, tuple)) or not overlay_pdf.pages:
        raise ValueError("Invalid PDF file or no pages found.")

    for page_num, (template_page, overlay_page) in enumerate(zip(template_pdf.pages, overlay_pdf.pages)):
        merger = PageMerge(template_page)
        merger.add(overlay_page, prepend=False).render()


    writer = PdfWriter()
    writer.addpages(template_pdf.pages)
    writer.write(output_path)


def pullFromDB(tableName, reportID):  
    if tableName == 'reports':
        response = (
            supabase
            .table(tableName)
            .select("*")
            .eq("id", reportID)
            .execute()
        )
        
        # Access the data
        #print(f"\nTable: {tableName}\n\n{response.data} \n\n")
        return response.data

    else:
        response = (
            supabase
            .table(tableName)
            .select("*")
            .eq("report_id", reportID)
            .execute()
        )
        
        # Access the data
        #print(f"\nTable: {tableName}\n\n{response.data} \n\n")
        return response.data


def mapValues(field_map, property_items, reports, crime_incidents, persons_involved, suspects, offenders, drug_items, vehicles_involved):
    Prompt = f"""
                Your only goal is to map the values to the fields asked.
                Your input will be multiple tables from a DataBase that contians information.
                The template you need to fill out is a field_map which is a data dict.
                Ensure you fill out the data_dict with the values from the tables.
                You need to return the back a data_dict that contains the values for the fields in the field_map.
                If the key needs to be a boolean, then ensure you return a boolean value. 'True' or 'False'. Ensue the 'T' and 'F' are capitalized.
                If the key is a boolean then ensure the True or False is capitalized. The first letter should be capitalized.
                If the key needs to be a string, then ensure you return a string value.
                If the key needs to be a date, then ensure you return a date value in the format 'MM/DD/YYYY' as a string
                If the key needs to be a phone number, then ensure you return a phone number value in the format 'XXX-XXX-XXXX' as a string.
                If you need to get a county based on the address, then search for the county name using your knowledge.
                If the key needs to be a number, then ensure you return a number value as a string.
                You will only reply back in JSON.
                Only reply in JSON with no other text or special characters.
                DO not add ``` in your response. Simpily give the JSON.
                Enssrue the first letter of the all boolean values are capitalized.
    """

    content = f"""
                Here is the field_map that you need to fill out:
                field_map: {field_map_template}
                
                Data from DB tables:

                property_items: {property_items}
                reports: {reports}
                crime_incidents: {crime_incidents}
                persons_involved: {persons_involved}
                suspects: {suspects}
                offenders: {offenders}
                drug_items: {drug_items}
                vehicles_involved: {vehicles_involved}  
            
            """
    
    msg = [
        ChatCompletionSystemMessageParam(role="system", content=Prompt),
        ChatCompletionUserMessageParam(role="user", content=content)
    ]

    response = openAIClient.chat.completions.create(
        model="gpt-4.1",  # Replace with your Azure OpenAI deployment name
        messages=msg
    )

    response_content = response.choices[0].message.content

    print(response_content)

    return response_content


def main():
    # Supabase table names
    supabase_tables = ['property_items', 'reports', 'crime_incidents', 'persons_involved', 'suspects', 'offenders', 'drug_items', 'vehicles_involved']
    report_id = "c78c75d6-4b02-4ef7-b066-16244a3ba37b"


    # Get data from Supabase
    property_items = pullFromDB(supabase_tables[0], report_id)
    reports = pullFromDB(supabase_tables[1], report_id)
    crime_incidents = pullFromDB(supabase_tables[2], report_id)
    persons_involved = pullFromDB(supabase_tables[3], report_id)
    suspects = pullFromDB(supabase_tables[4], report_id)
    offenders = pullFromDB(supabase_tables[5], report_id)
    drug_items = pullFromDB(supabase_tables[6], report_id)
    vehicles_involved = pullFromDB(supabase_tables[7], report_id)

    data_dict = mapValues(field_map, property_items, reports, crime_incidents, persons_involved, suspects, offenders, drug_items, vehicles_involved)

    if isinstance(data_dict, str):
        try:
            data_dict = json.loads(data_dict)
        except Exception as e:
            raise ValueError(f"data_dict is a string but could not be parsed as JSON: {e}")

    if not isinstance(data_dict, dict):
        raise TypeError("data_dict is not a dictionary after parsing.")


    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    report = reports[0]
    agencyName = report["agency_name"]
    output_file_name = f"{agencyName}_{report_id}"
    output_path = os.path.join(output_directory, f"{output_file_name}.pdf")



    overlay = create_overlay(data_dict, field_map, input_pdf_template_path)
    flatten_pdf(input_pdf_template_path, overlay, output_path)

    print(f"Non-editable PDF saved to: {output_path}")


    # #List all of the fields
    # fields = list_pdf_fields(input_pdf_template_path)
    # print(fields)


if __name__ == "__main__":
    main()





# data_dict = {
#     "FILENO": "123456789",
#     "COUNTYNAME": "Cary",
#     "VICTIM-INFORMATION_RECEIVE-FURTHER-NOTICES_YES": False,
#     "VICTIM-INFORMATION_RECEIVE-FURTHER-NOTICES_NO": False,
#     "VICTIM-NOTIFICATION-REQUEST_DATE": "05/21/2025",
#     "VICTIM-INFORMATION_NAME": "John Doe, the Victim",
#     "VICTIM-INFORMATION_ADDRESS-STREET": "1234 Main St Apt 101",
#     "VICTIM-INFORMATION_ADDRESS-CITY-STATE-ZIP": "Cary, NC 27512",
#     "VICTIM-INFORMATION_ADDRESS-ADDRESS-NOT-DISLOSED": False,
#     "VICTIM-INFORMATION_AGENCY": "TESTING",
#     "VICTIM-INFORMATION_PHONENO": "222-222-2222",
#     "VICTIM-INFORMATION_PHONE-NUMBER-NOT-DISCLOSED": False,
#     "VICTIM-INFORMATION_OTHER-CONTACT-INFO": "johndoe@email.com",
#     "VICTIM-INFORMATION_OTHER-CONTACT-NOT-DISCLOSED": False,
#     "VICTIM-INFORMATION_ADDRESS-STREET-1": "1234 Main Street",
#     "STATE-VERSUS_DEFENDANTNAME": "JOHN DOE, THE DEFENDANT",
#     "INFORMATION-FOR-VICTIMS_LAWENFORCEMENT-OFFICER": f"Officer M.V Matos\nCary Police Department\n120 Wilkinson Ave\nCary, NC 27512\n(919) 469-4012",
#     "VICTIM-NOTIFICATION-REQUEST_NOT-RECEIVE": False,
#     "VICTIM-NOTIFICATION-REQUEST_TRIAL-PROCEEDINGS": False,
#     "VICTIM-NOTIFICATION-REQUEST_POST-TRIAL-PROCEEDINGS": False,
#     "VICTIM-NOTIFICATION-REQUEST_RECEIVE-NOTICE_YES": False,
#     "VICTIM-NOTIFICATION-REQUEST_RECEIVE-NOTICE_NO": False,
#     "LAW-ENFORCEMENT-PERSONNEL_NAME": "Officer Maria Santos",
#     "LAW-ENFORCEMENT-PERSONNEL_TITLE": "Detective",
#     "LAW-ENFORCEMENT-PERSONNEL_SIGNATURE-DATE": "05/23/2025"

# }
