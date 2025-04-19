# YouTube Transcript Analyzer

A web application that analyzes YouTube video transcripts using open-source language models to extract topics, entities, and conversation structure.

## Features

- YouTube transcript extraction with timestamps
- Zero-shot topic classification using BART
- Named entity recognition using BERT and spaCy
- Conversation tree visualization
- Interactive timeline view
- No API keys required - everything runs locally

## Requirements

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-transcript-analyzer.git
cd youtube-transcript-analyzer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter a YouTube URL and click "Analyze Transcript"

4. View the analysis results:
   - Topics with confidence scores
   - Named entities grouped by type
   - Interactive conversation timeline
   - Full transcript with timestamps

## How It Works

1. **Transcript Extraction**: Uses the YouTube Transcript API to fetch video transcripts with timestamps.

2. **Topic Classification**: Uses BART-large-MNLI for zero-shot classification of transcript segments into predefined topics.

3. **Entity Recognition**: Combines BERT and spaCy for comprehensive named entity extraction.

4. **Conversation Tree**: Builds a hierarchical structure of the conversation using NetworkX.

5. **Visualization**: Creates both static (PNG) and interactive (HTML) visualizations using Plotly.

## Project Structure

```
youtube-transcript-analyzer/
├── app.py                 # Main Flask application
├── llm_analyzer.py        # LLM-based analysis module
├── requirements.txt       # Python dependencies
├── static/               # Static files (visualizations)
└── templates/            # HTML templates
    └── index.html        # Main web interface
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 