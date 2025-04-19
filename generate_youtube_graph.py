import graphviz
import os
from datetime import datetime

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    return str(datetime.utcfromtimestamp(seconds).strftime('%H:%M:%S'))

def generate_youtube_chapters_flow(chapters):
    """
    Generate a flowchart from YouTube chapters data
    
    Args:
        chapters: List of dictionaries containing chapter data
                 Each dict should have 'title' and 'start_time' keys
    Returns:
        str: SVG content of the generated graph
    """
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
        
        # Add some example subtopics for each chapter
        dot.attr('node',
            shape='box',
            style='rounded,filled',
            fillcolor='#f0f0f0',
            fontsize='12',
            width='1.5')
        
        # Add 2-3 subtopics per chapter
        subtopics = [
            "Main Points",
            "Key Discussion",
            "Related Topics"
        ]
        
        for j, subtopic in enumerate(subtopics):
            subtopic_name = f"Topic{i+1}_{j+1}"
            dot.node(subtopic_name, subtopic)
            dot.edge(node_name, subtopic_name, color='#666666', penwidth='1')
        
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