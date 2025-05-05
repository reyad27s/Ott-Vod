import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    "API-KEY": "ottbangla@android",
    "Authorization": "Basic YWRtaW46MTIzNA==",
    "Host": "otapp.store",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/4.9.0"
}

def fetch_movies(page=1):
    url = f"https://otapp.store/rest-api/v130/movies?page={page}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        elif isinstance(data, list):
            return data
        else:
            return []
    except:
        return []

def fetch_single_movie_details(movie_id):
    url = f"https://otapp.store/rest-api/v130/single_details?type=movie&id={movie_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except:
        return {}

def extract_stream_link(details):
    videos = details.get("videos", [])
    if videos and isinstance(videos, list):
        for vid in videos:
            link = vid.get("file_url", "")
            if link.startswith("http"):
                return link
    return None

def create_m3u_entry(title, logo, stream_link):
    return f'#EXTINF:-1 tvg-logo="{logo}",{title}\n{stream_link}'

def save_m3u(entries, file_name="ottbanglavod.m3u"):
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for entry in entries:
                f.write(entry + "\n")
        print(f"Saved {len(entries)} entries to M3U.")
    except Exception as e:
        print("Failed to save file:", e)

def process_movie(movie):
    movie_id = movie.get("id") or movie.get("videos_id")
    if not movie_id:
        return None
    details = fetch_single_movie_details(movie_id)
    if not details:
        return None
    title = details.get("title", "No Title").strip()
    logo = details.get("poster_url", "").strip()
    stream_link = extract_stream_link(details)
    if stream_link:
        print(f"OK: {title}")
        return create_m3u_entry(title, logo, stream_link)
    return None

# প্রধান প্রসেসিং
all_m3u_entries = []

for page in range(1, 47):
    print(f"\nCollecting page {page}...")
    movies = fetch_movies(page)
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(process_movie, movie) for movie in movies]
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_m3u_entries.append(result)
    time.sleep(0.5)

save_m3u(all_m3u_entries)