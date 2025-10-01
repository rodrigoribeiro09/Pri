import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
BASE_URL = "https://api.genius.com"


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



def get_artist_song_id(song,artist):
    #get the song_id and artist_id

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    query = f"{song} {artist}"
    response = requests.get(f"{BASE_URL}/search", headers=headers, params={"q": query})
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None
    hits = response.json()["response"]["hits"]
    if not hits:
        print("No results found.")
        return None
    #Hits[0]- the most aproximated value. Can be wrong i guess
    song_id = hits[0]["result"]["id"]
    artist_id=hits[0]["result"]["primary_artist"]["id"]
    return song_id,artist_id


def get_artist_info(artistId):
    #get the followers and artist descriptions

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(f"{BASE_URL}/artists/{artistId}", headers=headers)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None
   
    artistInfo=response.json()["response"]["artist"]["description"]
    artistName=response.json()["response"]["artist"]["name"]
    followers=response.json()["response"]["artist"]["followers_count"]# Add if needed
    plain_text = extract_text(artistInfo["dom"])
    return plain_text,followers,artistName


def get_music_info(musicId):
    # get musicDescription,realease_date,albumId,albumName
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(f"{BASE_URL}/songs/{musicId}", headers=headers)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None
    data = response.json()
    musicDescription=data["response"]["song"]["description"]["dom"]
    plain_text = extract_text(musicDescription)
    realease_date=data["response"]["song"]["release_date"]
    albumId=data["response"]["song"]["album"]["id"]
    albumName=data["response"]["song"]["album"]["name"]
    return plain_text,realease_date,albumId,albumName
  

#Working but not doing nothing the txt is just to check the json atributes
def get_album_info(albumId):
    # get musicDescription,realease_date,albumId,albumName
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(f"{BASE_URL}/albums/{albumId}", headers=headers)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None
    data = response.json()
    save_json_to_txt(data,"album")
  

if __name__ == "__main__":
    
    song_id,artist_id = get_artist_song_id("Hello", "Adele")
    plain_text,followers,artistName=get_artist_info(artist_id)
    print(plain_text,followers,artistName)
    
  
