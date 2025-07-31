from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import os
import json
from pathlib import Path
import PyPDF2
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging
from sentence_transformers import SentenceTransformer, util
import torch

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API
if not os.getenv("GEMINI_API_KEY"):
    logger.error("GEMINI_API_KEY not found in environment variables")
    exit(1)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-1.5-flash"

# Configuration
DREAMS_DIR = "dreams"
CACHE_FILE = "dream_cache.json"

class EnhancedDreamInterpreter:
    def __init__(self):
        self.dream_data = []
        self.semantic_model = None
        self.load_semantic_model()
        self.load_or_process_pdfs()
    
    def load_semantic_model(self):
        """Load Arabic-compatible sentence transformer model."""
        try:
            # Try to load Arabic BERT model, fallback to multilingual if not available
            try:
                self.semantic_model = SentenceTransformer("asafaya/bert-base-arabic")
                logger.info("Loaded Arabic BERT model successfully")
            except:
                self.semantic_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
                logger.info("Loaded multilingual model as fallback")
        except Exception as e:
            logger.warning(f"Could not load semantic model: {e}")
            self.semantic_model = None

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF with Arabic support."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            # Clean up Arabic text
                            page_text = re.sub(r'\s+', ' ', page_text)
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Could not extract page {page_num + 1} from {pdf_path}: {e}")
                        continue
                
                return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            return ""

    def process_dream_pdf(self, pdf_path: str, book_name: str) -> List[Dict]:
        """Process a single PDF and extract dream interpretations."""
        logger.info(f"Processing {book_name}...")
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text or len(text) < 100:
            logger.warning(f"No sufficient text extracted from {book_name}")
            return []
        
        # Split text into smaller chunks for better processing
        chunks = [text[i:i+2000] for i in range(0, len(text), 1800)]  # Smaller chunks with overlap
        all_entries = []
        
        for chunk_num, chunk in enumerate(chunks):
            try:
                prompt = f"""
أنت خبير في تفسير الأحلام. استخرج من النص التالي رموز الأحلام ومعانيها بدقة.

النص:
{chunk}

التعليمات:
1. ابحث عن الرموز الواضحة (مثل: الماء، الطيران، الثعبان، البيت، الموت، النار، الطفل، الأم، السقوط، الزواج)
2. كل رمز يجب أن يكون له معنى مفصل وواضح
3. استخرج أيضاً المرادفات والكلمات المشابهة لكل رمز
4. أرجع النتيجة كـ JSON باللغة العربية فقط
5. تجاهل النصوص القصيرة أقل من 30 حرف
6. حد أقصى 12 رمز لكل استجابة

الشكل المطلوب:
[{{"رمز": "الرمز الأساسي", "مرادفات": ["مرادف1", "مرادف2"], "معنى": "التفسير المفصل والواضح"}}]

JSON:"""

                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(prompt)
                
                try:
                    # Clean the response to extract JSON
                    response_text = response.text.strip()
                    if '```json' in response_text:
                        response_text = response_text.split('```json')[1].split('```')[0]
                    elif '```' in response_text:
                        response_text = response_text.split('```')[1].split('```')[0]
                    
                    # Remove any non-JSON content
                    response_text = re.sub(r'^[^[\{]*', '', response_text)
                    response_text = re.sub(r'[^}\]]*$', '', response_text)
                    
                    parsed_entries = json.loads(response_text)
                    
                    if isinstance(parsed_entries, list):
                        for entry in parsed_entries:
                            if (isinstance(entry, dict) and 
                                'رمز' in entry and 
                                'معنى' in entry and
                                len(entry['معنى']) >= 30):
                                
                                # Get synonyms if available
                                synonyms = entry.get('مرادفات', [])
                                if isinstance(synonyms, str):
                                    synonyms = [s.strip() for s in synonyms.split(',')]
                                
                                all_entries.append({
                                    "symbol": entry['رمز'].strip(),
                                    "synonyms": synonyms,
                                    "meaning": entry['معنى'].strip(),
                                    "source_book": book_name
                                })
                                
                except json.JSONDecodeError as e:
                    logger.warning(f"Could not parse JSON from chunk {chunk_num + 1} of {book_name}: {e}")
                    continue
                    
            except Exception as e:
                logger.error(f"Error processing chunk {chunk_num + 1} of {book_name}: {e}")
                continue
        
        logger.info(f"Extracted {len(all_entries)} entries from {book_name}")
        return all_entries

    def load_or_process_pdfs(self):
        """Load cached data or process PDFs if needed."""
        # Check if cache exists
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.dream_data = json.load(f)
                logger.info(f"Loaded {len(self.dream_data)} cached dream interpretations")
                return
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
        
        # Process PDFs
        if not os.path.exists(DREAMS_DIR):
            logger.error(f"Dreams directory '{DREAMS_DIR}' not found!")
            return
        
        pdf_files = list(Path(DREAMS_DIR).glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in '{DREAMS_DIR}' directory!")
            return
        
        logger.info(f"Processing {len(pdf_files)} PDF files...")
        
        all_entries = []
        for pdf_file in pdf_files:
            book_name = pdf_file.stem.replace("_", " ").replace("-", " ")
            entries = self.process_dream_pdf(str(pdf_file), book_name)
            all_entries.extend(entries)
        
        self.dream_data = all_entries
        
        # Cache the results
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, ensure_ascii=False, indent=2)
            logger.info(f"Cached {len(all_entries)} dream interpretations")
        except Exception as e:
            logger.error(f"Could not save cache: {e}")

    def extract_dream_symbols(self, dream_text: str) -> List[str]:
        """Extract key symbols from Arabic dream text using improved prompting."""
        prompt = f"""
أنت خبير في تعبير الرؤى والأحلام. استخرج الرموز الأساسية المهمة من الحلم التالي.

نص الحلم:
"{dream_text}"

التعليمات:
1. استخرج أهم 4 إلى 8 رموز (أشياء، أشخاص، أفعال، مشاعر، أماكن)
2. ركّز على الأسماء والأفعال البارزة والمهمة في الحلم
3. أرجع قائمة مفصولة بفواصل عربية (،) فقط
4. لا تضع أرقام أو شروحات، فقط الرموز
5. استخدم الكلمات الأساسية الواضحة

أمثلة على الرموز الجيدة: ماء، طيران، ثعبان، موت، بيت، نار، سيارة، أم، سقوط، زواج، طفل، حريق

الرموز:"""

        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            symbols_raw = response.text.strip()
            
            # Clean up the response - keep only Arabic text and commas
            symbols_raw = re.sub(r'[^\u0600-\u06FF،\s]', '', symbols_raw)
            symbols = [s.strip() for s in symbols_raw.split("،") if s.strip()]
            
            # Filter and clean symbols
            filtered_symbols = []
            seen = set()
            for symbol in symbols:
                if len(symbol) >= 2 and symbol not in seen and len(filtered_symbols) < 8:
                    filtered_symbols.append(symbol)
                    seen.add(symbol)
            
            return filtered_symbols if filtered_symbols else ['حلم', 'نوم']
            
        except Exception as e:
            logger.error(f"Error extracting symbols: {e}")
            # Fallback: extract Arabic words from the dream text
            words = re.findall(r'[\u0600-\u06FF]{3,}', dream_text)
            return words[:5] if words else ['حلم']

    def find_interpretations_enhanced(self, symbols: List[str]) -> Dict:
        """Enhanced symbol matching with exact, partial, and semantic matching."""
        results = {}
        
        for symbol in symbols:
            matches = []
            symbol_lower = symbol.lower().strip()
            
            # 1. Exact matches
            for entry in self.dream_data:
                entry_symbol = entry['symbol'].lower().strip()
                if symbol_lower == entry_symbol:
                    matches.append({
                        'meaning': entry['meaning'],
                        'source': entry['source_book'],
                        'match_type': 'exact',
                        'confidence': 1.0
                    })
            
            # 2. Partial matches (substring matching)
            if len(matches) < 2:
                for entry in self.dream_data:
                    entry_symbol = entry['symbol'].lower().strip()
                    # Check if symbol is contained in entry or vice versa
                    if (symbol_lower in entry_symbol or entry_symbol in symbol_lower) and len(matches) < 3:
                        # Avoid duplicates
                        if not any(m['meaning'] == entry['meaning'] for m in matches):
                            matches.append({
                                'meaning': entry['meaning'],
                                'source': entry['source_book'],
                                'match_type': 'partial',
                                'confidence': 0.8
                            })
                    
                    # Also check synonyms if available
                    synonyms = entry.get('synonyms', [])
                    for synonym in synonyms:
                        if synonym and (symbol_lower == synonym.lower().strip() or 
                                      symbol_lower in synonym.lower().strip()):
                            if not any(m['meaning'] == entry['meaning'] for m in matches):
                                matches.append({
                                    'meaning': entry['meaning'],
                                    'source': entry['source_book'],
                                    'match_type': 'synonym',
                                    'confidence': 0.9
                                })
                                break
            
            # 3. Semantic matching using sentence transformers (if available)
            if len(matches) < 2 and self.semantic_model:
                semantic_matches = self.semantic_symbol_match(symbol)
                matches.extend(semantic_matches)
            
            # 4. Fuzzy text matching as final fallback
            if len(matches) < 1:
                fuzzy_matches = self.fuzzy_text_match(symbol)
                matches.extend(fuzzy_matches)
            
            if matches:
                # Sort by confidence and limit results
                matches.sort(key=lambda x: x['confidence'], reverse=True)
                results[symbol] = matches[:3]
        
        return results

    def semantic_symbol_match(self, symbol: str) -> List[Dict]:
        """Use sentence transformers for semantic matching."""
        if not self.semantic_model:
            return []
        
        matches = []
        try:
            symbol_embedding = self.semantic_model.encode(symbol, convert_to_tensor=True)
            
            for entry in self.dream_data:
                entry_embedding = self.semantic_model.encode(entry['symbol'], convert_to_tensor=True)
                
                # Calculate cosine similarity
                similarity = float(util.pytorch_cos_sim(symbol_embedding, entry_embedding))
                
                if similarity > 0.7:  # Threshold for semantic similarity
                    matches.append({
                        'meaning': entry['meaning'],
                        'source': entry['source_book'],
                        'match_type': 'semantic',
                        'confidence': similarity
                    })
            
            # Sort by similarity score
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            return matches[:2]  # Return top 2 semantic matches
            
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
            return []

    def fuzzy_text_match(self, symbol: str) -> List[Dict]:
        """Fuzzy matching based on Arabic text similarity."""
        matches = []
        symbol_chars = set(symbol.lower())
        
        for entry in self.dream_data:
            entry_symbol = entry['symbol'].lower()
            entry_chars = set(entry_symbol)
            
            # Calculate character overlap
            overlap = len(symbol_chars.intersection(entry_chars))
            total_chars = len(symbol_chars.union(entry_chars))
            
            if total_chars > 0:
                similarity = overlap / total_chars
                
                if similarity > 0.5:  # 50% character overlap threshold
                    matches.append({
                        'meaning': entry['meaning'],
                        'source': entry['source_book'],
                        'match_type': 'fuzzy',
                        'confidence': similarity * 0.6  # Lower confidence for fuzzy matches
                    })
        
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches[:1]  # Return only the best fuzzy match

