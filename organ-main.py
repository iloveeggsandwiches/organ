import os
import time
import requests
import json

full = {
    "music": {
        "cassette": [],
        "cd": [],
        "vinyl": [],
        "8 track": [],
        "digital": [],
        "digital-drm": []
    },
    "movies": {
        "dvd": [],
        "VHS": [],
        "blu-ray": [],
        "digital": [],
        "digital-drm": []
    }
}

def add_item(item, category, format, cover_path):
    cat = full.get(category)
    frm = cat.get(format)
    frm.append([item, cover_path])
    print(f"Added {item} to {category},{format}")

def get_all_items_in_selected_format(category, format):
    cat = full.get(category)
    return cat.get(format)

def save_to_json(dict_data, path):
    with open(path, "w") as f:
        json.dump(dict_data, f)
    print("Saved dictionary changes to DB")

def load_json(path):
    global full
    with open(path, "r") as f:
        full = json.load(f)

def delete_item(item, category, format):
    cat = full.get(category)
    frm = cat.get(format)
    frm.remove(item)
    print(f"Removed {item} from {category},{format}")

# ---- MusicBrainz lookup ----

MB_HEADERS = {"User-Agent": "Organ/1.0 (ittimeweskel@gmail.com)"}
MB_BASE = "https://musicbrainz.org/ws/2"
COVER_DIR = "organ/covers"
_last_request = 0.0

# MusicBrainz format name -> (category, format key in your `full` dict)
MB_FORMAT_MAP = {
    "Cassette": ("music", "cassette"),
    "CD": ("music", "cd"),
    "Vinyl": ("music", "vinyl"),
    "8-track cartridge": ("music", "8 track"),
    "Digital Media": ("music", "digital"),
}

def _mb_get(url, params):
    """GET from MusicBrainz, respecting its 1 request/second limit."""
    global _last_request
    wait = 1.0 - (time.time() - _last_request)
    if wait > 0:
        time.sleep(wait)
    r = requests.get(url, params={**params, "fmt": "json"},
                     headers=MB_HEADERS, timeout=10)
    _last_request = time.time()
    r.raise_for_status()
    return r.json()

def fetch_metadata(title, artist=None):
    """Return metadata for the best-matching release, or None."""
    query = f'release:"{title}"'
    if artist:
        query += f' AND artist:"{artist}"'
    data = _mb_get(f"{MB_BASE}/release/", {"query": query, "limit": 5})
    releases = data.get("releases", [])
    if not releases:
        return None

    r = releases[0]
    media = r.get("media", [])
    credits = r.get("artist-credit", [])
    return {
        "mbid": r["id"],
        "title": r.get("title", title),
        "artist": credits[0]["name"] if credits else "Unknown",
        "date": r.get("date", ""),
        "format": media[0].get("format") if media else None,
    }

def download_cover(mbid):
    """Download the front cover from the Cover Art Archive. Returns a path or None."""
    os.makedirs(COVER_DIR, exist_ok=True)
    url = f"https://coverartarchive.org/release/{mbid}/front-500"
    r = requests.get(url, headers=MB_HEADERS, timeout=15)
    if r.status_code != 200:
        return None
    ext = ".png" if "png" in r.headers.get("Content-Type", "") else ".jpg"
    path = os.path.join(COVER_DIR, mbid + ext)
    with open(path, "wb") as f:
        f.write(r.content)
    return path

def add_music_auto(title, artist=None):
    """Look up a music release on MusicBrainz and add it to the collection."""
    meta = fetch_metadata(title, artist)
    if meta is None:
        print(f"No MusicBrainz match for {title}")
        return
    key = MB_FORMAT_MAP.get(meta["format"])
    if key is None:
        print(f"Unmapped format '{meta['format']}' for {meta['title']}")
        return
    category, fmt = key
    year = meta["date"][:4]
    label = f"{meta['artist']} - {meta['title']}" + (f" ({year})" if year else "")
    cover = download_cover(meta["mbid"])
    add_item(label, category, fmt, cover)

# ---- Main ----

load_json("organ/db.json")

add_music_auto("Abbey Road", "The Beatles")

save_to_json(full, "organ/db.json")