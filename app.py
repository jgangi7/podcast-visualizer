from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

app = Flask(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def extract_video_id(url):
    # Regular expression to match YouTube video IDs
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def preprocess_text(text):
    """Clean and preprocess text for topic extraction"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_keywords(text, top_n=5):
    """Extract the most important keywords from text"""
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_freq = Counter(words)
    
    # Return the top N most frequent words
    return [word for word, _ in word_freq.most_common(top_n)]

def generate_topics_from_transcript(transcript, num_topics=5):
    """Generate topics from the transcript using TF-IDF and clustering"""
    # Combine all transcript segments into a single text
    full_text = ' '.join([segment['text'] for segment in transcript])
    
    # Preprocess the text
    processed_text = preprocess_text(full_text)
    
    # Split the text into chunks (sentences or segments)
    chunks = []
    current_chunk = ""
    
    for segment in transcript:
        current_chunk += " " + segment['text']
        if len(current_chunk) > 100 or segment == transcript[-1]:  # Process in chunks of ~100 characters
            chunks.append(current_chunk)
            current_chunk = ""
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # If we have too few chunks, just use the full text
    if len(chunks) < num_topics:
        chunks = [processed_text]
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(chunks)
    
    # If we have enough chunks, use clustering to find topics
    if len(chunks) >= num_topics:
        # Use K-means clustering to group similar chunks
        kmeans = KMeans(n_clusters=num_topics, random_state=42)
        kmeans.fit(tfidf_matrix)
        
        # Extract the most common words in each cluster
        topics = []
        for i in range(num_topics):
            # Get the centroid of the cluster
            centroid = kmeans.cluster_centers_[i]
            
            # Get the indices of the top terms in the centroid
            top_indices = centroid.argsort()[-5:][::-1]
            
            # Get the feature names (words) for these indices
            feature_names = vectorizer.get_feature_names_out()
            topic_words = [feature_names[idx] for idx in top_indices]
            
            # Join the words to form a topic
            topic = ' '.join(topic_words)
            topics.append(topic)
    else:
        # If we don't have enough chunks, just extract keywords from the full text
        topics = extract_keywords(processed_text, top_n=num_topics)
    
    return topics

def assign_topic_to_sentence(sentence, topics):
    """Assign the most relevant topic to a sentence based on keyword matching"""
    sentence_text = preprocess_text(sentence['text'])
    sentence_words = set(word_tokenize(sentence_text))
    
    # Calculate similarity scores for each topic
    topic_scores = {}
    for topic in topics:
        topic_words = set(word_tokenize(topic))
        # Calculate Jaccard similarity
        intersection = len(sentence_words.intersection(topic_words))
        union = len(sentence_words.union(topic_words))
        if union > 0:
            similarity = intersection / union
            topic_scores[topic] = similarity
    
    # If no topic has a significant similarity, return 'general'
    if not topic_scores or max(topic_scores.values()) < 0.1:
        return 'general'
    
    # Return the topic with the highest similarity
    return max(topic_scores.items(), key=lambda x: x[1])[0]

def group_into_sentences(transcript, video_id=None):
    sentences = []
    current_sentence = {
        'text': '',
        'start': None,
        'end': None,
        'segments': [],
        'topic': None
    }
    
    # Define a pause threshold (in seconds)
    # Segments with gaps longer than this will be considered separate sentences
    PAUSE_THRESHOLD = 1.5
    # Maximum duration for a topic (20 minutes in seconds)
    MAX_TOPIC_DURATION = 20 * 60
    
    for i, segment in enumerate(transcript):
        # If this is the first segment, initialize the sentence
        if current_sentence['start'] is None:
            current_sentence['start'] = segment['start']
            current_sentence['end'] = segment['start'] + segment['duration']
            current_sentence['text'] = segment['text']
            current_sentence['segments'].append(segment)
            continue
        
        # Check for time gap between segments
        time_gap = segment['start'] - (current_sentence['end'])
        
        # Check if the current segment is part of the same sentence
        # This is a simple heuristic - we assume a sentence ends with a period, question mark, or exclamation mark
        # followed by a space or end of text, OR if there's a significant pause
        if not re.search(r'[.!?]\s*$', current_sentence['text']) and time_gap < PAUSE_THRESHOLD:
            # Append to current sentence
            current_sentence['text'] += ' ' + segment['text']
            current_sentence['end'] = segment['start'] + segment['duration']
            current_sentence['segments'].append(segment)
        else:
            # End of sentence detected (either by punctuation or pause), save it and start a new one
            sentences.append(current_sentence)
            current_sentence = {
                'text': segment['text'],
                'start': segment['start'],
                'end': segment['start'] + segment['duration'],
                'segments': [segment],
                'topic': None
            }
    
    # Add the last sentence if it exists
    if current_sentence['text']:
        sentences.append(current_sentence)
    
    # Generate topics from the transcript
    topics = generate_topics_from_transcript(transcript)
    
    # First pass: assign initial topics to all sentences
    for sentence in sentences:
        sentence['topic'] = assign_topic_to_sentence(sentence, topics)
    
    # Second pass: enforce time limit by splitting long topics
    topic_groups = []
    current_group = []
    current_topic = None
    current_start_time = None
    
    for sentence in sentences:
        # If this is a new topic or we don't have a current topic
        if current_topic != sentence['topic'] or current_topic is None:
            # Save the previous group if it exists
            if current_group:
                topic_groups.append(current_group)
            
            # Start a new group
            current_group = [sentence]
            current_topic = sentence['topic']
            current_start_time = sentence['start']
        else:
            # Check if adding this sentence would exceed the time limit
            if sentence['start'] - current_start_time > MAX_TOPIC_DURATION:
                # Time limit exceeded, save current group and start a new one
                topic_groups.append(current_group)
                current_group = [sentence]
                current_start_time = sentence['start']
            else:
                # Add to current group
                current_group.append(sentence)
    
    # Add the last group if it exists
    if current_group:
        topic_groups.append(current_group)
    
    # Third pass: reassign topics to ensure each group has a unique topic
    for i, group in enumerate(topic_groups):
        # Generate a unique topic name for this group
        group_topic = f"{group[0]['topic']}-{i+1}"
        
        # Assign the new topic to all sentences in the group
        for sentence in group:
            sentence['topic'] = group_topic
    
    # Flatten the groups back into a single list of sentences
    sentences = [sentence for group in topic_groups for sentence in group]
    
    # Update the topics list to include the new split topics
    topics = list(set(sentence['topic'] for sentence in sentences))
    
    return sentences, topics

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        sentences = [
            {
                'text': segment['text'],
                'start': segment['start'],
                'end': segment['start'] + segment['duration'],
                'segments': [segment],
                'topic': None
            }
            for segment in transcript
        ]
        return jsonify({'sentences': sentences})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 