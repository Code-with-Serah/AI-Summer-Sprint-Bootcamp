# matcher.py
import json
from thefuzz import fuzz
from typing import List, Dict
import re

DATA_JSON = "dream_data.json"

def load_dream_data():
    """Load dream data with error handling."""
    try:
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {DATA_JSON} not found. Please run parser.py first.")
        return []
    except json.JSONDecodeError:
        print(f"Error: {DATA_JSON} is corrupted. Please regenerate it.")
        return []

def clean_meaning(meaning: str) -> str:
    """Clean and validate meaning text."""
    if not meaning or not isinstance(meaning, str):
        return ""
    
    # Remove extra whitespace and clean up
    cleaned = re.sub(r'\s+', ' ', meaning.strip())
    
    # Filter out garbage entries
    if (len(cleaned) < 10 or  # Too short
        cleaned.replace(' ', '').isdigit() or  # Only numbers
        len(set(cleaned.replace(' ', ''))) < 3):  # Too repetitive
        return ""
    
    return cleaned

def find_matches(symbols: List[str], threshold: int = 70) -> Dict[str, Dict[str, List[str]]]:
    """Find matches for symbols with improved fuzzy matching."""
    DREAM_DATA = load_dream_data()
    if not DREAM_DATA:
        return {}
    
    results = {}
    
    for query_symbol in symbols:
        grouped = {}
        
        for entry in DREAM_DATA:
            # Try matching against both English and original symbols
            symbol_en = entry.get("symbol_en", "").lower().strip()
            symbol_orig = entry.get("symbol_original", "").lower().strip()
            
            # Calculate match scores
            score_en = fuzz.token_set_ratio(query_symbol.lower(), symbol_en) if symbol_en else 0
            score_orig = fuzz.token_set_ratio(query_symbol.lower(), symbol_orig) if symbol_orig else 0
            max_score = max(score_en, score_orig)
            
            # Also try partial matching for compound words
            partial_score_en = fuzz.partial_ratio(query_symbol.lower(), symbol_en) if symbol_en else 0
            partial_score_orig = fuzz.partial_ratio(query_symbol.lower(), symbol_orig) if symbol_orig else 0
            max_partial = max(partial_score_en, partial_score_orig)
            
            # Use the better score
            final_score = max(max_score, max_partial * 0.8)  # Slight preference for exact matches
            
            if final_score >= threshold:
                meaning = clean_meaning(entry.get("meaning", ""))
                
                if not meaning:  # Skip if meaning is empty or invalid
                    continue
                
                book = entry.get("source_book", "Unknown Source")
                
                if book not in grouped:
                    grouped[book] = []
                
                # Avoid duplicates
                if meaning not in grouped[book]:
                    grouped[book].append(meaning)
        
        # Only include symbols with good matches
        if grouped:
            results[query_symbol] = grouped
    
    return results
