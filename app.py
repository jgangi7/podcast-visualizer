from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv
from generate_youtube_graph import generate_youtube_chapters_flow

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize YouTube Data API client
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = None
if YOUTUBE_API_KEY:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
else:
    print("Warning: YOUTUBE_API_KEY not found in environment variables")

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS or MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def get_video_transcript(video_id):
    """Fetch and format video transcript"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatted_transcript = ""
        for entry in transcript:
            timestamp = format_timestamp(entry['start'])
            formatted_transcript += f"{timestamp} - {entry['text']}\n"
        return formatted_transcript
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return None

def get_video_chapters(video_id):
    """Fetch video chapters from video description"""
    if not youtube:
        return []
        
    try:
        # Get video details
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        if not video_response.get('items'):
            return []

        # Parse chapters from description
        description = video_response['items'][0]['snippet']['description']
        chapters = []
        
        for line in description.split('\n'):
            # Match timestamp patterns (HH:MM:SS or MM:SS)
            timestamp_match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)$', line.strip())
            if timestamp_match:
                time_str, title = timestamp_match.groups()
                
                # Convert timestamp to seconds
                time_parts = time_str.split(':')
                if len(time_parts) == 3:
                    hours, minutes, seconds = map(int, time_parts)
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                else:
                    minutes, seconds = map(int, time_parts)
                    total_seconds = minutes * 60 + seconds
                
                chapters.append({
                    'start_time': total_seconds,
                    'time': total_seconds,  # Add time field for backwards compatibility
                    'title': title.strip(),
                    'timestamp': format_timestamp(total_seconds)  # Add formatted timestamp
                })
        
        # Sort chapters by time
        chapters.sort(key=lambda x: x['start_time'])
        return chapters

    except Exception as e:
        print(f"Error fetching chapters: {str(e)}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    try:
        # Get video URL and clean it
        video_url = request.json.get('video_url', '')
        video_url = video_url.lstrip('@')
        
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
            
        # Get transcript and chapters
        transcript = get_video_transcript(video_id)
        if not transcript:
            return jsonify({'error': 'Failed to fetch transcript'}), 400
            
        chapters = get_video_chapters(video_id)
        
        # Generate visualization if chapters exist
        visualization_svg = None
        if chapters:
            visualization_svg = generate_youtube_chapters_flow(chapters, transcript)
        
        return jsonify({
            'transcript': transcript,
            'chapters': chapters,
            'visualization': visualization_svg
        })
        
    except Exception as e:
        print(f"Error in get_transcript: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 