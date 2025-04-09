# YouTube Transcript Viewer

A web application that allows you to view transcripts from YouTube videos with timestamps.

## Features

- Extract transcripts from YouTube videos
- Display timestamps alongside transcript text
- Modern, responsive UI
- Error handling for invalid URLs or unavailable transcripts

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Paste a YouTube video URL into the input field (e.g., https://www.youtube.com/watch?v=NRVEkc9lxH0)
2. Click "Get Transcript"
3. The transcript will be displayed with timestamps on the left side

## Requirements

- Python 3.7+
- Flask
- youtube-transcript-api 