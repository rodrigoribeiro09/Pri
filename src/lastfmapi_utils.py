API_KEY = "a97ff83c0dd165c5e767e8bed7751dbb"
SHARED_SECRET = "488a9e1eb21f17798beb5ec19d35c407"

"""Utilities for interacting with the Last.fm API.

This module provides small helper functions used by the project to search for
tracks, and fetch artist and track metadata using the Last.fm web API.

API root: http://ws.audioscrobbler.com/2.0/
"""

import requests
import time
import html
import re
from typing import Optional, Tuple, Dict, Any
import os
import json
import pandas as pd

API_ROOT = "http://ws.audioscrobbler.com/2.0/"


def _clean_html(text: Optional[str]) -> str:
	"""Remove simple HTML tags and unescape HTML entities.

	Last.fm returns wiki/html content in some fields; strip tags and unescape
	to get plain text suitable for CSV/storage.
	"""
	if not text:
		return ""
	# Remove HTML tags
	clean = re.sub(r"<[^>]+>", "", text)
	# Unescape HTML entities
	return html.unescape(clean).strip()


def _safe_request(params: Dict[str, Any], retries: int = 3, delay: float = 1.0) -> Optional[Dict[str, Any]]:
	"""Call the Last.fm API endpoint with provided params and return parsed JSON.

	The params dict should include the 'method' key (e.g. 'track.getInfo').
	This function adds the api_key and format=json automatically and retries
	on transient network errors.
	"""
	params = dict(params)
	params.setdefault("api_key", API_KEY)
	params.setdefault("format", "json")

	for attempt in range(1, retries + 1):
		try:
			resp = requests.get(API_ROOT, params=params, timeout=10)
			if resp.status_code == 200:
				return resp.json()
			else:
				print(f"Last.fm API returned status {resp.status_code} (attempt {attempt}/{retries})")
		except requests.RequestException as e:
			print(f"Network error contacting Last.fm API: {e} (attempt {attempt}/{retries})")

		if attempt < retries:
			time.sleep(delay)

	return None


def search_track(track: str, artist: Optional[str] = None) -> Optional[Tuple[Optional[str], Optional[str], str, str]]:
	"""Search for a track on Last.fm.

	Returns (track_mbid, artist_mbid, track_name, artist_name) for the best
	match (first result). MBIDs may be None if not present. Returns None on
	failure or when no match is found.
	"""
	params = {"method": "track.search", "track": track, "limit": 5}
	if artist:
		params["artist"] = artist

	data = _safe_request(params)
	if not data:
		return None

	results = data.get("results", {})
	matches = results.get("trackmatches", {}).get("track", [])
	if not matches:
		return None

	# matches can be a dict when there's a single result
	best = matches if isinstance(matches, dict) else matches[0]

	track_name = best.get("name", track)
	artist_name = best.get("artist", artist or "")
	track_mbid = best.get("mbid") or None
	artist_mbid = None
	return track_mbid, artist_mbid, track_name, artist_name


def get_artist_info(artist_name: Optional[str] = None, artist_mbid: Optional[str] = None, _retry: bool = False) -> Optional[Tuple[str, int, str]]:
    if not artist_name and not artist_mbid:
        return None

    params = {"method": "artist.getInfo"}
    if artist_mbid:
        params["mbid"] = artist_mbid
    else:
        params["artist"] = artist_name

    data = _safe_request(params)
    if not data:
        return None

    artist = data.get("artist") or data.get("response", {}).get("artist")
    if not artist:
        return None

    bio = artist.get("bio", {})
    bio_text = _clean_html(bio.get("summary") or bio.get("content") or "")

    # Se for "incorrect tag", tenta extrair o nome correto e repetir a consulta
    if bio_text.lower().startswith("this is an incorrect tag") and not _retry:
        # Tenta extrair o nome correto do texto, ex: "*NSYNC"
        m = re.search(r"incorrect tag for ([\*\w\s\.\-&']+)", bio_text, re.IGNORECASE)
        if m:
            correct_name = m.group(1).strip()
            # Evita loop infinito
            return get_artist_info(artist_name=correct_name, _retry=True)
        else:
            bio_text = ""  # Não conseguiu extrair, devolve vazio

    stats = artist.get("stats", {})
    try:
        listeners = int(stats.get("listeners", 0))
    except Exception:
        listeners = 0

    name = artist.get("name") or artist_name or ""
    return bio_text, listeners, name


