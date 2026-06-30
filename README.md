# 🎬 MOVIE2JSON — Movie Info Extraction Tool

Turn any movie paragraph into structured JSON data using AI. Powered by Mistral AI.

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Paste Text** | Paste any movie paragraph and extract structured info |
| 📄 **File Upload** | Upload `.txt` or `.pdf` files |
| 🌐 **URL Scrape** | Paste a Wikipedia/IMDb URL and auto-extract |
| 📥 **Export JSON** | Download extracted data as `.json` file |
| 💬 **Chat with Movie** | Ask questions about the extracted movie |
| 🔌 **API Endpoint** | FastAPI backend for programmatic access |

## 🛠️ Setup

```bash
# Clone
git clone https://github.com/Vivekjoshi1973/MOVIE2JSON.git
cd MOVIE2JSON

# Install
pip install -r requirements.txt

# Add API key
echo "MISTRAL_API_KEY=your_key_here" > .env

# Run
streamlit run app.py
```

## 🚀 Deploy

Deploy on [Streamlit Community Cloud](https://streamlit.io/cloud) — set main file to `app.py`, add `MISTRAL_API_KEY` in Secrets.

## 🔌 API Usage

```bash
# Start server
python api.py

# Send request
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Avengers: Endgame is a superhero movie..."}'
```
