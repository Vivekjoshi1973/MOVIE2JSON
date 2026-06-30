from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List
import uvicorn

load_dotenv()

app = FastAPI(title="Movie2JSON API", description="Extract structured movie info from text", version="1.0")

class MovieInfo(BaseModel):
    movie_name: str
    genre: str
    director: str
    producer: str
    release_info: str
    main_characters: List[str]
    antagonist: str
    plot_summary: str
    key_themes: List[str]
    emotional_tone: str
    quick_summary: str

class ExtractRequest(BaseModel):
    text: str

parser = JsonOutputParser(pydantic_object=MovieInfo)
model = ChatMistralAI(model="mistral-small-2506", temperature=0.1)

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

@app.post("/extract", response_model=MovieInfo)
def extract_movie(req: ExtractRequest):
    if not req.text.strip():
        raise HTTPException(400, "Text cannot be empty")
    try:
        return chain.invoke({"paragraph": req.text.strip()})
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
