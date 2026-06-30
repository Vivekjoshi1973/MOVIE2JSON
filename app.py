import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import json, PyPDF2, requests
from bs4 import BeautifulSoup

load_dotenv()

class MovieInfo(BaseModel):
    movie_name: str = Field(description="Full title of the movie")
    genre: str = Field(description="Genre(s) of the movie")
    director: str = Field(description="Director(s) of the movie")
    producer: str = Field(description="Production company or studio")
    release_info: str = Field(description="Any release or saga context mentioned")
    main_characters: List[str] = Field(description="List of main characters mentioned")
    antagonist: str = Field(description="Main villain or threat in the movie")
    plot_summary: str = Field(description="Brief plot summary in 2-3 sentences")
    key_themes: List[str] = Field(description="Key themes mentioned")
    emotional_tone: str = Field(description="Overall emotional tone of the movie")
    quick_summary: str = Field(description="One-line quick summary of the movie")

model = ChatMistralAI(model="mistral-small-2506", temperature=0.1)
parser = JsonOutputParser(pydantic_object=MovieInfo)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a movie information extraction assistant. Given a paragraph about a movie, extract structured information and return it in JSON format.

Extract the following fields:
- movie_name: Full title of the movie
- genre: Genre(s) of the movie
- director: Director(s) of the movie
- producer: Production company or studio
- release_info: Any release or saga context mentioned
- main_characters: List of main characters mentioned
- antagonist: Main villain or threat in the movie
- plot_summary: Brief plot summary in 2-3 sentences
- key_themes: List of key themes mentioned
- emotional_tone: Overall emotional tone of the movie
- quick_summary: One-line quick summary

Only extract information present in the given paragraph. Do not add external knowledge. Return valid JSON only."""),
    ("human", "Paragraph: {paragraph}")
])

chain = prompt | model | parser

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a movie expert assistant. You have the following extracted data about a movie:

{movie_json}

Answer the user's questions based on this data. Be concise and accurate."""),
    ("human", "{question}")
])

