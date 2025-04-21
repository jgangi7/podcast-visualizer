#!/usr/bin/env python3
"""
Grok Conversation Analyzer

This script uses the xAI Grok API to analyze conversations and extract main points
and related topics. It uses the OpenAI Python SDK for compatibility with xAI's API.

Requirements:
- Python 3.6+
- openai package (pip install openai)
- python-dotenv package (pip install python-dotenv)
- .env file with XAI_API_KEY

Usage:
1. Set your XAI_API_KEY in the .env file
2. Run the script: python grok_analyzer.py
3. View the analysis in the console and analysis.txt

For web integration, see the Flask example in the comments below.
"""

import os
import time
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
XAI_API_BASE = "https://api.x.ai/v1"
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds

# Sample chapters for testing
SAMPLE_CHAPTERS = [
    {
        "title": "Chapter 1: Early Life",
        "content": """
        Growing up, did you ever think you'd be a politician?
        - Nope. Not in a million years.
        - Yeah, I know that you hate talking about yourself, which is rare for a politician. What's your philosophy behind that?
        - I focus on the issues facing the people, not myself. Politics should be about addressing real problems.
        """
    },
    {
        "title": "Chapter 2: Civil Rights Movement",
        "content": """
        You were active in the civil rights movement in 1963 and attended the March on Washington. What was that like?
        - It was extraordinary. A huge crowd, focused on jobs and justice. MLK's speech was inspiring.
        - How did that experience shape your political views?
        - It showed me the power of peaceful protest and the importance of standing up for what's right.
        """
    }
]

def get_api_key() -> str:
    """
    Get the API key from .env file or prompt the user.
    Returns the API key as a string.
    """
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Warning: XAI_API_KEY not found in .env file.")
        print("Please create a .env file with your API key:")
        print("XAI_API_KEY=your_api_key_here")
        api_key = input("Please enter your xAI API key: ").strip()
        
        # Save the API key to .env file
        try:
            with open(".env", "a") as f:
                f.write(f"\nXAI_API_KEY={api_key}")
            print("API key has been saved to .env file for future use.")
        except Exception as e:
            print(f"Warning: Could not save API key to .env file: {str(e)}")
            
    return api_key

def create_analysis_prompt(chapter_content: str) -> List[Dict[str, str]]:
    """
    Create the messages for the API call with the conversation analysis prompt.
    """
    system_message = """You are an analytical summarizer. Your task is to:
1. Extract and summarize the main points from the conversation
2. Identify related topics and themes
3. Present the information in a clear, structured format"""

    user_message = f"""Please analyze this conversation and provide:
1. A summary of the main points
2. A list of related topics or themes

Conversation:
{chapter_content}"""

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

