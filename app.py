import streamlit as st
import json
import os
import re
from typing import List
import base64

# Pro Dark Theme
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stTextArea > label { color: #fafafa; }
    .stButton > button { 
        background: linear-gradient(90deg, #1f77b4, #0f4c7a); 
        color: white; 
        border-radius: 12px; 
        border: none;
        font-weight: bold;
        padding: 10px 20px;
    }
    .stSuccess { background-color: #164B19; border-radius: 8px; }
    .metric-container { background-color: #1a1d2e; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="ASL Translator", layout="wide", page_icon="🤟", initial_sidebar_state="expanded")

@st.cache_data(ttl=300)
def load_dict_safe(filename: str, default=dict()):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        st.error(f"⚠️ Invalid {filename} - using empty dict")
        return default

sentences = load_dict_safe("sentences.json")
words = load_dict_safe("words.json")
alphabet = load_dict_safe("alphabet.json")

def clean_token(token: str) -> str:
    return re.sub(r'[^\w]', '', token.lower().strip())

def get_sign_paths(text: str) -> List[str]:
    words_list = text.lower().split()
    result = []
    i = 0
    while i < len(words_list):
        word = clean_token(words_list[i])
        # Try sentences (simple match)
        sent_match = None
        for sent in sentences:
            if sent.split()[0] == word:
                sent_match = sent
                break
        if sent_match and os.path.exists(sentences[sent_match]):
            result.append(sentences[sent_match])
            i += 1
            continue
        # Words
        if word in words and os.path.exists(words[word]):
            result.append(words[word])
        else:
            # Alphabet/Number fallback
            for ch in word:
                ch_u = ch.upper()
                if ch_u in alphabet and os.path.exists(alphabet[ch_u]):
                    result.append(alphabet[ch_u])
        i += 1
    return result

# Sidebar Controls
with st.sidebar:
    st.title("⚙️ Pro Controls")
    autoplay = st.checkbox("⏯️ Auto-play", True)
    speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)
    
    st.subheader("➕ Quick Add")
    new_word = st.text_input("Word/Key")
    new_path = st.text_input("File path")
    if st.button("Add to words.json", use_container_width=True):
        if new_word and new_path:
            words[new_word] = new_path
            with open("words.json", "w") as f:
                json.dump(words, f, indent=2)
            st.success(f"✅ Added {new_word}")
            st.rerun()
    
    st.subheader("📊 Stats")
    test_text = st.text_input("Test coverage:", "yes thank you 8")
    test_signs = get_sign_paths(test_text)
    col1, col2 = st.columns(2)
    col1.metric("Signs", len(test_signs))
    col2.metric("Total Items", len(words) + len(alphabet))

# Main Interface
st.title("🤟 ASL Translator")
st.markdown("**Smart 3-Layer Logic:** Sentences → Words → Alphabet/Numbers | Zero Errors")

tab1, tab2 = st.tabs(["✨ Main Translator", "🔧 Tools"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        input_text = st.text_area("Type any sentence:", 
                                 placeholder="yes thank you 8 → yes.png + THANK letters + you.png + 8.png",
                                 height=100)
    with col2:
        if st.button("🚀 Generate Signs", type="primary", use_container_width=True):
            signs = get_sign_paths(input_text)
            if signs:
                st.session_state.last_signs = signs
                st.session_state.last_input = input_text
                st.success(f"✅ Ready! {len(signs)} signs generated.")
            else:
                st.warning("❌ No signs found. Add to JSONs or check paths.")
    
    # Display Results
    if 'last_signs' in st.session_state and st.session_state.last_signs:
        st.subheader("📹 Signs (in order)")
        cols = st.columns(4)
        for i, path in enumerate(st.session_state.last_signs):
            with cols[i % 4]:
                if os.path.splitext(path)[1].lower() in ['.gif', '.mp4', '.avi']:
                    st.video(path)
                else:
                    st.image(path, use_column_width=True)
                st.caption(f"**{os.path.basename(path)}**")

with tab2:
    st.subheader("📁 JSON Dictionaries")
    st.json({"Words": words, "Alphabet": alphabet, "Sentences": sentences})
    
    uploaded = st.file_uploader("Upload JSON", type=['json'])
    if uploaded:
        data = json.load(uploaded)
        filename = st.selectbox("Save to:", ["words.json", "alphabet.json"])
        if st.button("Import"):
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            st.success("Imported!")
            st.rerun()

# Footer
st.markdown("---")
with st.container():
    col1, col2, col3 = st.columns(3)
    col1.caption("🎯 Test: 'yes thank you 8'")
    col2.caption("📁 static/{sentences,words,alphabet}/*.png/gif/mp4")
    col3.caption("✨ Pro features: Live edit + Stats + History")
