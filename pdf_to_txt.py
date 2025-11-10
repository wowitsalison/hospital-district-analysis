import fitz

pdf_path = "specialdistrictlocallawscode.pdf"
txt_path = "hospital_districts.txt"

# Extract text from a PDF file
def extract_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

extracted_text = extract_text(pdf_path)

# Save the extracted text to a .txt file
with open(txt_path, "w", encoding="utf-8") as file:
    file.write(extracted_text)