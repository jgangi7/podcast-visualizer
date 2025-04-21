from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv

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
    # Regular expression to match YouTube video IDs
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

def get_video_chapters(video_id):
    """Fetch video chapters using YouTube Data API"""
    if not youtube:
        return []
        
    try:
        # Get video details with the correct parts
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        if not video_response.get('items'):
            return []

        # Get video description which may contain chapters
        description = video_response['items'][0]['snippet']['description']
        
        # Parse chapters from description
        # Format: 00:00 Chapter 1
        chapters = []
        for line in description.split('\n'):
            # Look for timestamp patterns (HH:MM:SS or MM:SS)
            timestamp_match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)$', line.strip())
            if timestamp_match:
                time_str, title = timestamp_match.groups()
                # Convert timestamp to seconds
                time_parts = time_str.split(':')
                if len(time_parts) == 3:
                    hours, minutes, seconds = map(int, time_parts)
                    seconds = hours * 3600 + minutes * 60 + seconds
                else:
                    minutes, seconds = map(int, time_parts)
                    seconds = minutes * 60 + seconds
                
                chapters.append({
                    'time': seconds,
                    'title': title.strip()
                })
        
        # Sort chapters by time
        chapters.sort(key=lambda x: x['time'])
        return chapters

    except Exception as e:
        print(f"Error fetching chapters: {str(e)}")
        return []

def parse_transcript_chunks(transcript_text: str, chapters: list) -> list:
    """Parse transcript into chunks based on chapter timestamps"""
    chunks = []
    lines = transcript_text.strip().split('\n')
    
    # Sort chapters by time
    sorted_chapters = sorted(chapters, key=lambda x: x['time'])
    
    # Add a final "chapter" at the end to capture the last section
    if sorted_chapters:
        last_chapter = sorted_chapters[-1]
        sorted_chapters.append({
            'time': float('inf'),
            'title': 'End'
        })
    
    current_chunk = []
    current_chapter_index = 0
    
    for line in lines:
        # Extract timestamp from line
        timestamp_match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*(.+)$', line)
        if not timestamp_match:
            continue
            
        timestamp_str, text = timestamp_match.groups()
        
        # Convert timestamp to seconds
        time_parts = timestamp_str.split(':')
        if len(time_parts) == 3:
            hours, minutes, seconds = map(int, time_parts)
            current_time = hours * 3600 + minutes * 60 + seconds
        else:
            minutes, seconds = map(int, time_parts)
            current_time = minutes * 60 + seconds
        
        # Check if we've moved to a new chapter
        while (current_chapter_index < len(sorted_chapters) and 
               current_time >= sorted_chapters[current_chapter_index]['time']):
            # Save the current chunk if it's not empty
            if current_chunk:
                chunks.append({
                    'chapter': sorted_chapters[current_chapter_index]['title'],
                    'text': '\n'.join(current_chunk)
                })
            current_chunk = []
            current_chapter_index += 1
        
        # Add the text without timestamp to the current chunk
        current_chunk.append(text)
    
    # Add the final chunk if there's anything left
    if current_chunk and current_chapter_index < len(sorted_chapters):
        chunks.append({
            'chapter': sorted_chapters[current_chapter_index]['title'],
            'text': '\n'.join(current_chunk)
        })
    
    return chunks

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    try:
        url = request.json['url']
        video_id = extract_video_id(url)
        
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Get the transcript
        try:
            youtube_transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as e:
            return jsonify({'error': f'Failed to get transcript: {str(e)}'}), 400
        
        # Get video chapters
        chapters = get_video_chapters(video_id)
        
        # Convert YouTube transcript format to our format
        transcript_text = ""
        for segment in youtube_transcript:
            # Convert seconds to MM:SS format
            minutes = int(segment['start'] // 60)
            seconds = int(segment['start'] % 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"
            transcript_text += f"{timestamp} - {segment['text']}\n"
        
        # Parse transcript into chunks based on chapters
        transcript_chunks = parse_transcript_chunks(transcript_text, chapters)
        
        # Return transcript, chapters, and chunks
        return jsonify({
            'success': True,
            'transcript': transcript_text,
            'chapters': chapters,
            'transcript_chunks': transcript_chunks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 