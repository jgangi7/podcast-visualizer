from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv
from grok_analyzer import extract_insights_from_chunk
import graphviz

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
    lines = transcript_text.split('\n')
    
    # Sort chapters by time
    sorted_chapters = sorted(chapters, key=lambda x: x['time'])
    
    # If no chapters, return empty list
    if not sorted_chapters:
        return []
    
    # Add a final "chapter" at the end to capture the last section
    sorted_chapters.append({
        'time': float('inf'),
        'title': 'End'
    })
    
    # Create a list of lines with their timestamps (if available)
    indexed_lines = []
    for i, line in enumerate(lines):
        # Extract timestamp from line if available
        timestamp_match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*(.+)$', line)
        if timestamp_match:
            timestamp_str, text = timestamp_match.groups()
            
            # Convert timestamp to seconds
            time_parts = timestamp_str.split(':')
            if len(time_parts) == 3:
                hours, minutes, seconds = map(int, time_parts)
                current_time = hours * 3600 + minutes * 60 + seconds
            else:
                minutes, seconds = map(int, time_parts)
                current_time = minutes * 60 + seconds
                
            indexed_lines.append({
                'index': i,
                'line': line,
                'text': text,
                'time': current_time,
                'has_timestamp': True
            })
        else:
            # Line without timestamp
            indexed_lines.append({
                'index': i,
                'line': line,
                'text': line,
                'time': None,
                'has_timestamp': False
            })
    
    # Process each chapter
    for i in range(len(sorted_chapters) - 1):
        current_chapter = sorted_chapters[i]
        next_chapter = sorted_chapters[i + 1]
        
        # Find the first line with a timestamp that's >= current chapter time
        start_index = None
        for line_info in indexed_lines:
            if line_info['has_timestamp'] and line_info['time'] >= current_chapter['time']:
                start_index = line_info['index']
                break
        
        # If no line found with timestamp >= current chapter time, use the first line
        if start_index is None:
            start_index = 0
        
        # Find the last line with a timestamp that's < next chapter time
        end_index = None
        for line_info in reversed(indexed_lines):
            if line_info['has_timestamp'] and line_info['time'] < next_chapter['time']:
                end_index = line_info['index']
                break
        
        # If no line found with timestamp < next chapter time, use the last line
        if end_index is None:
            end_index = len(lines) - 1
        
        # Extract all lines between start_index and end_index (inclusive)
        chunk_lines = []
        for j in range(start_index, end_index + 1):
            if j < len(indexed_lines):
                chunk_lines.append(indexed_lines[j]['text'])
        
        # Add the chunk if it's not empty
        if chunk_lines:
            chunks.append({
                'chapter': current_chapter['title'],
                'text': '\n'.join(chunk_lines)
            })
    
    return chunks

def generate_flow_chart(chunks):
    # Create a new directed graph
    dot = graphviz.Digraph(comment='Chapter Flow Visualization')
    
    # Set graph attributes for better visualization
    dot.attr(rankdir='LR', splines='ortho')
    dot.attr('node', fontname='Arial', style='filled', fontcolor='#333333')
    
    # Color palette for chapters (pastel colors that work well in both light/dark modes)
    colors = [
        '#FFB3BA',  # Light pink
        '#BAFFC9',  # Light green
        '#BAE1FF',  # Light blue
        '#FFFFBA',  # Light yellow
        '#E8BAFF',  # Light purple
        '#FFD9BA',  # Light orange
        '#B3FFE0',  # Light mint
        '#FFB3E6',  # Light magenta
    ]
    
    # For each chunk, create a subgraph for the chapter and its details
    for i, chunk in enumerate(chunks):
        chapter_color = colors[i % len(colors)]
        
        with dot.subgraph(name=f'cluster_{i}') as c:
            # Set subgraph attributes
            c.attr(
                label=chunk['chapter'],
                style='rounded,filled',
                color=chapter_color,
                fillcolor=f'{chapter_color}80',  # Add transparency
                fontcolor='#333333',
                penwidth='2'
            )
            
            # Create main points node
            if chunk['main_points']:
                main_points_node = f'main_points_{i}'
                c.node(
                    main_points_node,
                    'Key Points',
                    shape='box',
                    style='filled',
                    fillcolor='white',
                    margin='0.2'
                )
                
                # Group main points in a more compact way
                points_text = '• ' + '\n• '.join(chunk['main_points'])
                point_node = f'points_{i}'
                c.node(
                    point_node,
                    points_text,
                    shape='box',
                    style='filled,rounded',
                    fillcolor='white',
                    margin='0.2'
                )
                c.edge(main_points_node, point_node, style='dotted')
            
            # Create related topics node
            if chunk['related_topics']:
                topics_node = f'topics_{i}'
                c.node(
                    topics_node,
                    'Related Topics',
                    shape='box',
                    style='filled',
                    fillcolor='white',
                    margin='0.2'
                )
                
                # Group related topics in a more compact way
                topics_text = '• ' + '\n• '.join(chunk['related_topics'])
                topic_list_node = f'topic_list_{i}'
                c.node(
                    topic_list_node,
                    topics_text,
                    shape='box',
                    style='filled,rounded',
                    fillcolor='white',
                    margin='0.2'
                )
                c.edge(topics_node, topic_list_node, style='dotted')
            
            # Connect main points and topics if both exist
            if chunk['main_points'] and chunk['related_topics']:
                c.edge(main_points_node, topics_node, style='dashed')
        
        # Connect chapters in sequence with a thicker, colored edge
        if i > 0:
            dot.edge(
                f'main_points_{i-1}',
                f'main_points_{i}',
                color=chapter_color,
                penwidth='2',
                constraint='true'
            )
    
    return dot

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
        
        # Analyze each chunk using Grok
        for chunk in transcript_chunks:
            analysis = extract_insights_from_chunk(chunk['text'])
            chunk['main_points'] = analysis['main_points']
            chunk['related_topics'] = analysis['related_topics']
        
        # Return transcript, chapters, and analyzed chunks
        return jsonify({
            'success': True,
            'transcript': transcript_text,
            'chapters': chapters,
            'transcript_chunks': transcript_chunks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_flow_chart', methods=['POST'])
def create_flow_chart():
    try:
        data = request.get_json()
        chunks = data.get('chunks', [])
        
        if not chunks:
            return jsonify({'error': 'No chunks provided'}), 400
        
        # Generate the flow chart
        dot = generate_flow_chart(chunks)
        
        # Render the graph to a file
        output_path = 'static/flow_chart'
        dot.render(output_path, format='svg', cleanup=True)
        
        return jsonify({
            'success': True,
            'svg_path': output_path + '.svg'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 