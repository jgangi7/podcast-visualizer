import networkx as nx
import plotly.graph_objects as go
from typing import List, Dict, Tuple
import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from transformers import pipeline
import torch

class TranscriptAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        # Initialize transformers pipeline for zero-shot classification
        self.classifier = pipeline("zero-shot-classification",
                                 model="facebook/bart-large-mnli",
                                 device=0 if torch.cuda.is_available() else -1)
            
        # Define topic categories
        self.topic_categories = [
            "technology", "science", "politics", "business", "entertainment",
            "sports", "health", "education", "environment", "society"
        ]
        
    def analyze_transcript(self, transcript: List[Dict]) -> Dict:
        """
        Analyze the transcript and return structured insights
        """
        # Combine transcript segments into a single text
        full_text = " ".join([segment["text"] for segment in transcript])
        
        # Extract entities using NLTK
        entities = self._extract_entities(full_text)
        
        # Perform topic classification using zero-shot learning
        topics = self._classify_topics(full_text)
        
        # Build conversation tree
        tree = self._build_conversation_tree(transcript)
        
        return {
            "entities": entities,
            "topics": topics,
            "tree": tree
        }
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text using NLTK
        """
        entities = []
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            tokens = word_tokenize(sentence)
            pos_tags = nltk.pos_tag(tokens)
            chunks = nltk.ne_chunk(pos_tags)
            
            current_entity = []
            current_label = None
            
            for chunk in chunks:
                if isinstance(chunk, nltk.Tree):
                    # Named entity found
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    entity_label = chunk.label()
                    entities.append({
                        "text": entity_text,
                        "label": entity_label,
                        "start": text.find(entity_text),
                        "end": text.find(entity_text) + len(entity_text)
                    })
        
        return entities
    
    def _classify_topics(self, text: str) -> List[Dict]:
        """
        Classify topics using zero-shot classification
        """
        # Split text into smaller chunks if it's too long
        max_length = 512
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Classify each chunk
        all_results = []
        for chunk in chunks:
            result = self.classifier(
                chunk,
                candidate_labels=self.topic_categories,
                multi_label=True
            )
            all_results.append(result)
        
        # Aggregate results
        topic_scores = {topic: 0.0 for topic in self.topic_categories}
        for result in all_results:
            for label, score in zip(result['labels'], result['scores']):
                topic_scores[label] += score
        
        # Normalize scores
        num_chunks = len(all_results)
        topic_scores = {k: v/num_chunks for k, v in topic_scores.items()}
        
        # Convert to list of dictionaries and sort by confidence
        topics = [{"topic": k, "confidence": v} for k, v in topic_scores.items() if v > 0.1]
        topics.sort(key=lambda x: x["confidence"], reverse=True)
        
        return topics
    
    def _build_conversation_tree(self, transcript: List[Dict]) -> Dict:
        """
        Build a hierarchical tree structure of the conversation
        """
        G = nx.DiGraph()
        
        # Create nodes for each segment
        for i, segment in enumerate(transcript):
            node_id = f"segment_{i}"
            G.add_node(node_id, 
                      text=segment["text"],
                      start=segment["start"],
                      duration=segment["duration"])
            
            # Connect to previous segment
            if i > 0:
                G.add_edge(f"segment_{i-1}", node_id)
        
        # Convert to tree structure
        tree = {
            "nodes": [{"id": n, **G.nodes[n]} for n in G.nodes()],
            "edges": [{"source": u, "target": v} for u, v in G.edges()]
        }
        
        return tree
    
    def visualize_tree(self, tree: Dict, output_path: str = "conversation_tree.html"):
        """
        Create an interactive visualization of the conversation tree
        """
        # Create figure
        fig = go.Figure()
        
        # Add nodes
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in tree["nodes"]:
            node_x.append(node["start"])
            node_y.append(0)  # All nodes on same level for timeline view
            node_text.append(node["text"][:50] + "..." if len(node["text"]) > 50 else node["text"])
            node_size.append(node["duration"] * 5)  # Size proportional to duration
        
        # Add nodes trace
        fig.add_trace(go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            marker=dict(
                size=node_size,
                color="#1f77b4",
                line=dict(width=2, color="#ffffff")
            ),
            name="Segments"
        ))
        
        # Add edges
        for edge in tree["edges"]:
            source_idx = int(edge["source"].split("_")[1])
            target_idx = int(edge["target"].split("_")[1])
            
            fig.add_trace(go.Scatter(
                x=[node_x[source_idx], node_x[target_idx]],
                y=[node_y[source_idx], node_y[target_idx]],
                mode="lines",
                line=dict(width=1, color="#888"),
                showlegend=False
            ))
        
        # Update layout
        fig.update_layout(
            title="Conversation Timeline",
            xaxis_title="Time (seconds)",
            yaxis_title="",
            showlegend=True,
            height=600,
            template="plotly_white",
            hovermode="closest"
        )
        
        # Save as interactive HTML
        fig.write_html(output_path)
        
        # Also save as PNG for static view
        if output_path.endswith(".html"):
            png_path = output_path.replace(".html", ".png")
            fig.write_image(png_path)
        
        return fig 