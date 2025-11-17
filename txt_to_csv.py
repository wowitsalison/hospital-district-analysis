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
    r'serve[s]? (?:staggered )?(\d+|one|two|three|four|five|six|seven|eight|nine|ten)-year terms',
    re.IGNORECASE
)

amend_eff_pattern = re.compile(r'Amended by:.*?eff\.\s*(\w+ \d{1,2}, \d{4})', re.IGNORECASE | re.DOTALL)


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
    writer.writerow(["Chapter Number", "District Name", "Director Term (years)", "Staggered?", "Last Amendment Date"])

    for chapter_num, district_name, body in chapter_data:
        director_term, staggered = extract_director_term(body)
        amend_date = extract_amend_date(body)
        writer.writerow([chapter_num, district_name, director_term, staggered, amend_date])