import fitz
import re

pdf_path = "specialdistrictlocallawscode.pdf"
txt_path = "hospital_districts.txt"

# Remove headers, footers, and page numbers
def clean_line(line):
    if re.match(r'^SPECIAL DISTRICT LOCAL LAWS CODE$', line.strip()):
        return ""
    if re.match(r'^Statute text rendered on:', line.strip()):
        return ""
    if re.match(r'^- \d+ -$', line.strip()):
        return ""
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', line.strip()):
        return ""
    return line

def extract_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            for line in page.get_text().splitlines():
                cleaned = clean_line(line)
                if cleaned.strip():
                    text += cleaned + "\n"
    return text

extracted_text = extract_text(pdf_path)

with open(txt_path, "w", encoding="utf-8") as file:
    file.write(extracted_text)