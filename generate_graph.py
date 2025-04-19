import graphviz
import os

def generate_conversation_flow():
    # Read the DOT file
    dot_file_path = 'static/graphviz/conversation_flow.dot'
    
    # Create static/images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    # Generate the graph
    graph = graphviz.Source.from_file(dot_file_path)
    
    # Render the graph to a PNG file
    graph.render('static/images/conversation_flow', format='png', cleanup=True)

if __name__ == '__main__':
    generate_conversation_flow() 