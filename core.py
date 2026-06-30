from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

load_dotenv()
# using pydantic importing basemodal class -guiding how to give output 
class MovieInfo(BaseModel):
    movie_name: str = Field(description="Full title of the movie")
    genre: str = Field(description="Genre(s) of the movie (e.g. superhero, action, sci-fi)")
    director: str = Field(description="Director(s) of the movie")
    producer: str = Field(description="Production company or studio")
    release_info: str = Field(description="Any release or saga context mentioned")
    main_characters: List[str] = Field(description="List of main characters/heroes mentioned")
    antagonist: str = Field(description="Main villain or threat in the movie")
    plot_summary: str = Field(description="Brief summary of the plot in 2-3 sentences")
    key_themes: List[str] = Field(description="Key themes (e.g. sacrifice, teamwork, time travel)")
    emotional_tone: str = Field(description="Overall emotional tone of the movie")
    quick_summary: str = Field(description="One-line quick summary of the movie")

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a movie information extraction assistant. Given a paragraph about a movie, extract structured information and return it in JSON format.

Extract the following fields:
- movie_name: Full title of the movie
- genre: Genre(s) of the movie
- director: Director(s) of the movie
- producer: Production company or studio
- release_info: Any release or saga context mentioned
- main_characters: List of main characters/heroes mentioned
- antagonist: Main villain or threat in the movie
- plot_summary: Brief plot summary in 2-3 sentences
- key_themes: List of key themes mentioned
- emotional_tone: Overall emotional tone of the movie
- quick_summary: One-line quick summary

Only extract information that is present in the given paragraph. Do not add external knowledge. Return valid JSON only."""),
    ("human", "Paragraph: {paragraph}")
])

model = ChatMistralAI(model="mistral-small-2506", temperature=0.1)
# pydantic output parser check that all info is correct or not 
parser = JsonOutputParser(pydantic_object=MovieInfo)

chain = prompt | model | parser

if __name__ == "__main__":
    sample = (
        "Avengers: Endgame is an epic superhero movie produced by Marvel Studios and directed by "
        "Anthony Russo and Joe Russo. The film follows the remaining Avengers as they try to reverse "
        "the devastating actions of Thanos, who wiped out half of all life in the universe in the "
        "previous movie, Avengers: Infinity War. With the help of time travel and teamwork, heroes "
        "like Iron Man, Captain America, Thor, Hulk, and Black Widow reunite for one final mission "
        "to restore balance and save humanity. The movie is filled with emotional moments, thrilling "
        "action scenes, and powerful sacrifices, making it one of the most memorable films in the "
        "Marvel Cinematic Universe. It also marks the end of an important era for many beloved "
        "characters and delivers a satisfying conclusion to the Infinity Saga."
    )
    result = chain.invoke({"paragraph": sample})
    import json
    print(json.dumps(result, indent=2))
