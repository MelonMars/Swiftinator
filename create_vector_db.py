import json, marqo

mq = marqo.Client(url="http://localhost:8882")
try:
    mq.index("songs").delete()
except:
    pass
mq.create_index("songs", model="hf/e5-base-v2")

songs = json.load(open("master_songs.json", "r"))
for song_title in songs.keys():
    song = songs[song_title]
    add_result = mq.index("songs").add_documents([{
        "title": song_title,
        "tone": song["tone"],
        "themes": ", ".join(song["themes"]),
        "summary": song["summary"],
        "original_lyrics": song["original_lyrics"]
    }],
    tensor_fields=["themes", "tone", "summary", "original_lyrics"])
    print(add_result)

results = mq.index("songs").search("melancholic and reflective", attributes_to_retrieve=["lyrics"])
print(results)