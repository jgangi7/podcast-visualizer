# YouTube Podcast Visualizer

This is a web application that analyzes YouTube podcast transcripts using the Grok-beta API to extract main talking points and related topics. The app visualizes the analysis results in an organized, chapter-by-chapter format. I built this with the intention that if you would like to get the "spark-notes" from a long form complex conversation posted to Youtube (thank you to all creators who do post thier pods) you could simply paste a link and get as much or as little insight as you would like.

## Features

- **Automatic Transcript Generation**: Fetches and processes YouTube video transcripts
- **Chapter Detection**: Automatically identifies and extracts chapters from video descriptions
- **Chapter Navigation**: Click on chapters to jump to specific timestamps in the transcript
- **Interactive Flow Chart**: Visualizes the podcast structure with:
  - Color-coded chapter sections
  - Key points from each chapter
  - Related topics and connections
  - Pan and zoom functionality for easy navigation
  - Export available
- **Dark/Light Mode**: Toggle between themes for comfortable viewing

## Technologies Used

### Backend
- **Flask**: Python web framework for the backend server
- **youtube-transcript-api**: For fetching YouTube video transcripts
- **Google API Client**: For accessing YouTube Data API (chapter information)
- **Graphviz**: For generating the flow chart visualizations
- **Grok-Beta API**: For analyzing transcript content and extracting insights (requires xAI API key)

### Frontend
- **HTML/CSS/JavaScript**: Core web technologies
- **Bootstrap**: For responsive design and UI components
- **SVG Pan-Zoom**: For interactive flow chart navigation
- **save-svg-as-png**: For exporting flow charts as PNG files
- **svg2pdf.js**: For exporting flow charts as PDF files

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd podcast-visualizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Graphviz:
- **Windows**: Download and install from [Graphviz website](https://graphviz.org/download/)
- **Mac**: `brew install graphviz`
- **Linux**: `sudo apt-get install graphviz`

5. Set up environment variables:
Create a `.env` file in the project root with:
```
YOUTUBE_API_KEY=your_youtube_api_key
XAI_API_KEY=your_xai_api_key
```

6. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Input**: Paste a YouTube URL of a podcast or long-form video
2. **Processing**: The application will:
   - Fetch the video transcript
   - Extract chapters
   - Analyze the content
   - Generate visualizations

3. **Navigation**:
   - Use the chapter list to jump to specific sections
   - Pan and zoom the flow chart using mouse controls
   - Click the theme toggle for dark/light mode
   - Export the flow chart using the export button

4. **Flow Chart Controls**:
   - Click and drag to pan
   - Use mouse wheel or buttons to zoom
   - Use reset button to return to original view
   - Export as PNG or PDF for sharing

## API Keys

- **YouTube API Key**: Required for fetching chapter information. Get it from [Google Cloud Console](https://console.cloud.google.com/)
- **OpenAI API Key**: Required for content analysis. Get it from [OpenAI Platform](https://platform.openai.com/)

## Limitations

- Works best with videos that have:
  - Available transcripts (auto-generated or manual)
  - Chapter markers in the description (currently working to make it work for pods with no chapters too)
- Processing time varies based on video length
- Requires active internet connection
- API rate limits apply

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 