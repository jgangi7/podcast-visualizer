from typing import List, Dict, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans
# import numpy as np
# from transformers import pipeline
# import torch
from datetime import datetime
import hashlib
from functools import lru_cache

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
            
        # Comment out LLM initialization
        # self.classifier = pipeline("zero-shot-classification",
        #                          model="facebook/bart-large-mnli",
        #                          device=0 if torch.cuda.is_available() else -1)
            
        # Comment out topic categories
        # self.topic_categories = [
        #     "combat sports",
        #     "personal life",
        #     "mental preparation",
        #     "competition preparation",
        #     "software development",
        #     "artificial intelligence",
        #     "tech trends",
        #     "nutrition",
        #     "fitness",
        #     "mental health",
        #     "self-care",
        #     "entrepreneurship",
        #     "marketing",
        #     "finance",
        #     "investing",
        #     "startups",
        #     "astronomy",
        #     "physics",
        #     "biology",
        #     "chemistry",
        #     "environmental science",
        #     "scientific discoveries",
        #     "green technology",
        #     "online learning",
        #     "study techniques",
        #     "language learning",
        #     "teaching",
        #     "educational technology",
        #     "academic research",
        #     "skill development",
        #     "world travel",
        #     "video games",
        #     "social justice",
        #     "human rights",
        #     "cooking",
        #     "outdoor activities",
        #     "ancient civilizations",
        #     "world history",
        #     "baking",
        #     "cars",
        #     "hiking",
        #     "camping",
        #     "rock climbing",
        #     "kayaking",
        #     "survival skills",
        #     "wilderness exploration",
        #     "extreme sports",
        #     "parenting tips",
        #     "child development",
        #     "real estate"
        # ]
        
        # Initialize cache for classification results
        # self._classification_cache = {}
        
    def parse_timestamp(self, timestamp: str) -> int:
        """Convert timestamp to seconds"""
        try:
            # Handle HH:MM:SS format
            if len(timestamp.split(':')) == 3:
                h, m, s = map(int, timestamp.split(':'))
                return h * 3600 + m * 60 + s
            # Handle MM:SS format
            elif len(timestamp.split(':')) == 2:
                m, s = map(int, timestamp.split(':'))
                return m * 60 + s
            return 0
        except:
            return 0

    def format_timestamp(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def analyze_transcript(self, transcript: List[Dict]) -> Dict:
        """
        Return basic transcript information without LLM analysis
        """
        return {
            "segments": transcript,
            "topics": [],
            "entities": []
        }
    
    def parse_timestamp_line(self, line: str) -> Tuple[int, str]:
        """Parse a timestamp line in the format 'HH:MM:SS - Topic'"""
        try:
            # Split timestamp and topic
            parts = line.split(' - ', 1)
            if len(parts) != 2:
                return None, None
            
            timestamp, topic = parts
            
            # Parse timestamp
            seconds = this.parse_timestamp(timestamp.strip())
            
            return seconds, topic.strip()
        except:
            return None, None
    
    def extract_segments_from_text(self, text: str) -> List[Dict]:
        """Extract segments from text with timestamps"""
        segments = []
        lines = text.strip().split('\n')
        
        for i, line in enumerate(lines):
            seconds, topic = this.parse_timestamp_line(line)
            if seconds is not None:
                # Calculate duration (use next timestamp or default to 300 seconds)
                duration = 300
                if i < len(lines) - 1:
                    next_seconds, _ = this.parse_timestamp_line(lines[i + 1])
                    if next_seconds is not None:
                        duration = next_seconds - seconds
                
                segments.append({
                    "start": seconds,
                    "duration": duration,
                    "text": topic,
                    "original_line": line
                })
        
        return segments
    
    def analyze_segments_from_text(self, text: str) -> Dict:
        """Analyze segments from text with timestamps"""
        segments = this.extract_segments_from_text(text)
        return {
            "segments": segments,
            "topics": [],
            "entities": []
        } 