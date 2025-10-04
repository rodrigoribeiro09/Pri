import os
import requests
from dotenv import load_dotenv
import json
import pandas as pd
import time

load_dotenv()

ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
BASE_URL = "https://api.genius.com"
PROGRESS_FILE = "processData/progress.json"


def save_json_to_txt(data, filename):
    try:
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted_json)
        print(f"JSON data saved to {filename}")
    except Exception as e:
        print("Error saving JSON:", e)

        
def extract_text(dom):
    """
    Recursively extract text from Genius API 'dom' structure.
    """
    if isinstance(dom, str):
        return dom
    elif isinstance(dom, dict):
        text = ""
        if "children" in dom:
            for child in dom["children"]:
                text += extract_text(child)
        return text
    elif isinstance(dom, list):
        return "".join(extract_text(item) for item in dom)
    return ""


def safe_request(url, params=None, retries=3, delay=2):
    """Request with timeout and retry"""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f" API returned {response.status_code}, retry {attempt+1}/{retries}")
        except requests.RequestException as e:
            print(f"Network/API error: {e}, retry {attempt+1}/{retries}")
        time.sleep(delay)
    return None


def get_artist_song_id(song,artist):
    #get the song_id and artist_id

    query = f"{song} {artist}"
    data = safe_request(f"{BASE_URL}/search", params={"q": query})
    if data is None or not data.get("response", {}).get("hits"):
        return None
    hits = data.get("response", {}).get("hits", [])
    if not hits:
        print("No results found.")
        return None
    #Hits[0]- the most aproximated value. Can be wrong i guess
    song_id = hits[0]["result"]["id"]
    artist_id=hits[0]["result"]["primary_artist"]["id"]
    return song_id,artist_id


def get_artist_info(artistId):
    # get the followers and artist descriptions
    data = safe_request(f"{BASE_URL}/artists/{artistId}")
    if data is None:
        return None

    artist = data.get("response", {}).get("artist", {})
    
    artistInfo = artist.get("description", {}) 
    artistName = artist.get("name", "")
    followers = artist.get("followers_count", 0)

    
    plain_text = extract_text(artistInfo.get("dom", []))

    return plain_text, followers, artistName

def get_music_info(musicId):
    data = safe_request(f"{BASE_URL}/songs/{musicId}")
    if data is None:
        return None

    song = data.get("response", {}).get("song", {})


    description = song.get("description", {})

    plain_text = extract_text(description.get("dom", []))
  
    print(f"plain_text,{plain_text}")
    release_date = song.get("release_date", None)

    album = song.get("album", {})

    if not album:
        albumId=0
        albumName="No album Name"
    else:
        albumId = album.get("id", None)
        albumName = album.get("name", "")
    return plain_text, release_date, albumId, albumName


def save_progress(index, artists):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"index": index, "artists": artists}, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"index": 0, "artists": {}}


def getNewProcessData(csv_path,index=0,artist_dict=None):
    print(f"index values {index}")
    os.makedirs("processData", exist_ok=True)
    
    artist_csv = os.path.join("processData", "artist.csv")
    song_csv = os.path.join("processData", "song.csv")
    
    if not os.path.exists(artist_csv):
        pd.DataFrame(columns=["id","api_id" ,"artist_name", "artist_bio", "followers"]).to_csv(artist_csv, index=False)
    if not os.path.exists(song_csv):
        pd.DataFrame(columns=["id","api_id", "artist_id", "lyrics", "music_description", "album_Name", "realease_date"]).to_csv(song_csv, index=False)

    df = pd.read_csv(csv_path)
    c = index
    finished = True
    
    artists = artist_dict if artist_dict is not None else {}
    artist_id = len(artists)
    for _, row in df.iloc[index:].iterrows():
        artist = row['artist']
        song = row['song']
        text = row['text']
        try:
            res = get_artist_song_id(song, artist)
            if res is None:
                print(f" Could not get artist/song IDs for '{song}' / '{artist}' at index {c}")
                c += 1
                continue
            realSongId, realArtistId = res

            print(f"realsong {realSongId} , realArtis {realArtistId}")

            if(not realArtistId in artists.keys()):
                artists[realArtistId]=artist_id
                info = get_artist_info(realArtistId)
                if info is None:
                    print(f"Could not get artist info for {realArtistId} at index {c}")
                    c += 1
                    continue
                plain_textArtist, followers, artistName = info
                pd.DataFrame([[artist_id,realArtistId, artistName,plain_textArtist,followers]], columns=["id","api_id" "artist_name","artist_bio","followers"]).to_csv(
                    artist_csv, mode='a', header=False, index=False
                )
                artist_id+=1
                print(artist_id)
            fakeArtistid=artists[realArtistId]
            music = get_music_info(realSongId)
            if music is None:
                print(f" Could not get music info for {realSongId} at index {c}")
                c += 1
                continue
            plain_textMusic, realease_date, albumId, albumName = music
            pd.DataFrame([[c, realSongId,fakeArtistid,text,plain_textMusic,albumName,realease_date]], columns=["id","api_id", "artist_id","lyrics","music_description","album_Name","realease_date"]).to_csv(
                    song_csv, mode='a', header=False, index=False
                )
            
            c+=1
            save_progress(c, artists)

        except Exception as e:
            print(f" Error at index {c}: {e}")
            print(" You can resume from this index later.")
            finished = False
            break

    return c,artists,finished


def apiLoop(csv_path):
    progress = load_progress()
    index = progress.get("index", 0)
    artists = progress.get("artists", {})
    finished = False

    while not finished:
        index, artists, finished = getNewProcessData(csv_path, index, artists)
        print(f"Processed index: {index}, artists: {len(artists)}")

    print(" All Done!")
        
if __name__ == "__main__":
    
    apiLoop("../dataset/spotify_millsongdata.csv")

  