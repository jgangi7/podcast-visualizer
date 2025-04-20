import graphviz
import os
from datetime import datetime
from llm_processor import TranscriptProcessor
import re

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    return str(datetime.utcfromtimestamp(seconds).strftime('%H:%M:%S'))

def generate_youtube_chapters_flow(chapters, transcript_text=None):
    """
    Generate a flowchart from YouTube chapters data with LLM-processed information
    
    Args:
        chapters: List of dictionaries containing chapter data
                 Each dict should have 'title' and 'start_time' keys
        transcript_text: Optional full transcript text to process for each chapter
    Returns:
        str: SVG content of the generated graph
    """
    # Initialize LLM processor if transcript is provided
    processor = None
    if transcript_text:
        try:
            processor = TranscriptProcessor()
        except Exception as e:
            print(f"Failed to initialize LLM processor: {str(e)}")
    
    # Create a new directed graph
    dot = graphviz.Digraph('YoutubeChaptersFlow')
    
    # Graph settings
    dot.attr(rankdir='LR', splines='curved')
    dot.attr('node', fontname='Arial')
    dot.attr('edge', color='#666666')
    
    # Set main chapter node style
    dot.attr('node',
        shape='box',
        style='rounded,filled',
        fillcolor='#90EE90',
        fontsize='14',
        width='2')
    
    # Create chapter nodes
    for i, chapter in enumerate(chapters):
        current_time = format_timestamp(chapter['start_time'])
        next_time = format_timestamp(chapters[i+1]['start_time']) if i < len(chapters)-1 else "END"
        
        node_name = f"Chapter{i+1}"
        label = f"{chapter['title']}\n({current_time}-{next_time})"
        dot.node(node_name, label)
        
        # Add clock icon
        dot.node(f"Clock{i+1}", "⏱",
            shape='circle',
            style='filled',
            fillcolor='#FFD700',
            fontcolor='black',
            width='0.3',
            height='0.3',
            fontsize='10')
        
        # Add invisible edge from clock to chapter
        dot.edge(f"Clock{i+1}", node_name, style='invis')
        
        # Connect chapters in sequence
        if i > 0:
            dot.edge(f"Chapter{i}", node_name, color='#90EE90', penwidth='2')
        
        # Process chapter text with LLM if available
        if processor and transcript_text:
            try:
                # Extract chapter text from transcript
                start_time = chapter['start_time']
                end_time = chapters[i+1]['start_time'] if i < len(chapters)-1 else float('inf')
                
                # Extract text between timestamps
                chapter_lines = []
                for line in transcript_text.split('\n'):
                    if line.strip():
                        time_match = re.match(r'(\d{2}):(\d{2})\s*-\s*', line)
                        if time_match:
                            minutes, seconds = map(int, time_match.groups())
                            line_time = minutes * 60 + seconds
                            if start_time <= line_time < end_time:
                                chapter_lines.append(line)
                
                chapter_text = '\n'.join(chapter_lines)
                
                # Process chapter text
                if chapter_text:
                    results = processor.process_segment(chapter_text)
                    formatted_results = processor.format_for_visualization(results)
                    
                    # Add result nodes
                    dot.attr('node',
                        shape='box',
                        style='rounded,filled',
                        fillcolor='#f0f0f0',
                        fontsize='12',
                        width='2')
                    
                    for category, text in formatted_results.items():
                        node_id = f"{node_name}_{category}"
                        dot.node(node_id, text)
                        dot.edge(node_name, node_id, color='#666666', penwidth='1')
            
            except Exception as e:
                print(f"Error processing chapter {i+1}: {str(e)}")
                # Add error node
                dot.attr('node',
                    shape='box',
                    style='rounded,filled',
                    fillcolor='#ffcccc',
                    fontsize='12',
                    width='1.5')
                dot.node(f"{node_name}_error", "Failed to process chapter")
                dot.edge(node_name, f"{node_name}_error", color='#ff0000', penwidth='1')
        
        # Set rank for clock and chapter
        with dot.subgraph() as s:
            s.attr(rank='same')
            s.node(f"Clock{i+1}")
            s.node(node_name)
    
    # Return SVG content
    return dot.pipe(format='svg').decode('utf-8')

# Example usage:
if __name__ == '__main__':
    # Example chapters data
    sample_chapters = [
        {'title': 'Introduction', 'start_time': 0},
        {'title': 'Main Discussion', 'start_time': 930},  # 15:30
        {'title': 'Conclusion', 'start_time': 1965},      # 32:45
    ]
    
    generate_youtube_chapters_flow(sample_chapters) 