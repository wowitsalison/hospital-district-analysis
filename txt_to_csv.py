import re
import csv

# Load the full text
with open("hospital_districts.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# Split text by hospital district
chapter_pattern = re.compile(r'CHAPTER \d+\.  ([A-Z][A-Z\s]+ HOSPITAL DISTRICT)')
parts = chapter_pattern.split(full_text)

# Build dictionary of districts
districts_parsed = {}
for i in range(1, len(parts), 2):
    name = parts[i].strip().upper()
    body = parts[i+1].strip()
    districts_parsed[name] = body

# Setup regexes
number_words = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

term_pattern = re.compile(
    r'serve[s]?\s+(?:staggered\s+)?(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*-\s*year\s+terms',
    re.IGNORECASE | re.DOTALL
)

amend_eff_pattern = re.compile(r'Amended by:.*?eff\.\s*(\w+ \d{1,2}, \d{4})', re.IGNORECASE | re.DOTALL)

# Regex to capture all "Acts ..." lines in the Amended by section
acts_pattern = re.compile(r'Amended by:(.*?eff\.\s*\w+ \d{1,2}, \d{4}\.)', re.IGNORECASE | re.DOTALL)
acts_line_pattern = re.compile(r'(Acts \d{4}.*?eff\.)', re.IGNORECASE)

# Get the term lengths in years
def extract_director_term(text):
    if not text:
        return None, False
    staggered = "staggered" in text.lower()
    match = term_pattern.search(text)
    term = None
    if match:
        term_str = match.group(1).lower()
        if term_str.isdigit():
            term = int(term_str)
        else:
            term = number_words.get(term_str, None)
    return term, staggered

# Get the amendment dates
def extract_amend_date(text):
    if not text:
        return None
    match = amend_eff_pattern.search(text)
    return match.group(1) if match else None

def extract_acts_lines(text):
    if not text:
        return None
    acts_section = acts_pattern.search(text)
    if acts_section:
        acts_lines = acts_line_pattern.findall(acts_section.group(1))
        return " | ".join([line.replace('\n', ' ').strip() for line in acts_lines])
    return None

def extract_acts_legislation(text):
    if not text:
        return None
    acts_section = acts_pattern.search(text)
    if acts_section:
        acts_lines = acts_line_pattern.findall(acts_section.group(1))
        formatted = []
        for line in acts_lines:
            # Example: Acts 2013, 83rd Leg., R.S., Ch. 826 (S.B. 1861), Sec. 1, eff.
            match = re.search(r'Acts (\d{4}).*?\((S\.B\.|H\.B\.) (\d+)\)', line)
            if match:
                year = match.group(1)
                bill_type = match.group(2)
                bill_num = match.group(3)
                formatted.append(f"{year}, {bill_type} {bill_num}")
        return " | ".join(formatted) if formatted else None
    return None

def extract_lease_limit(text):
    if not text:
        return None
    lease_pattern = re.compile(
        r'term\s+of\s+(a|the)\s+lease(?:\s+under\s+this\s+section)?\s+may\s+not\s+exceed\s+(\d+)\s+years',
        re.IGNORECASE | re.DOTALL
    )
    match = lease_pattern.search(text)
    if match:
        return int(match.group(2))
    return None

'''
# Process each district and print (for debugging and checking)
for name, body in districts:
    director_term, staggered = extract_director_term(body)
    amend_date = extract_amend_date(body)

    print(f"District: {name}")
    print(f"  Director Term (years): {director_term}")
    print(f"  Staggered?: {staggered}")
    print(f"  Last Amendment Date: {amend_date}")
    print("-" * 50)
'''

# Split text by chapter numbers (1001–1123)
chapter_split_pattern = re.compile(
    r'(CHAPTER (10[0-9]{2}|11[0-1][0-9]|112[0-3])\.\s+([A-Z][A-Z\s,.-]+))'
)
chapters = chapter_split_pattern.split(full_text)

# Build list of chapters
chapter_data = []
for i in range(1, len(chapters), 4):
    chapter_num = chapters[i+1]
    raw_name = chapters[i+2].strip()
    district_name = raw_name.split("SUBCHAPTER")[0].strip()
    district_name = district_name.replace('\n', ' ').replace('\r', ' ')  # Remove line breaks
    body = chapters[i+3].strip()
    chapter_data.append((chapter_num, district_name, body))

# Put data into CSV
with open("hospital_districts.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Chapter Number", "District Name", "Director Term (years)", "Staggered?",
        "Last Amendment Date", "Amendment Legislation", "Lease Length Limit (years), Legislation Link"
    ])

    for chapter_num, district_name, body in chapter_data:
        director_term, staggered = extract_director_term(body)
        amend_date = extract_amend_date(body)
        acts_legislation = extract_acts_legislation(body)
        lease_limit = extract_lease_limit(body)
        writer.writerow([chapter_num, district_name, director_term, staggered, amend_date, acts_legislation, lease_limit])