def get_track_info(track_name: Optional[str] = None, artist_name: Optional[str] = None, track_mbid: Optional[str] = None) -> Optional[Tuple[str, Optional[str], Optional[str], str]]:
	"""Fetch track information from Last.fm.

	Either provide track_mbid or both track_name and artist_name.
	Returns (description, release_date, album_mbid_or_0, album_name) or None on failure.
	"""
	if not track_mbid and (not track_name or not artist_name):
		raise ValueError("Either track_mbid or (track_name and artist_name) must be provided")

	params = {"method": "track.getInfo"}
	if track_mbid:
		params["mbid"] = track_mbid
	else:
		params["track"] = track_name
		params["artist"] = artist_name

	data = _safe_request(params)
	if not data:
		return None

	track = data.get("track")
	if not track:
		return None

	wiki = track.get("wiki", {})
	description = _clean_html(wiki.get("content") or wiki.get("summary") or "")
	release_date = wiki.get("published") if wiki else None

	album = track.get("album") or {}
	album_name = album.get("title") or "No album Name"
	album_mbid = album.get("mbid") or 0

	return description, release_date, album_mbid, album_name


# ------------------ CSV augmentation helpers ------------------


def _save_progress(last_index: int, progress_file: str, cache: Dict[str, Any]):
	os.makedirs(os.path.dirname(progress_file), exist_ok=True)
	with open(progress_file, "w", encoding="utf-8") as f:
		json.dump({"last_index": last_index, "cache": cache}, f, ensure_ascii=False, indent=2)


def _load_progress(progress_file: str) -> Tuple[int, Dict[str, Any]]:
	if os.path.exists(progress_file):
		with open(progress_file, "r", encoding="utf-8") as f:
			data = json.load(f)
			return data.get("last_index", 0), data.get("cache", {})
	return 0, {}


