# app.py
import streamlit as st
import json
import os
from extractor import extract_symbols_with_gemini
from matcher import find_matches

st.set_page_config(page_title="Dream Interpretation AI", page_icon="🌙", layout="centered")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check if data file exists
if not os.path.exists("dream_data.json"):
    st.error("❌ Dream data not found! Please run parser.py first to process your PDF books.")
    st.stop()

st.title("🌙 Dream Interpretation Chatbot")
st.markdown("Enter your dream in **Arabic or English** to get interpretations from classical books.")

# Chat display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Describe your dream here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Show processing message
            processing_placeholder = st.empty()
            processing_placeholder.markdown("🔍 Analyzing your dream...")

            # Step 1: Extract symbols via Gemini
            symbols = extract_symbols_with_gemini(prompt)
            processing_placeholder.markdown(f"🔍 Found symbols: {', '.join(symbols)}")

            # Step 2: Match against dream data
            results = find_matches(symbols)

            # Step 3: Format response
            if not results:
                response = "😔 Sorry, I couldn't find interpretations for the symbols in your dream within our available books. Try describing your dream with more specific objects or actions."
            else:
                lines = [f"🌟 **Dream Interpretation Results:**\n"]
                
                for symbol, books in results.items():
                    lines.append(f"### 🔮 {symbol.title()}")
                    for book, meanings in books.items():
                        lines.append(f"\n📖 **{book}:**")
                        for meaning in meanings[:3]:  # Limit to 3 meanings per book
                            # Clean up the meaning text
                            clean_meaning = meaning.strip()
                            if len(clean_meaning) > 200:
                                clean_meaning = clean_meaning[:200] + "..."
                            lines.append(f"• {clean_meaning}")
                        lines.append("")  # Add spacing
                
                response = "\n".join(lines)

            # Clear processing message and display result
            processing_placeholder.empty()
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"❌ Error processing your dream: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, there was an error processing your dream: {str(e)}"})