# Grok Conversation Analyzer

This Python script uses the xAI Grok API to analyze conversations and extract main points and related topics. It uses the OpenAI Python SDK for compatibility with xAI's API.

## Features

- Analyzes conversations using the Grok-beta model
- Extracts main points and related topics
- Handles API errors and rate limits with retry logic
- Saves analysis results to a file
- Includes a sample conversation for testing
- Optional Flask integration for web API usage
- Secure API key storage using .env file

## Requirements

- Python 3.6+
- xAI API key (get it from https://x.ai)
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository or download the files
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your API key:
   ```
   XAI_API_KEY=your_api_key_here
   ```

## Usage

1. Make sure your `.env` file contains your xAI API key:
   ```
   XAI_API_KEY=your_api_key_here
   ```

2. Run the script:
   ```bash
   python grok_analyzer.py
   ```

3. The script will:
   - Analyze the sample conversation
   - Display the results in the console
   - Save the analysis to `analysis.txt`

## Web API Integration

The script includes a Flask integration example in the comments. To use it:

1. Uncomment the Flask code at the bottom of the script
2. Run the Flask server:
   ```bash
   python grok_analyzer.py
   ```
3. Send POST requests to `/analyze` with a JSON body containing the conversation:
   ```json
   {
     "conversation": "Your conversation text here"
   }
   ```

## Customization

- Modify `SAMPLE_CONVERSATION` in the script to analyze different conversations
- Adjust `MAX_RETRIES` and `INITIAL_RETRY_DELAY` for different retry behavior
- Change the output file name in `save_analysis()` function

## Error Handling

The script includes comprehensive error handling for:
- Missing API key
- API authentication errors
- Rate limiting (with exponential backoff)
- File I/O errors

## Security Notes

- The API key is stored in the `.env` file, which should be added to `.gitignore`
- Never commit your `.env` file to version control
- The script will prompt for the API key if not found in the `.env` file
- When prompted, the script will attempt to save the API key to the `.env` file for future use

## License

MIT License 