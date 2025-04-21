# YouTube Podcast Visualizer

This is a web application that analyzes YouTube podcast transcripts using the Grok-beta API to extract main talking points and related topics. The app visualizes the analysis results in an organized, chapter-by-chapter format. I built this with the intention that if you would like to get the "spark-notes" from a long form complex conversation posted to Youtube (thank you to all creators who do post thier pods) you could simply paste a link and get as much or as little insight as you would like.

## Features

- **YouTube Transcript Extraction**: Automatically fetches transcripts from YouTube videos
- **Chapter-Based Analysis**: Organizes content by video chapters for better context
- **Grok AI Analysis**: Uses the Grok-beta API to extract:
  - Main talking points (core arguments, key statements, central ideas)
  - Related topics (connected subjects, references, tangential ideas)
- **Interactive UI**: 
  - Dark/light theme support
  - Chapter navigation
  - Collapsible transcript sections
  - Responsive design for all devices

## Requirements

- Python 3.6+
- YouTube API key (for chapter extraction)
- xAI API key (for Grok-beta analysis)
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/podcast-visualizer.git
   cd podcast-visualizer
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   XAI_API_KEY=your_xai_api_key_here
   ```

4. Download required NLTK data:
   ```bash
   python download_nltk_data.py
   ```

## Usage

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Enter a YouTube URL in the input field and click "Visualize"

4. Wait for the analysis to complete (this may take a few minutes)

5. View the analysis results organized by chapters

## Compatible YouTube Videos

The application works best with YouTube videos that have:

1. **Available Transcripts**: The video must have captions/subtitles available
2. **Chapter Markers**: The video description should include chapter timestamps in the format:
   ```
   00:00 Introduction
   05:30 Main Topic
   15:45 Conclusion
   ```

### Finding Compatible Videos

- Most professional podcasts on YouTube include chapter markers
- Educational content often has well-structured chapters
- Look for videos with a table of contents in the description

### Limitations

- Videos without chapter markers will not be properly segmented
- Videos without transcripts cannot be analyzed
- Private or age-restricted videos may not be accessible

## How It Works

1. **Transcript Extraction**: The app uses the YouTube Transcript API to fetch the transcript
2. **Chapter Detection**: YouTube Data API extracts chapter information from the video description
3. **Text Segmentation**: The transcript is divided into chunks based on chapter timestamps
4. **AI Analysis**: Each chunk is analyzed by the Grok-beta API to extract main points and related topics
5. **Visualization**: Results are displayed in an organized, interactive interface

## Customization

- Modify `grok_analyzer.py` to adjust the analysis parameters
- Edit `static/css/styles.css` to customize the appearance
- Update `templates/index.html` to change the layout

## Troubleshooting

- **API Key Issues**: Ensure your API keys are correctly set in the `.env` file
- **Missing Transcripts**: Some videos may have disabled captions
- **No Chapters**: Videos without chapter markers will show all content in one section
- **Rate Limiting**: The Grok API has rate limits; the app includes retry logic

## License

MIT License 