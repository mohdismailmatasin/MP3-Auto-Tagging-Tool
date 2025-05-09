import os
import sys
import subprocess

# Constants
REQUIRED_MODULES = ["requests", "eyed3"]

def check_and_install_modules():
    """Check if required modules are installed, and install them if not."""
    for module in REQUIRED_MODULES:
        try:
            __import__(module)
        except ImportError:
            print(f"📦 Installing missing module: {module}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])

# Run the module check before importing external modules
check_and_install_modules()

import re
import time
import tempfile
import requests
import eyed3

# Constants
MUSICBRAINZ_API_URL = "https://musicbrainz.org/ws/2/"
USER_AGENT = {"User-Agent": "AutoMP3Tagger/1.0 (contact@example.com)"}

def is_mp3(file_path):
    """Check if the file is an MP3."""
    return file_path.lower().endswith(".mp3")

def embed_artwork(audiofile, release_id):
    """Embed album artwork into the MP3 file."""
    try:
        url = f"http://coverartarchive.org/release/{release_id}/front"
        response = requests.get(url)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False) as img_file:
                img_file.write(response.content)
                img_path = img_file.name
            with open(img_path, "rb") as albumart:
                audiofile.tag.images.set(3, albumart.read(), "image/jpeg", u"Cover")
                audiofile.tag.save()
                print("🎨 Artwork embedded.")
        else:
            print("⚠️ No artwork found.")
    except Exception as e:
        print(f"Artwork error: {e}")

def clean_title(filename):
    """Clean the title by removing track numbers and extra characters."""
    name = os.path.splitext(os.path.basename(filename))[0]
    return re.sub(r"^\d+\s*[-.]?\s*", "", name).strip()

def search_artist(artist_name):
    """Search for an artist using the MusicBrainz API."""
    try:
        params = {"query": artist_name, "fmt": "json"}
        response = requests.get(f"{MUSICBRAINZ_API_URL}artist", headers=USER_AGENT, params=params)
        response.raise_for_status()
        return response.json().get("artists", [])
    except Exception as e:
        print(f"❌ Error searching for artist: {e}")
        return []

def get_albums_by_artist(artist_id):
    """Fetch albums by artist ID and filter for official albums."""
    try:
        params = {"artist": artist_id, "fmt": "json", "limit": 100, "type": "album"}
        response = requests.get(f"{MUSICBRAINZ_API_URL}release-group", headers=USER_AGENT, params=params)
        response.raise_for_status()
        albums = response.json().get("release-groups", [])

        # Filter for official albums and remove duplicates by title
        unique_albums = {}
        for album in albums:
            if album.get("primary-type") == "Album" and not album.get("secondary-types"):
                title = album.get("title", "Unknown Title")
                release_date = album.get("first-release-date", "Unknown Date")
                if title not in unique_albums or release_date < unique_albums[title]["first-release-date"]:
                    unique_albums[title] = {
                        "title": title,
                        "first-release-date": release_date,
                        "id": album.get("id")
                    }

        return sorted(unique_albums.values(), key=lambda x: x["first-release-date"])
    except Exception as e:
        print(f"❌ Error fetching albums: {e}")
        return []

def guess_artist_from_directory(directory_name):
    """Guess the artist based on the directory name."""
    print(f"🤔 Guessing artist based on directory name: {directory_name}")
    artists = search_artist(directory_name)
    if artists:
        print(f"✔ Found potential matches for '{directory_name}':")
        for i, artist in enumerate(artists[:5], 1):  # Show top 5 matches
            print(f"{i}. {artist['name']} (ID: {artist['id']})")
        choice = input("Enter the number of the correct artist (or press Enter to skip): ")
        if choice.strip().isdigit():
            choice = int(choice)
            if 1 <= choice <= len(artists):
                return artists[choice - 1]
    print("❌ No artist selected. Skipping.")
    return None

def select_album(albums):
    """Allow the user to select an album or go back."""
    if not albums:
        print("❌ No albums found.")
        return None

    while True:
        print("\nChoose an album to tag files:")
        for i, album in enumerate(albums):
            print(f"{i + 1}. {album['title']} ({album['first-release-date']})")
        print("0. Back")

        choice = input("Enter album number: ")
        if choice.strip().isdigit():
            choice = int(choice)
            if choice == 0:
                return "back"
            elif 1 <= choice <= len(albums):
                return albums[choice - 1]
        print("❌ Invalid selection. Please try again.")

def tag_file(file_path, album, artist_name):
    """Tag an MP3 file with metadata."""
    print(f"\nProcessing: {file_path}")
    audiofile = eyed3.load(file_path)
    if not audiofile:
        print("❌ Could not load file.")
        return

    try:
        audiofile.tag = audiofile.tag or eyed3.id3.Tag()
        audiofile.tag.title = clean_title(file_path)
        audiofile.tag.artist = album.get('artist-credit', [{}])[0].get('name', artist_name)
        audiofile.tag.album = album['title']
        audiofile.tag.save()

        print(f"✔ Tagged: {audiofile.tag.title} - {audiofile.tag.artist} | Album: {audiofile.tag.album}")
        embed_artwork(audiofile, album['id'])
    except Exception as e:
        print(f"❌ Error tagging file: {e}")

def scan_path(path, album, artist_name):
    """Scan a directory or file and tag MP3 files."""
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                if is_mp3(full_path):
                    tag_file(full_path, album, artist_name)
    elif os.path.isfile(path) and is_mp3(path):
        tag_file(path, album, artist_name)
    else:
        print(f"Skipping unsupported file: {path}")

def choose_input_mode():
    """Allow the user to choose between manual input or auto-guessing."""
    while True:
        print("\nChoose input mode:")
        print("1. Auto-guess artist from directory name")
        print("2. Manually input artist name")
        choice = input("Enter your choice (1 or 2): ")
        if choice.strip() in ["1", "2"]:
            return int(choice)
        print("❌ Invalid selection. Please choose 1 or 2.")

if __name__ == "__main__":
    while True:
        input_mode = choose_input_mode()

        if input_mode == 1:
            directory_name = os.path.basename(os.path.normpath(sys.argv[1]))
            guessed_artist = guess_artist_from_directory(directory_name)
            if guessed_artist:
                artist_name = guessed_artist["name"]
                artist_id = guessed_artist["id"]
            else:
                print("❌ No artist guessed. Switching to manual input.")
                input_mode = 2

        if input_mode == 2:
            artist_name = input("Enter artist name: ")
            artists = search_artist(artist_name)
            if not artists:
                print("❌ No artist found. Try again.")
                continue
            artist_id = artists[0]["id"]

        albums = get_albums_by_artist(artist_id)
        selected_album = select_album(albums)
        if selected_album == "back":
            print("🔙 Going back to artist selection.")
            continue
        elif not selected_album:
            print("❌ No album selected. Exiting.")
            sys.exit(1)

        print(f"✔ Selected album: {selected_album['title']}")
        for path in sys.argv[1:]:
            scan_path(path, selected_album, artist_name)
            time.sleep(1)
        sys.exit(0)