def extract_insights_from_chunk(text_chunk: str) -> dict:
    """
    Analyzes a chunk of podcast transcription and extracts main points and related topics
    using the Grok-beta API.
    
    Args:
        text_chunk: String containing the transcription text to analyze
        
    Returns:
        Dictionary with two keys:
        - 'main_points': List of strings representing main talking points
        - 'related_topics': List of strings representing related topics
    """
    # Initialize the OpenAI client with xAI's API endpoint
    api_key = get_api_key()
    client = OpenAI(
        api_key=api_key,
        base_url=XAI_API_BASE
    )
    
    # Create the analysis prompt
    messages = [
        {"role": "system", "content": """You are an analytical summarizer focused on extracting key insights from podcast transcripts.
Your task is to:
1. Identify the main talking points - core arguments, key statements, and central ideas
2. Extract related topics - connected subjects, references, or tangential ideas mentioned
Keep the output concise and focused on the most important elements."""},
        {"role": "user", "content": f"""Please analyze this podcast transcript chunk and provide:
1. Main talking points (core arguments, key statements, central ideas)
2. Related topics (connected subjects, references, tangential ideas)

Transcript chunk:
{text_chunk}"""}
    ]
    
    # Make the API call with retry logic
    retry_count = 0
    delay = INITIAL_RETRY_DELAY
    
    while retry_count < MAX_RETRIES:
        try:
            response: ChatCompletion = client.chat.completions.create(
                model="grok-beta",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                stream=False
            )
            
            # Parse the response to extract main points and related topics
            content = response.choices[0].message.content
            
            # Initialize the result dictionary
            result = {
                'main_points': [],
                'related_topics': []
            }
            
            # Split the response into sections and parse
            sections = content.split('\n\n')
            current_section = None
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                if 'main' in section.lower() or 'talking points' in section.lower():
                    current_section = 'main_points'
                    continue
                elif 'related' in section.lower() or 'topics' in section.lower():
                    current_section = 'related_topics'
                    continue
                
                if current_section:
                    # Split by bullet points or numbers
                    points = [p.strip('- 1234567890.') for p in section.split('\n')]
                    points = [p.strip() for p in points if p.strip()]
                    result[current_section].extend(points)
            
            return result
            
        except Exception as e:
            if "429" in str(e) and retry_count < MAX_RETRIES - 1:
                print(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                retry_count += 1
                continue
            print(f"Error analyzing chunk: {str(e)}")
            return {'main_points': [], 'related_topics': []}

def analyze_chapter(
    client: OpenAI,
    chapter: Dict[str, str],
    max_retries: int = MAX_RETRIES
) -> Optional[Dict[str, str]]:
    """
    Analyze a single chapter using the Grok API.
    Returns a dictionary with the chapter title and analysis.
    """
    print(f"\nAnalyzing {chapter['title']}...")
    messages = create_analysis_prompt(chapter['content'])
    retry_count = 0
    delay = INITIAL_RETRY_DELAY

    while retry_count < max_retries:
        try:
            response: ChatCompletion = client.chat.completions.create(
                model="grok-beta",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                stream=False
            )
            return {
                "title": chapter['title'],
                "analysis": response.choices[0].message.content
            }

        except Exception as e:
            if "429" in str(e) and retry_count < max_retries - 1:
                print(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                retry_count += 1
                continue
            print(f"Error analyzing chapter: {str(e)}")
            return None

def save_analysis(analyses: List[Dict[str, str]], filename: str = "analysis.txt") -> None:
    """Save the analyses to a file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for analysis in analyses:
                f.write(f"\n{'='*50}\n")
                f.write(f"{analysis['title']}\n")
                f.write(f"{'='*50}\n\n")
                f.write(analysis['analysis'])
                f.write("\n\n")
        print(f"Analysis saved to {filename}")
    except Exception as e:
        print(f"Error saving analysis to file: {str(e)}")

def main():
    """Main function to run the conversation analysis."""
    # Initialize the OpenAI client with xAI's API endpoint
    api_key = get_api_key()
    client = OpenAI(
        api_key=api_key,
        base_url=XAI_API_BASE
    )

    # Analyze each chapter
    analyses = []
    for chapter in SAMPLE_CHAPTERS:
        analysis = analyze_chapter(client, chapter)
        if analysis:
            analyses.append(analysis)
            print(f"\nAnalysis for {chapter['title']}:")
            print("-" * 50)
            print(analysis['analysis'])
            print("-" * 50)
        else:
            print(f"Failed to analyze {chapter['title']}. Please check your API key and try again.")
    
    # Save all analyses to a file
    if analyses:
        save_analysis(analyses)

if __name__ == "__main__":
    main()

"""
Flask Integration Example:

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    chapters = request.json.get('chapters', [])
    if not chapters:
        return jsonify({'error': 'No chapters provided'}), 400
    
    analyses = []
    for chapter in chapters:
        analysis = analyze_chapter(client, chapter)
        if analysis:
            analyses.append(analysis)
    
    if not analyses:
        return jsonify({'error': 'Analysis failed'}), 500
    
    return jsonify({'analyses': analyses})

if __name__ == '__main__':
    app.run(debug=True)
""" 