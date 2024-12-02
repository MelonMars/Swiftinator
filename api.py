from fastapi import FastAPI
from openai import OpenAI
from tooldantic import OpenAiResponseFormatBaseModel as BaseModel
import json, marqo
import requests

mq = marqo.Client(url="http://localhost:8882")

class Themes(BaseModel):
    themes: list[str]
    emotions: list[str]
    query_rewrite: str

class FinalResponse(BaseModel):
    lyrics: str
    song: str

app = FastAPI()

# keys = json.load(open("env/keys.json", "r"))
# client = OpenAI(
#     api_key=keys["OpenAI"]
# )

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

    final_response = get_lyrics(results['title'], themes)
    return final_response

def get_themes(query):
    print(f"Getting themes for query: {query}")
    payload = {
        "model": "phi-3.1-mini-128k-instruct",
        "messages": [
            {"role": "system", "content": """The user is looking for lyrics matching a specific theme or idea. Extract key themes and emotions. Provide output in JSON format:
1. "themes" - High-level thematic keywords.
2. "emotions" - Emotional undertones.
3. "query_rewrite" - A rewritten version of the query optimized for semantic search.
"""},
            {"role": "user", "content": "Give me lyrics about achieving greatness"},
            {"role": "assistant", "content": """
{
  "themes": ["achievement", "greatness", "success"],
  "emotions": ["motivation", "triumph", "pride"],
  "query_rewrite": "Songs about achieving greatness, success, or personal triumph."
}
"""},
            {"role": "user", "content": "What's a good song about heartbreak?"},
            {"role": "assistant", "content": """
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
        "max_new_tokens": 1000,
        "response_format": Themes.model_json_schema()
    }

    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload)
    response_json = response.json()
    themes = response_json["choices"][0]["message"]["content"]
    print(f"Received themes from local model: {themes}")
    return themes

def search_marqo(query):
    print(f"Searching Marqo with query: {query}")
    results = mq.index("songs").search(
        q=query,
        searchable_attributes=["original_lyrics", "themes", "summary", "tone"],
        attributes_to_retrieve=["title", "lyrics"]
    )

    print(f"Marqo search results: {results}")
    return results["hits"][0]

def get_lyrics(query, themes):
    print(f"Getting lyrics for query: {query} with themes: {themes}")
    with open("master_songs.json", "r") as f:
        songs = json.load(f)
    song = songs[query]['original_lyrics']
    payload = {
        "model": "phi-3.1-mini-128k-instruct",
        "messages": [
            {"role": "system", "content": "The user is looking for some lyrics to match a prompt in their song. Provide the lyrics in response. Keep in mind that the user's inputs have been formatted into JSON to allow easy use. Also make sure that you provide the name of the song, which you should already be given. Keep the selected portion of the song short, returning less than  30 words. And only return lyrics from the song, nothing else."},
            {"role": "user", "content": f"I have the song: {song} and want to find out about {themes}"}
        ],  
        "response_format": FinalResponse.model_json_schema(),
        "max_new_tokens": 250
    }
    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload)
    response_json = response.json()
    output = response_json["choices"][0]["message"]["content"]
    output_json = json.loads(output)
    print(f"Received lyrics: {output_json}")
    return output_json

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)