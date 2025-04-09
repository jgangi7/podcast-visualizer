# YouTube Transcript Viewer

A web application that allows you to view transcripts from YouTube videos with timestamps, grouped by sentences, conversation pauses, and topics.

## Features

- Extract transcripts from YouTube videos
- Group transcript segments into complete sentences
- Detect and group sentences by conversation pauses
- Automatically detect topics for each part of the conversation
- Display time ranges for each sentence
- Show pause durations between sentences
- Expandable view to see individual transcript segments
- Modern, responsive UI
- Error handling for invalid URLs or unavailable transcripts

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Download the required NLTK data:
```bash
python download_nltk_data.py
```

3. Run the application:
```bash
python app.py
```

4. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Paste a YouTube video URL into the input field (e.g., https://www.youtube.com/watch?v=NRVEkc9lxH0)
2. Click "Get Transcript"
3. The transcript will be displayed with sentences grouped by conversation pauses and topics
4. Each group is labeled with its detected topic (e.g., "intro", "species", "direwolves", "game of thrones")
5. Each sentence shows its time range and any pause duration before the next sentence
6. Click on a sentence to expand and see the individual transcript segments

## Topic Detection

The application automatically detects topics for different parts of the conversation based on keyword matching. Supported topics include:

- intro
- goodbye
- species
- direwolves
- game of thrones
- biology
- history
- science
- education
- technology
- general (default when no specific topic is detected)

## Requirements

- Python 3.7+
- Flask
- youtube-transcript-api
- NLTK 