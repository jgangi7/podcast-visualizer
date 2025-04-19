from llm_analyzer import TranscriptAnalyzer

# Sample transcript with exact format
sample_text = """0:48 - Road to ADCC
19:20 - Danaher Death Squad
28:04 - Mental preparation
52:49 - Gordon Ryan
1:49:47 - Giancarlo Bodoni
2:14:54 - Garry Tonon
2:28:51 - Nicholas Meregali
2:44:17 - Ruotolo brothers
2:53:56 - Takedowns
2:58:16 - GSP
3:06:44 - Renzo Gracie
3:11:21 - Boris
3:15:12 - Ali Abdelaziz
3:17:38 - Khabib Nurmagomedov
3:21:30 - Joe Rogan playing pool
3:24:43 - Advice for grapplers
3:34:40 - Day in the life
3:41:21 - Bear vs Gorilla vs Lion vs Anaconda
4:19:08 - Tom Hardy
4:30:42 - Emojis
4:33:11 - Love
4:38:35 - Fighting to the death
4:42:22 - Knives"""

def test_format():
    print("Initializing TranscriptAnalyzer...")
    analyzer = TranscriptAnalyzer()
    
    print("\nExtracting segments from text...")
    segments = analyzer.extract_segments_from_text(sample_text)
    
    print("\nSegments found:")
    for i, segment in enumerate(segments, 1):
        print(f"\nSegment {i}:")
        print(f"Time: {analyzer.format_timestamp(segment['start'])} - Duration: {segment['duration']}s")
        print(f"Topic: {segment['text']}")
    
    print("\nAnalyzing segments...")
    results = analyzer.analyze_segments_from_text(sample_text)
    
    print("\nTopics identified:")
    for topic in results["topics"]:
        print(f"  - {topic['topic']} (confidence: {topic['confidence']:.2f})")
    
    print("\nEntities found:")
    for entity in results["entities"]:
        print(f"  - {entity['text']} ({entity['label']})")

if __name__ == "__main__":
    test_format() 