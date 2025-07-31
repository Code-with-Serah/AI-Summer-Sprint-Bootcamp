# parser.py (Improved)
import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import re
from typing import List, Dict

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.0-flash-exp"
DATA_DIR = "dreams"
OUTPUT_JSON = "dream_data.json"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF with better error handling."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    # Clean up the text
                    page_text = re.sub(r'\s+', ' ', page_text)
                    text += page_text + "\n"
            except Exception as e:
                print(f"Warning: Could not extract page {page_num + 1} from {pdf_path}: {e}")
                continue
                
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def parse_dream_entries(text: str, source_book: str) -> List[Dict]:
    """Parse text into structured dream entries using AI."""
    if not text or len(text) < 100:
        return []
    
    # Split text into manageable chunks (Gemini has context limits)
    chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
    all_entries = []
    
    for chunk_num, chunk in enumerate(chunks):
        try:
            prompt = f"""
            Parse this dream interpretation text into structured entries. Extract symbol-meaning pairs.

            Text:
            {chunk}

            Instructions:
            1. Find entries that contain dream symbols and their interpretations
            2. Each entry should have a clear symbol/keyword and its meaning
            3. Return as JSON array: [{{"symbol": "word", "meaning": "interpretation text"}}]
            4. Skip entries shorter than 15 characters
            5. Translate symbols to English if they're in Arabic
            6. Maximum 20 entries per response

            JSON:"""

            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                parsed_entries = json.loads(response.text.strip())
                if isinstance(parsed_entries, list):
                    for entry in parsed_entries:
                        if (isinstance(entry, dict) and 
                            'symbol' in entry and 
                            'meaning' in entry and
                            len(entry['meaning']) >= 15):
                            
                            all_entries.append({
                                "symbol_en": entry['symbol'].strip(),
                                "symbol_original": entry['symbol'].strip(),
                                "meaning": entry['meaning'].strip(),
                                "source_book": source_book
                            })
            except json.JSONDecodeError:
                print(f"Could not parse JSON from chunk {chunk_num + 1} of {source_book}")
                continue
                
        except Exception as e:
            print(f"Error processing chunk {chunk_num + 1} of {source_book}: {e}")
            continue
    
    return all_entries

def clean_book_name(filename: str) -> str:
    """Clean up book filename for display."""
    name = filename.replace(".pdf", "").replace("-", " ").replace("_", " ")
    # Capitalize properly
    name = " ".join(word.capitalize() for word in name.split())
    return name.strip()

def parse_books_to_json():
    """Main function to parse all PDF books and create JSON data."""
    if not os.path.exists(DATA_DIR):
        print(f"Error: Directory '{DATA_DIR}' not found!")
        return
    
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{DATA_DIR}' directory!")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process...")
    
    all_entries = []
    
    for filename in pdf_files:
        pdf_path = os.path.join(DATA_DIR, filename)
        source_book = clean_book_name(filename)
        
        print(f"Processing {filename}...")
        
        # Extract text
        raw_text = extract_text_from_pdf(pdf_path)
        
        if not raw_text:
            print(f"Warning: No text extracted from {filename}")
            continue
        
        # Parse entries using AI
        entries = parse_dream_entries(raw_text, source_book)
        
        if entries:
            all_entries.extend(entries)
            print(f"  ✓ Extracted {len(entries)} entries from {source_book}")
        else:
            print(f"  ✗ No valid entries found in {source_book}")
    
    if all_entries:
        # Save as JSON
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(all_entries, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Successfully saved {len(all_entries)} entries to {OUTPUT_JSON}")
        print(f"📚 Books processed: {len(pdf_files)}")
    else:
        print("\n❌ No entries were extracted from any books!")

if __name__ == "__main__":
    parse_books_to_json()