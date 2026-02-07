import fitz  # PyMuPDF
import json
import re
import os

# CONFIGURATION
# Using absolute paths to avoid "File Not Found" errors
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PDF_PATH = os.path.join(PROJECT_ROOT, "data", "Four Vedas - English Translation.pdf")
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "data", "atharva_dataset.json")

def extract_atharva_veda():
    # 1. ENSURE DIRECTORIES EXIST
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at: {PDF_PATH}")
        print("Please move your PDF into the 'data' folder inside 'atharvaveda-v1'")
        return

    doc = fitz.open(PDF_PATH)
    print(f"Opened PDF with {len(doc)} pages.")

    # 2. FIND START PAGE (Bloomfield Translation usually starts around 1311)
    # We will search aggressively for the header
    start_page = 1311 
    found_start = False
    
    for page_num in range(1300, 1350):
        text = doc[page_num].get_text()
        if "ATHARVA-VEDA" in text.upper() and "BLOOMFIELD" in text.upper():
            start_page = page_num
            found_start = True
            print(f"Found Start Marker at Page {start_page}")
            break
            
    if not found_start:
        print(f"Warning: Start marker not found. Defaulting to Page {start_page}")

    # 3. EXTRACTION LOOP
    hymns = []
    current_hymn = None
    
    # Improved Regex: Captures "VI, 105. CHARM..." and takes the WHOLE line as title
    header_pattern = re.compile(r"([XVI]+),\s+(\d+)\.\s+(.+)")

    for i in range(start_page, len(doc)):
        text = doc[i].get_text("text")
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Skip empty lines or page headers
            if not line or "Four Vedas" in line or line.isdigit():
                continue

            match = header_pattern.match(line)
            
            if match:
                # Save previous hymn
                if current_hymn:
                    hymns.append(current_hymn)
                
                # Start new hymn
                book_num = match.group(1)
                hymn_num = match.group(2)
                raw_title = match.group(3).strip()
                
                # Clean the title (remove trailing dots or page numbers)
                clean_title = raw_title.rstrip(" .0123456789")

                current_hymn = {
                    "id": f"{book_num}_{hymn_num}",
                    "book": book_num,
                    "hymn": hymn_num,
                    "title": clean_title,
                    "content": "",
                    "page": i
                }
                print(f"Extracted: {clean_title} (Bk {book_num}, Hymn {hymn_num})")
            
            elif current_hymn:
                # Append text to current hymn
                current_hymn["content"] += line + " "

    # Save the last hymn
    if current_hymn:
        hymns.append(current_hymn)

    # 4. SAVE TO JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(hymns, f, indent=2, ensure_ascii=False)
    
    print(f"\nSUCCESS: Saved {len(hymns)} hymns to {OUTPUT_JSON}")

if __name__ == "__main__":
    extract_atharva_veda()