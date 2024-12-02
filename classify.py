from tooldantic import OpenAiResponseFormatBaseModel as BaseModel
import json, requests

class Song(BaseModel):
    themes: list[str]
    tone: str
    summary: str

songs = json.load(open("songs.json", "r"))
songs = [song[1] for song in songs.items()]
songs = [song.replace("\u2005", "REPLACETHIS") for song in songs]
songs = [song.replace("\u2019", "\'") for song in songs]

song_titles = [title for title in json.load(open("songs.json", "r")).keys()]

total_songs = len(songs)

master_songs = json.load(open("master_songs.json", "r"))
for i, (song, song_title) in enumerate(zip(songs[298:], song_titles[298:])):
    print(f"Classifying song: {song_title}")
    print(f"Progress: {i}/{total_songs-298}")
    payload = {
        "model": "phi-3.1-mini-128k-instruct",
        "messages": [
            {"role": "system", "content": """You are a music enthusiast who wants to classify songs into themes, tone, and summary. You will be provided with a song title and lyrics. You will then need to come up with the themes, tone, and summary of the song. Provide output in JSON format."""},
            {"role": "user", "content": f"Classify the song {song_title}, with lyrics: {song}"},
        ],
        "max_new_tokens": 100,
        "response_format": Song.model_json_schema()
    }
    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload)
    response_json = response.json() 
    try:
        output = response_json["choices"][0]["message"]["content"]
    except:
        print("Error in response")
        continue
    output_json = json.loads(output)
    output_json["original_lyrics"] = song
    
    master_songs[song_title] = output_json
    with open("master_songs.json", "w") as f:
        f.seek(0)
        json.dump(master_songs, f)

print("All songs classified and saved to master_songs.json")