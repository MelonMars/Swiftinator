import pandas as pd
import os, re, json

albumsFolder = 'SongsNonprocessed/Albums'
albums = os.listdir(albumsFolder)
print(f"Albums: {albums}")

all_songs = {}
unique_songs = set()

for album in albums:
    songFolder = 'SongsNonprocessed/Albums/{0}'.format(album)
    songs = os.listdir(songFolder)
    print(f"Songs in {album}: {songs}")

    for song in songs:
        songPath = 'SongsNonprocessed/Albums/{0}/{1}'.format(album, song)
        with open(songPath, 'r') as file:
            lines = file.readlines()
            song_text = ''.join(lines[1:])
            song_text = re.sub(r'\d+Embed$', '', song_text)

        if song_text not in unique_songs:
            print(f"Song: {song}")
            print(f"Song text: {song_text}")
            unique_songs.add(song_text)
            all_songs[song.replace(".txt", "")] = song_text

with open("songs.json", "w") as file:
    file.write(json.dumps(all_songs))