# Initialize the enhanced interpreter
interpreter = EnhancedDreamInterpreter()

# Enhanced HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌙 مفسر الأحلام الذكي المطور</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            direction: rtl;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            text-align: center;
            padding: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .subtitle {
            margin-top: 10px;
            font-size: 1.1em;
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .input-section {
            margin-bottom: 30px;
        }
        textarea {
            width: 100%;
            height: 140px;
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            font-size: 16px;
            resize: vertical;
            direction: rtl;
            box-sizing: border-box;
        }
        textarea:focus {
            border-color: #4CAF50;
            outline: none;
        }
        .button {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 15px;
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }
        .results {
            margin-top: 30px;
            display: none;
        }
        .symbol-result {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-right: 5px solid #4CAF50;
        }
        .symbol-title {
            font-size: 1.4em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .interpretation {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #eee;
            position: relative;
        }
        .interpretation-text {
            margin-bottom: 10px;
            line-height: 1.6;
        }
        .source-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .source {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
        }
        .match-badge {
            background: #e3f2fd;
            color: #1976d2;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .match-exact { background: #e8f5e8; color: #2e7d32; }
        .match-partial { background: #fff3e0; color: #f57c00; }
        .match-semantic { background: #f3e5f5; color: #7b1fa2; }
        .match-fuzzy { background: #fce4ec; color: #c2185b; }
        .loading {
            text-align: center;
            font-size: 1.2em;
            color: #666;
            padding: 40px;
        }
        .stats {
            background: #f0f8f0;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            color: #2e7d32;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌙 مفسر الأحلام الذكي المطور</h1>
            <p class="subtitle">اكتب حلمك باللغة العربية وسنقوم بتفسيره باستخدام تقنيات الذكاء الاصطناعي المتقدمة</p>
        </div>
        
        <div class="content">
            <div class="stats" id="stats">
                📚 جاري تحميل قاعدة البيانات...
            </div>
            
            <div class="input-section">
                <textarea id="dreamText" placeholder="اكتب حلمك هنا بالتفصيل... مثال: رأيت في المنام أنني أطير فوق الماء الصافي وأمي تناديني من بعيد..."></textarea>
                <button class="button" onclick="interpretDream()">🔮 فسر الحلم</button>
            </div>
            
            <div id="results" class="results"></div>
        </div>
    </div>

    <script>
        // Load stats on page load
        window.onload = async function() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('stats').innerHTML = 
                    `📚 قاعدة البيانات تحتوي على ${data.total_interpretations} تفسير من الكتب الكلاسيكية`;
            } catch (error) {
                document.getElementById('stats').innerHTML = '📚 جاهز للاستخدام';
            }
        };

        async function interpretDream() {
            const dreamText = document.getElementById('dreamText').value.trim();
            const resultsDiv = document.getElementById('results');
            
            if (!dreamText) {
                alert('يرجى كتابة نص الحلم أولاً');
                return;
            }
            
            // Check for Arabic content
            const arabicPattern = /[\u0600-\u06FF]/;
            if (!arabicPattern.test(dreamText)) {
                alert('يرجى كتابة الحلم باللغة العربية');
                return;
            }
            
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div class="loading">🔍 جاري تحليل الحلم باستخدام الذكاء الاصطناعي...</div>';
            
            try {
                const response = await fetch('/api/interpret', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ dream: dreamText })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="symbol-result">❌ خطأ: ${data.error}</div>`;
                    return;
                }
                
                if (!data.interpretations || Object.keys(data.interpretations).length === 0) {
                    resultsDiv.innerHTML = `
                        <div class="symbol-result">
                            <div class="symbol-title">😔 لم نجد تفسيرات مطابقة</div>
                            <div class="interpretation">
                                <div class="interpretation-text">
                                    عذراً، لم نجد تفسيرات للرموز المستخرجة من حلمك في قاعدة البيانات الحالية.
                                    <br><br>
                                    <strong>الرموز المستخرجة:</strong> ${data.symbols ? data.symbols.join('، ') : 'لا توجد'}
                                    <br><br>
                                    <strong>اقتراحات:</strong>
                                    <ul style="text-align: right; margin: 10px 0;">
                                        <li>حاول وصف حلمك بتفاصيل أكثر</li>
                                        <li>استخدم كلمات أساسية واضحة مثل: الماء، الطيران، الموت، الزواج</li>
                                        <li>تأكد من الكتابة باللغة العربية الواضحة</li>
                                    </ul>
                                </div>
                            </div>
                        </div>`;
                    return;
                }
                
                let html = '<h2>🌟 نتائج تفسير الحلم:</h2>';
                html += `<div class="stats">🔍 تم العثور على تفسيرات لـ ${Object.keys(data.interpretations).length} رمز من أصل ${data.symbols.length} رموز مستخرجة</div>`;
                
                for (const [symbol, interpretations] of Object.entries(data.interpretations)) {
                    html += `
                        <div class="symbol-result">
                            <div class="symbol-title">🔮 ${symbol}</div>`;
                    
                    interpretations.forEach((interp, index) => {
                        const matchTypeMap = {
                            'exact': 'مطابقة تامة',
                            'partial': 'مطابقة جزئية', 
                            'semantic': 'مطابقة دلالية',
                            'synonym': 'مرادف',
                            'fuzzy': 'مطابقة تقريبية'
                        };
                        
                        const matchType = interp.match_type || 'exact';
                        const confidence = interp.confidence ? Math.round(interp.confidence * 100) : 100;
                        
                        html += `
                            <div class="interpretation">
                                <div class="interpretation-text">${interp.meaning}</div>
                                <div class="source-info">
                                    <span class="source">📖 المصدر: ${interp.source}</span>
                                    <span class="match-badge match-${matchType}">
                                        ${matchTypeMap[matchType]} (${confidence}%)
                                    </span>
                                </div>
                            </div>`;
                    });
                    
                    html += '</div>';
                }
                
                resultsDiv.innerHTML = html;
                
            } catch (error) {
                resultsDiv.innerHTML = `<div class="symbol-result">❌ حدث خطأ في الاتصال: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/interpret', methods=['POST'])
def interpret_dream():
    """Enhanced API endpoint to interpret dreams."""
    try:
        data = request.get_json()
        dream_text = data.get('dream', '').strip()
        
        if not dream_text:
            return jsonify({'error': 'نص الحلم مطلوب'}), 400
        
        # Check if text contains Arabic characters
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        if not arabic_pattern.search(dream_text):
            return jsonify({'error': 'يرجى كتابة الحلم باللغة العربية'}), 400
        
        logger.info(f"Processing dream: {dream_text[:50]}...")
        
        # Extract symbols from the dream
        symbols = interpreter.extract_dream_symbols(dream_text)
        logger.info(f"Extracted symbols: {symbols}")
        
        # Find interpretations using enhanced matching
        interpretations = interpreter.find_interpretations_enhanced(symbols)
        
        return jsonify({
            'symbols': symbols,
            'interpretations': interpretations,
            'total_entries': len(interpreter.dream_data),
            'matching_method': 'enhanced'
        })
        
    except Exception as e:
        logger.error(f"Error interpreting dream: {e}")
        return jsonify({'error': 'حدث خطأ أثناء تفسير الحلم'}), 500

@app.route('/api/status')
def status():
    """Get system status."""
    semantic_status = "متاح" if interpreter.semantic_model else "غير متاح"
    return jsonify({
        'status': 'online',
        'total_interpretations': len(interpreter.dream_data),
        'semantic_matching': semantic_status,
        'message': 'مفسر الأحلام المطور جاهز للاستخدام'
    })

if __name__ == '__main__':
    print("🌙 Starting Enhanced Dream Interpreter...")
    print(f"📚 Loaded {len(interpreter.dream_data)} dream interpretations")
    semantic_status = "✅ Available" if interpreter.semantic_model else "❌ Not available"
    print(f"🧠 Semantic matching: {semantic_status}")
    print("🚀 Server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)