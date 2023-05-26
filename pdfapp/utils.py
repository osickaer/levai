import tabula
import PyPDF2

def parse_pdf(file_path):
    # Read the PDF and extract tables
    tables = tabula.read_pdf(file_path, pages=3)  # Adjust the page number as needed

    # Assuming the desired table is the first one on the page
    df = tables[0]

    # Set the column names manually
    df.columns = ["Item No.", "Reference", "Event", "Date or Deadline"]

    # Filter out rows where 'Date or Deadline' column is NaN
    df = df.dropna(subset=["Date or Deadline"])

    df = df.iloc[2:]

    df.reset_index(inplace=True)

    return df

def extract_fields_from_pdf(pdf_path):
    buyer_name = None
    email_address = None

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page = reader.pages[19]  # Extract page 20 (zero-based index)

        # Read the lines from the page
        lines = page.extract_text().split('\n')

        # Iterate over the lines and search for the fields
        for line in lines:
            if "Buyer" in line and "Name" in line:
                fields = line.split(': ')
                if len(fields) > 1:
                    buyer_name = fields[1]
            elif line.startswith("Email Address:"):
                fields = line.split(': ')
                if len(fields) > 1:
                    email_address = fields[1]

    return buyer_name, email_address


