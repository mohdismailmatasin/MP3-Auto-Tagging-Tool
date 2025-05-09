# MP3 Auto-Tagging Tool

This Python script automates the process of tagging MP3 files with metadata (title, artist, album) and embedding album artwork using the MusicBrainz API.

## Features

- Automatically detects and tags MP3 files in a directory.
- Fetches artist and album information from the MusicBrainz API.
- Embeds album artwork into MP3 files using the Cover Art Archive.
- Supports both auto-guessing artist names from directory names and manual input.
- Automatically installs missing dependencies (`requests` and `eyed3`).

## Requirements

- Python 3.6 or higher
- Internet connection (for API requests and downloading album artwork)

## Installation

1. Clone the repository or download the script:
   ```bash
   git clone https://github.com/your-repo/mp3-auto-tagger.git
   cd mp3-auto-tagger
   ```

2. Install Python dependencies:
   The script automatically installs missing dependencies (`requests` and `eyed3`) when you run it.

## Usage

1. Run the script with the path to your MP3 files:
   ```bash
   python3 mp3autotag.py '/path/to/mp3/files'
   ```

2. Follow the interactive prompts:
   - Choose input mode:
     - Auto-guess artist name from the directory name.
     - Manually input the artist name.
   - Select an album from the list of fetched albums.

3. The script will process each MP3 file in the directory, tag it with metadata, and embed album artwork.

## Example

```bash
python3 mp3autotag.py '/home/user/Music/ArtistName'
```

### Output Example:
```
Choose input mode:
1. Auto-guess artist from directory name
2. Manually input artist name
Enter your choice (1 or 2): 1

🤔 Guessing artist based on directory name: ArtistName
✔ Found potential matches for 'ArtistName':
1. Artist Name (ID: abc123)
2. Another Artist (ID: def456)
Enter the number of the correct artist (or press Enter to skip): 1

✔ Selected album: Album Title
Processing: /home/user/Music/ArtistName/song1.mp3
✔ Tagged: Song Title - Artist Name | Album: Album Title
🎨 Artwork embedded.
```

## Dependencies

The script uses the following Python libraries:
- `requests`: For making HTTP requests to the MusicBrainz API.
- `eyed3`: For reading and writing MP3 metadata.

These dependencies are automatically installed when you run the script.

## Known Issues

- The script assumes that the directory name matches the artist name. If the directory name is incorrect, you may need to manually input the artist name.
- Album artwork may not be available for all albums.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Contact

For questions or feedback, please contact [mohdismailmatasin@gmail.com].