st.set_page_config(page_title="Movie2JSON", page_icon="🍃")
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a0a00, #2d1300, #1a0a00); }
    .main > div { background: transparent; }
    h1, h2, h3, p, label, .stCaption { color: #f0e6d3 !important; }
    .stTextArea textarea {
        background: rgba(240, 230, 211, 0.08) !important;
        border: 1px solid #e65100 !important;
        color: #f0e6d3 !important;
        border-radius: 8px !important;
        font-size: 15px !important;
    }
    .stTextArea textarea:focus {
        border-color: #ff8f00 !important;
        box-shadow: 0 0 12px rgba(255, 143, 0, 0.2) !important;
    }
    .stButton button {
        font-weight: bold !important;
        padding: 10px 30px !important;
        transition: all 0.3s !important;
        position: relative !important;
        overflow: hidden !important;
        letter-spacing: 0.5px !important;
    }
    .stButton button:hover {
        transform: translateY(-3px) !important;
    }
    button[key="extract_btn"] {
        background: linear-gradient(135deg, #e65100 0%, #bf360c 50%, #e65100 100%) !important;
        color: #f0e6d3 !important;
        border: 2px solid #ff8f00 !important;
        border-radius: 30px !important;
        padding: 12px 40px !important;
        font-size: 16px !important;
        box-shadow: 0 4px 15px rgba(230, 81, 0, 0.3) !important;
        letter-spacing: 2px !important;
    }
    button[key="extract_btn"]:hover {
        box-shadow: 0 8px 30px rgba(230, 81, 0, 0.6), inset 0 0 20px rgba(255, 143, 0, 0.15) !important;
        border-color: #ffd700 !important;
    }
    button[key="extract_btn"]::after {
        content: "⚡";
        margin-left: 8px;
    }
    button[key="fetch_btn"] {
        background: linear-gradient(135deg, #1a237e, #283593) !important;
        color: #e8eaf6 !important;
        border: 2px solid #5c6bc0 !important;
        border-radius: 30px !important;
        padding: 10px 30px !important;
        font-size: 14px !important;
        box-shadow: 0 4px 15px rgba(92, 107, 192, 0.3) !important;
    }
    button[key="fetch_btn"]:hover {
        box-shadow: 0 6px 25px rgba(92, 107, 192, 0.5) !important;
        border-color: #7986cb !important;
    }
    button[key="fetch_btn"]::before {
        content: "🌐 ";
    }
    button[key="download_btn"] {
        background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
        color: #e8f5e9 !important;
        border: 2px solid #66bb6a !important;
        border-radius: 12px 0 12px 0 !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3) !important;
    }
    button[key="download_btn"]:hover {
        box-shadow: 0 6px 25px rgba(46, 125, 50, 0.5) !important;
        border-color: #81c784 !important;
    }
    button[key="chat_btn"] {
        background: linear-gradient(135deg, #6a1b9a, #4a148c) !important;
        color: #f3e5f5 !important;
        border: 2px solid #ab47bc !important;
        border-radius: 0 12px 0 12px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(106, 27, 154, 0.3) !important;
    }
    button[key="chat_btn"]:hover {
        box-shadow: 0 6px 25px rgba(106, 27, 154, 0.5) !important;
        border-color: #ce93d8 !important;
    }
    button[key="reset_btn"] {
        background: linear-gradient(135deg, #c62828, #b71c1c) !important;
        color: #ffebee !important;
        border: 2px solid #ef5350 !important;
        border-radius: 30px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(198, 40, 40, 0.3) !important;
    }
    button[key="reset_btn"]:hover {
        box-shadow: 0 6px 25px rgba(198, 40, 40, 0.5) !important;
        border-color: #e57373 !important;
    }
    button[key="paste_tab"], button[key="url_tab"] {
        background: transparent !important;
        color: #a67c52 !important;
        border: 2px solid #5d2000 !important;
        border-radius: 25px !important;
        padding: 6px 22px !important;
        font-size: 13px !important;
        min-width: 0 !important;
        width: auto !important;
        height: 36px !important;
        transition: all 0.3s !important;
    }
    button[key="paste_tab"]:hover, button[key="url_tab"]:hover {
        border-color: #e65100 !important;
        color: #f0e6d3 !important;
        background: rgba(230, 81, 0, 0.15) !important;
        box-shadow: 0 0 15px rgba(230, 81, 0, 0.2) !important;
    }
    div[data-testid="column"]:has(button[key="paste_tab"]),
    div[data-testid="column"]:has(button[key="url_tab"]) {
        flex: 0 0 auto !important;
        width: auto !important;
    }
    .stCodeBlock {
        background: rgba(240, 230, 211, 0.05) !important;
        border: 1px solid #e65100 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stStatusWidget"] { display: none !important; }
    .logo-container { text-align: center; padding: 20px 0 10px 0; }
    .seal {
        display: inline-block; width: 100px; height: 100px;
        background: radial-gradient(circle at 30% 30%, #e65100, #5d2000);
        border-radius: 50%; border: 3px solid #ff8f00;
        box-shadow: 0 0 35px rgba(230, 81, 0, 0.6), inset 0 0 20px rgba(255, 143, 0, 0.15);
        text-align: center; position: relative;
        animation: pulse 3s infinite;
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 35px rgba(230, 81, 0, 0.6); }
        50% { box-shadow: 0 0 55px rgba(230, 81, 0, 0.9); }
    }
    .seal-ring {
        position: absolute; top: 5px; left: 5px; right: 5px; bottom: 5px;
        border: 2px dashed rgba(255, 143, 0, 0.4); border-radius: 50%;
    }
    .seal-inner {
        position: absolute; top: 15px; left: 15px; right: 15px; bottom: 15px;
        border: 2px solid rgba(255, 143, 0, 0.6); border-radius: 50%;
        display: flex; align-items: center; justify-content: center; font-size: 32px;
    }
    .seal-spiral {
        position: absolute; top: -8px; left: 50%; transform: translateX(-50%);
        font-size: 18px; filter: drop-shadow(0 0 4px rgba(255, 143, 0, 0.8));
    }
    .title {
        text-align: center; color: #ff8f00; font-size: 34px; font-weight: 900;
        letter-spacing: 5px; margin: 12px 0 2px 0;
        text-shadow: 3px 3px 0 #5d2000, 0 0 30px rgba(255, 143, 0, 0.2);
        font-family: 'Arial Black', sans-serif;
    }
    .subtitle {
        text-align: center; color: #bf7a3a; font-size: 11px;
        letter-spacing: 5px; text-transform: uppercase; margin: 0 0 25px 0;
        font-family: monospace;
    }
    .upload-zone {
        border: 2px dashed #5d2000; border-radius: 12px; padding: 15px;
        text-align: center; margin-top: 10px;
        background: rgba(240, 230, 211, 0.02);
    }
    .upload-zone .icon { font-size: 28px; }
    .upload-zone .text { color: #a67c52; font-size: 13px; font-weight: bold; }
    .stTextInput input {
        background: rgba(240, 230, 211, 0.08) !important;
        border: 1px solid #e65100 !important; color: #f0e6d3 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #ff8f00 !important;
        box-shadow: 0 0 12px rgba(255, 143, 0, 0.2) !important;
    }
    [data-testid="stFileUploader"] section {
        background: rgba(240, 230, 211, 0.05) !important;
        border: 1px dashed #e65100 !important; border-radius: 8px !important;
        color: #f0e6d3 !important;
    }
    [data-testid="stFileUploader"] section button {
        background: linear-gradient(145deg, #e65100, #bf360c) !important;
        color: #f0e6d3 !important; border: none !important;
    }
    .stSpinner > div {
        border-color: #e65100 !important; border-top-color: transparent !important;
    }
    .result-card {
        background: rgba(240, 230, 211, 0.05);
        border: 1px solid #e65100; border-radius: 8px; padding: 15px; margin-top: 10px;
    }
    .result-card h4 {
        color: #ff8f00; margin: 0 0 10px 0; font-size: 14px;
        letter-spacing: 2px; text-transform: uppercase;
    }
    .feature-tabs {
        display: flex; gap: 6px; justify-content: center; margin: 15px 0 10px 0;
    }
    .feature-tabs button {
        border-radius: 20px !important; padding: 4px 16px !important;
        font-size: 12px !important; font-weight: bold !important;
        min-width: 0 !important; width: auto !important; height: 30px !important;
        line-height: 1 !important;
        background: transparent !important; color: #a67c52 !important;
        border: 1px solid #5d2000 !important; transition: all 0.3s !important;
    }
    .feature-tabs button:hover {
        border-color: #e65100 !important; color: #f0e6d3 !important;
        background: rgba(230, 81, 0, 0.1) !important;
    }
    div[data-testid="column"]:has(button[key="paste_tab"]),
    div[data-testid="column"]:has(button[key="url_tab"]) {
        flex: 0 0 auto !important; width: auto !important;
    }
    .stChatMessage {
        background: rgba(240, 230, 211, 0.05) !important;
        border-radius: 12px !important; padding: 10px !important;
        margin: 5px 0 !important; border: 1px solid rgba(230, 81, 0, 0.15) !important;
    }
    .stChatInput textarea {
        background: rgba(240, 230, 211, 0.08) !important;
        border: 1px solid #e65100 !important; color: #f0e6d3 !important;
        border-radius: 12px !important;
    }
    .stChatInput textarea:focus {
        border-color: #ff8f00 !important;
        box-shadow: 0 0 12px rgba(255, 143, 0, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="logo-container">
    <div class="seal">
        <div class="seal-ring"></div>
        <div class="seal-inner">🎬</div>
        <div class="seal-spiral">🌀</div>
    </div>
    <div class="title">MOVIE2JSON</div>
    <div class="subtitle">⚡ Secret Jutsu Formula ⚡</div>
</div>
""", unsafe_allow_html=True)

if "input_mode" not in st.session_state:
    st.session_state.input_mode = "paste"
if "extracted" not in st.session_state:
    st.session_state.extracted = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

c1, c2, c3, c4, _ = st.columns([1, 1, 1, 1, 1])
with c1:
    if st.button("📝 Paste", key="paste_tab"):
        st.session_state.input_mode = "paste"; st.rerun()
with c2:
    if st.button("🌐 URL", key="url_tab"):
        st.session_state.input_mode = "url"; st.rerun()

paragraph = ""
if st.session_state.input_mode == "paste":
    paragraph = st.text_area("", placeholder="Paste a movie paragraph here...", height=140, label_visibility="collapsed")
    st.markdown('<div class="upload-zone"><div class="icon">📂</div><div class="text">Or upload .txt / .pdf below</div></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["txt", "pdf"], label_visibility="collapsed")
    if uploaded:
        if uploaded.type == "text/plain":
            paragraph = uploaded.read().decode("utf-8")
        elif uploaded.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded)
            paragraph = "".join(page.extract_text() for page in reader.pages)
        if paragraph:
            st.caption(f"✅ Loaded {len(paragraph.split())} words from {uploaded.name}")
else:
    url = st.text_input("", placeholder="Paste a movie URL (Wikipedia, IMDb, etc.)...", label_visibility="collapsed")
    if url and st.button("🌐 Fetch & Extract", key="fetch_btn", use_container_width=True):
        with st.spinner("Fetching page content..."):
            try:
                resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(resp.text, "lxml")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = soup.get_text(separator="\n")
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                paragraph = "\n".join(lines[:100])
                st.caption(f"✅ Fetched {len(paragraph.split())} words from URL")
            except Exception as e:
                st.error(f"Failed to fetch URL: {e}")

if st.button(" Extract Data", key="extract_btn", use_container_width=True) and paragraph.strip():
    with st.spinner("Running the extraction algorithm..."):
        try:
            st.session_state.extracted = chain.invoke({"paragraph": paragraph.strip()})
            st.session_state.chat_history = []
            st.rerun()
        except Exception as e:
            st.error(f"Extraction failed: {e}")

if st.session_state.extracted:
    result = st.session_state.extracted
    st.markdown('<div class="result-card"><h4>📦 Extracted JSON</h4></div>', unsafe_allow_html=True)
    st.code(json.dumps(result, indent=2, ensure_ascii=False), language="json")

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        st.download_button(" Download JSON", key="download_btn", data=json.dumps(result, indent=2, ensure_ascii=False),
                           file_name=f"{result.get('movie_name', 'movie').replace(' ', '_')}.json",
                           mime="application/json", use_container_width=True)
    with col_b:
        if st.button(" Chat with Movie", key="chat_btn", use_container_width=True):
            st.session_state.show_chat = True
    with col_c:
        if st.button(" New Extract", key="reset_btn", use_container_width=True):
            st.session_state.extracted = None
            st.session_state.chat_history = []
            st.session_state.show_chat = False
            st.rerun()

    if st.session_state.get("show_chat"):
        st.markdown("---")
        st.markdown("<h4 style='color:#ff8f00; text-align:center;'>💬 Ask anything about this movie</h4>", unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if q := st.chat_input("Ask about the movie..."):
            st.session_state.chat_history.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                chain = chat_prompt | model
                resp = chain.invoke({"movie_json": json.dumps(result, indent=2), "question": q})
                st.markdown(resp.content)
            st.session_state.chat_history.append({"role": "assistant", "content": resp.content})
