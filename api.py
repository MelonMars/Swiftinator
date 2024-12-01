from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
import json, marqo

mq = marqo.Client(url="http://localhost:8882")

class Themes(BaseModel):
    themes: list[str]
    emotions: list[str]
    query_rewrite: list[str]

class FinalResponse(BaseModel):
    lyrics: str
    song: str

app = FastAPI()

keys = json.load(open("env/keys.json", "r"))
client = OpenAI(
    api_key=keys["OpenAI"]
)

@app.get("/get_quote")
def get_quote(query: str):
    """
    query: What the user is looking for

    Authenticate User -> Get query -> LLM (extract high and low level info about it) -> Marqo query -> Ask LLM to get specific lyrics for it -> return to user
    """
    print(f"Received query: {query}")
    themes = get_themes(query)
    print(f"Extracted themes: {themes}")

    results = search_marqo(themes)
    print(f"Search results from Marqo: {results}")

    final_response = get_lyrics(results[0], themes)
    return final_response # CHANGE THIS TO MORE USEABLE FROM THE FRONTEND

def get_themes(query):
    print(f"Getting themes for query: {query}")
    response = client.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """The user is looking for lyrics matching a specific theme or idea. Extract key themes and emotions. Provide output in JSON format:
1. "themes" - High-level thematic keywords.
2. "emotions" - Emotional undertones.
3. "query_rewrite" - A rewritten version of the query optimized for semantic search.
"""},
            {"role": "user", "content": "Give me lyrics about achieving greatness"},
            {"role": "assisant", "content": """
{
  "themes": ["achievement", "greatness", "success"],
  "emotions": ["motivation", "triumph", "pride"],
  "query_rewrite": "Songs about achieving greatness, success, or personal triumph."
}
"""},
            {"role": "user", "content": "What's a good song about heartbreak?"},
            {"role": "assisant", "content": """
{
  "themes": ["heartbreak", "loss", "grief"],
  "emotions": ["sadness", "melancholy", "longing"],
  "query_rewrite": "Songs about heartbreak, loss, or longing."
}
"""},
            {"role": "user", "content": "Lyrics that feel like flying through a fiery sky."},
            {"role": "assistant", "content": """
{
  "themes": ["freedom", "intensity", "transcendence"],
  "emotions": ["exhilaration", "passion", "defiance"],
  "symbolic_meaning": "Experiencing freedom and intense emotions in the face of adversity.",
  "query_rewrite": "Songs about freedom, intensity, or transcendence in challenging situations."
}
"""},
            {"role": "user", "content": query}
        ],
        max_new_tokens=1000,
        response_format=Themes,
    )

    themes = response.choices[0].message.content
    print(f"Received themes from OpenAI: {themes}")
    return themes

def search_marqo(query):
    print(f"Searching Marqo with query: {query}")
    results = mq.index("song").search(
        q=query,
        searchable_attributes=["lyrics", "themes", "summary", "tone"],
        boosts={"lyrics": 1, "themes": 1.5, "tone": 1.5},
        limit=5
    )

    print(f"Marqo search results: {results}")
    return results["hit"]

def get_lyrics(query, themes):
    print(f"Getting lyrics for query: {query} with themes: {themes}")
    response = client.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "The user is looking for some lyrics to match a prompt in their song. Provide the lyrics in response. Keep in mind that the user's inputs have been formatted into JSON to allow easy use. Also make sure that you provide the name of the song, which you should already be given"},
            {"role": "user", "content": f"I have the song: {query} and want to find out about {themes}"}
        ],  
        response_format=FinalResponse,
    )

    lyrics = response.choices[0].message.content
    print(f"Received lyrics from OpenAI: {lyrics}")
    return lyrics