def augment_csv_with_lastfm(
    csv_path: str,
    out_csv_path: Optional[str] = None,
    start_index: int = 0,
    chunk_size: int = 200,
    progress_file: str = "processData/lastfm_progress.json",
    overwrite: bool = False,
    sleep_between_calls: float = 0.2,
) -> None:
    """Augment the input CSV with Last.fm fields and write to out_csv_path.

	This function processes the file in chunks (to handle large files), and
	writes an output CSV that contains the original columns plus the following
	new fields:

	- lastfm_track_mbid
	- lastfm_artist_mbid
	- lastfm_artist_name
	- lastfm_artist_bio
	- lastfm_artist_listeners
	- lastfm_track_description
	- lastfm_release_date
	- lastfm_album_mbid
	- lastfm_album_name

	The function supports resuming using `progress_file` which stores the last
	processed row index and a small cache for artist info to avoid repeated
	API calls.
	"""
    if out_csv_path is None:
        out_csv_path = csv_path.replace(".csv", "_with_lastfm.csv")
    # two outputs: songs and artists
    songs_out_path = out_csv_path
    artists_out_path = out_csv_path.replace('.csv', '_artists.csv')

    if overwrite and os.path.exists(out_csv_path):
        os.remove(out_csv_path)

    os.makedirs(os.path.dirname(progress_file), exist_ok=True)
    last_index_saved, cache = _load_progress(progress_file)
    if last_index_saved > start_index:
        start_index = last_index_saved

    cols_to_add = [
        "lastfm_track_description",
        "lastfm_release_date",
        "lastfm_album_name",
    ]

    reader = pd.read_csv(csv_path, chunksize=chunk_size, iterator=True, dtype=str, encoding="utf-8")

    # song output write control
    first_write = True
    # artist output write control
    first_write_art = True
    # track which artist ids have already been written to artists_out
    artists_written = set(cache.get('__artists_written__', []))

    # artist id mapping persisted in cache under key '__artist_id_map__'
    artist_id_map = cache.get('__artist_id_map__', {})
    # determine starting counter for generated ids
    def _max_id(map_dict):
        mx = 0
        for v in map_dict.values():
            try:
                iv = int(v)
                if iv > mx:
                    mx = iv
            except Exception:
                pass
        return mx
    artist_id_counter = max(_max_id(artist_id_map) + 1, 1)
    processed = 0
    global_index = 0

    for chunk in reader:
        n = len(chunk)
        if global_index + n <= start_index:
            global_index += n
            continue

        start_in_chunk = max(0, start_index - global_index)
        end_in_chunk = n

        # helper para escolher o primeiro valor não vazio/não-NaN
        def _first_nonempty(*vals):
            for v in vals:
                if v is None:
                    continue
                try:
                    if pd.isna(v):
                        continue
                except Exception:
                    pass
                s = str(v).strip()
                if s:
                    return s
            return ""

        new_rows = []
        new_artist_rows = []
        for i in range(start_in_chunk, end_in_chunk):
            row = chunk.iloc[i]
            idx = global_index + i

            # ler colunas de forma robusta a NaN
            song = _first_nonempty(row.get("song"), row.get("track"))
            artist = _first_nonempty(row.get("artist"))

            try:
                if sleep_between_calls:
                    time.sleep(sleep_between_calls)
                res = search_track(song, artist)
                if res is None:
                    track_mbid = None
                    artist_mbid = None
                    track_name = song
                    artist_name = artist
                else:
                    track_mbid, artist_mbid, track_name, artist_name = res

                cache_key = (artist_name or artist).lower()
                cached = cache.get(cache_key)
                artist_bio = ""
                artist_listeners = 0
                artist_name_clean = artist_name or artist or ""
                cached_artist_id = None
                if cached:
                    # handle previous tuple formats (bio,listeners,name) or extended with id
                    try:
                        if isinstance(cached, (list, tuple)) and len(cached) >= 3:
                            artist_bio, artist_listeners, artist_name_clean = cached[0], cached[1], cached[2]
                            if len(cached) >= 4:
                                cached_artist_id = cached[3]
                        else:
                            # unknown cached format: ignore
                            pass
                    except Exception:
                        pass
                else:
                    if sleep_between_calls:
                        time.sleep(sleep_between_calls)
                    artist_info = get_artist_info(artist_name=artist_name or artist, artist_mbid=artist_mbid)
                    if artist_info is None:
                        artist_bio, artist_listeners, artist_name_clean = "", 0, artist_name or artist or ""
                    else:
                        artist_bio, artist_listeners, artist_name_clean = artist_info
                    # no id yet; will set below
                    cached_artist_id = None

                # determine artist id: prefer input id columns if present, then cached id, else mapping
                input_artist_id = None
                for cand in ('artist_id', 'id'):
                    try:
                        v = row.get(cand)
                        if v is not None and str(v).strip():
                            input_artist_id = str(v).strip()
                            break
                    except Exception:
                        pass

                if input_artist_id:
                    artist_id_final = input_artist_id
                elif cached_artist_id:
                    artist_id_final = str(cached_artist_id)
                else:
                    # try map by cleaned name
                    name_key = artist_name_clean.lower().strip()
                    if name_key in artist_id_map:
                        artist_id_final = str(artist_id_map[name_key])
                    else:
                        artist_id_final = str(artist_id_counter)
                        artist_id_counter += 1
                        artist_id_map[name_key] = artist_id_final

                # update cache with extended info including id
                cache[cache_key] = (artist_bio, artist_listeners, artist_name_clean, artist_id_final)

                if sleep_between_calls:
                    time.sleep(sleep_between_calls)
                track_info = get_track_info(track_name=track_name, artist_name=artist_name_clean, track_mbid=track_mbid)
                if track_info is None:
                    track_description, release_date, album_mbid, album_name = "", None, 0, ""
                else:
                    track_description, release_date, album_mbid, album_name = track_info

                # Build only LASTFM columns for songs output (avoid duplicating artist/song/link/text)
                new_rows.append({
                    "lastfm_track_description": track_description,
                    "lastfm_release_date": release_date,
                    "lastfm_album_name": album_name,
                })

                # prepare artist row (unique)
                artist_record = {
                    "id": artist_id_final,
                    "artist": artist_name_clean or artist,
                    "lastfm_artist": artist_name_clean or artist,
                    "lastfm_artist_bio": artist_bio,
                }
                # only add to new_artist_rows if not already written or seen in this chunk
                if artist_id_final not in artists_written:
                    new_artist_rows.append(artist_record)
                    artists_written.add(artist_id_final)

            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                # append empty LASTFM columns on error (keeps column alignment)
                new_rows.append({c: "" for c in cols_to_add})

            processed += 1
            if processed % (chunk_size * 2) == 0:
                _save_progress(idx + 1, progress_file, cache)

        added_df = pd.DataFrame(new_rows, index=chunk.index[start_in_chunk:end_in_chunk])
        # keep original columns (artist,song,link,text,...) and append only the LASTFM fields
        out_df = pd.concat([chunk.iloc[start_in_chunk:end_in_chunk].reset_index(drop=True), added_df.reset_index(drop=True)], axis=1)

        # write songs output
        out_df.to_csv(songs_out_path, mode='a', header=first_write, index=False, encoding='utf-8')
        first_write = False

        # write new artist rows (unique)
        if new_artist_rows:
            art_df = pd.DataFrame(new_artist_rows)
            art_df.to_csv(artists_out_path, mode='a', header=first_write_art, index=False, encoding='utf-8')
            first_write_art = False

        # persist artist mapping and written set into cache so resume works
        cache['__artists_written__'] = list(artists_written)
        cache['__artist_id_map__'] = artist_id_map

        global_index += n
        _save_progress(global_index, progress_file, cache)

    print(f"Finished augmenting CSV. Output written to {out_csv_path}")
