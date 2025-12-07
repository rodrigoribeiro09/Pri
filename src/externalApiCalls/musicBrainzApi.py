import requests
import time
import pandas as pd

MB_API = "https://musicbrainz.org/ws/2/artist"
def mb_search_artist(name, retries=3):
    if not name:
        return None

    params = {"query": name, "fmt": "json", "limit": 5}
    headers = {"User-Agent": "ArtistCountryEnricher/1.0 (teu-email@dominio.com)"}

    for attempt in range(retries):
        try:
            resp = requests.get(MB_API, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            artists = data.get("artists", [])
            if not artists:
                return None
            best = max(artists, key=lambda a: int(a.get("score", 0)))
            return best
        except requests.RequestException as e:
            time.sleep(0 + 0.05*attempt)  
    return None


def enrich_artists_with_country(input_csv, output_csv, sleep=1.0):
    """Enriquece um CSV de artistas com país (ISO code e nome)."""
    df = pd.read_csv(input_csv, dtype=str)
    countries = []
    country_codes = []

    for _, row in df.iterrows():
        name = str(row.get("artist_name", "") or "").strip()
        country = ""
        code = ""

        if name:
            time.sleep(sleep)  
            artist = mb_search_artist(name)
            if artist:
                code = artist.get("country") or ""
                area = artist.get("area") or {}
                country = area.get("name") or code  
            print(f"  Artist: {name}, Country: {country}, Code: {code}")

        countries.append(country)
        country_codes.append(code)

    df["artist_country"] = countries
    df["artist_country_code"] = country_codes
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"✅ Saved enriched artists to {output_csv}")


if __name__ == "__main__":
    enrich_artists_with_country("dataset/artist.csv", "dataset/artists_enriched.csv", sleep=0.005)
