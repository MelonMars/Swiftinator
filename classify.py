from tooldantic import OpenAiResponseFormatBaseModel as BaseModel
from openai import OpenAI
import json

class Song(BaseModel):
    title: str
    artist: str
    album: str
    lyrics: str
    themes: list[str]
    tone: str
    summary: str

songs = json.load(open("songs.json", "r"))
songs = [song[1] for song in songs.items()]
songs = [song.replace("\u2005", "REPLACETHIS") for song in songs]
songs = [song.replace("\u2019", "\'") for song in songs]

def prepare_jsonl():
    jsonl = []
    for i, song in enumerate(songs):
        jsonl.append(
            {
                'custom_id': f'request-{i}',
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-3.5-turbo-16k",
                    "max_new_tokens": 1000,
                    "messages": [
                        {"role": "system", "content": "You are a music critic, categorizing and labeling a song. You need to provide the song's title, artist, album, lyrics, themes, tone, and a summary."},
                        {"role": "user", "content": song},
                        ],
                    "response_format": Song.model_json_schema(),
                },
            }
        )
    return jsonl

with open("requests.jsonl", "w") as f:
    for line in prepare_jsonl():
        f.write(json.dumps(line) + "\n")

keys = json.load(open("env/keys.json", "r"))
client = OpenAI(
    api_key=keys["OpenAI"]
)

batch_file = client.files.create(
    file=open("requests.jsonl", "rb"),
    purpose="batch"
)

batch_job = client.batches.create(
  input_file_id=batch_file.id,
  endpoint="/v1/chat/completions",
  completion_window="24h"
)

print("Created batch job:", batch_job.id)