# extractor.py
import google.generativeai as genai
from langdetect import detect, DetectorFactory
from typing import List
import os
import re

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Setup Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.0-flash-exp"

def detect_language(text: str) -> str:
    """Detect whether the input is Arabic or English."""
    try:
        lang = detect(text)
        return "ar" if lang == "ar" else "en"
    except:
        # Fallback: check for Arabic characters
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        return "ar" if arabic_pattern.search(text) else "en"

def extract_symbols_with_gemini(dream_text: str) -> List[str]:
    """Extract key symbols from dream text using Gemini."""
    lang = detect_language(dream_text)
    
    # Enhanced prompt for better symbol extraction
    prompt = f"""
    You are an expert dream analyst. Extract the most important symbolic elements from this dream.

    Dream text (language: {lang}):
    "{dream_text}"

    Instructions:
    1. Extract 4-8 key symbolic elements (objects, people, actions, emotions, places)
    2. Focus on concrete nouns and significant actions
    3. Translate everything to English
    4. Return ONLY a comma-separated list of single words or short phrases
    5. No explanations, no numbering, just the symbols

    Examples of good symbols: water, flying, snake, death, baby, house, fire, car, mother, falling
    
    Symbols:"""

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        symbols_raw = response.text.strip()
        
        # Clean and process the response
        symbols_raw = re.sub(r'[^\w\s,]', '', symbols_raw)  # Remove special chars except commas
        symbols = [s.strip().lower() for s in symbols_raw.split(",") if s.strip()]
        
        # Filter out common words and ensure quality
        filtered_symbols = []
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        
        for symbol in symbols:
            if (len(symbol) >= 2 and 
                symbol not in stop_words and 
                not symbol.isdigit() and
                len(filtered_symbols) < 8):
                filtered_symbols.append(symbol)
        
        return filtered_symbols if filtered_symbols else ['dream', 'sleep']
        
    except Exception as e:
        print(f"Error extracting symbols: {e}")
        # Fallback: simple keyword extraction
        words = re.findall(r'\b\w+\b', dream_text.lower())
        return [w for w in words if len(w) > 3][:5]
