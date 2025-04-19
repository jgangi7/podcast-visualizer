from llm_analyzer import TranscriptAnalyzer

# Sample transcript data
sample_transcript = [
    {
        "text": "Welcome to today's podcast about artificial intelligence and machine learning.",
        "start": 0,
        "duration": 5
    },
    {
        "text": "We'll be discussing the latest developments in deep learning and neural networks.",
        "start": 5,
        "duration": 6
    },
    {
        "text": "Our guest today is Dr. Smith, a leading expert in computer vision.",
        "start": 11,
        "duration": 4
    },
    {
        "text": "She has published numerous papers on convolutional neural networks.",
        "start": 15,
        "duration": 4
    }
]

def test_analyzer():
    print("Initializing TranscriptAnalyzer...")
    analyzer = TranscriptAnalyzer()
    
    print("\nAnalyzing sample transcript...")
    results = analyzer.analyze_transcript(sample_transcript)
    
    print("\nAnalysis Results:")
    print("\n1. Entities found:")
    for entity in results["entities"]:
        print(f"   - {entity['text']} ({entity['label']})")
    
    print("\n2. Topics identified:")
    for topic in results["topics"]:
        print(f"   - {topic['topic']} (confidence: {topic['confidence']:.2f})")
    
    print("\n3. Conversation Tree Structure:")
    print("   Nodes:", len(results["tree"]["nodes"]))
    print("   Edges:", len(results["tree"]["edges"]))
    
    print("\nGenerating visualization...")
    analyzer.visualize_tree(results["tree"], "test_conversation_tree.png")
    print("Visualization saved as 'test_conversation_tree.png'")

if __name__ == "__main__":
    test_analyzer() 