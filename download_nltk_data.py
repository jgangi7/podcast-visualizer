import nltk

def download_nltk_data():
    print("Downloading required NLTK data...")
    
    # Download required NLTK data
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    
    print("NLTK data download complete!")

if __name__ == "__main__":
    download_nltk_data() 