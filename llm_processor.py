from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import Dict, List, Optional
import re

class TranscriptProcessor:
    def __init__(self, model_name: str = "facebook/opt-125m"):
        """Initialize the transcript processor with a lightweight OPT model."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Define prompt templates
        self.prompt_templates = {
            "main_points": (
                "Extract the main points from this podcast transcript segment as bullet points:\n"
                "{text}\n"
                "Main points:"
            ),
            "key_discussion": (
                "Identify the key discussion topics and important exchanges from this podcast segment. "
                "Format as bullet points:\n"
                "{text}\n"
                "Key discussion points:"
            ),
            "related_topics": (
                "List related topics, references, and connected ideas mentioned in this podcast segment. "
                "Format as bullet points:\n"
                "{text}\n"
                "Related topics:"
            )
        }
        
        # Maximum input length for the model
        self.max_input_length = 1024
        self.max_output_length = 150
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and prepare transcript text."""
        # Remove timestamps if present
        text = re.sub(r'\d{1,2}:\d{2}(:\d{2})?\s*-\s*', '', text)
        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove filler words and common transcription artifacts
        filler_words = r'\b(um|uh|like|you know|I mean|sort of|kind of)\b'
        text = re.sub(filler_words, '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit model's maximum input length."""
        tokens = self.tokenizer.encode(text, truncation=False)
        if len(tokens) > self.max_input_length:
            tokens = tokens[:self.max_input_length-2]  # Leave room for special tokens
            text = self.tokenizer.decode(tokens, skip_special_tokens=True)
        return text
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from generated text."""
        # Split on common bullet point markers
        points = re.split(r'•|-|\*|\d+\.|⁃', text)
        # Clean and filter points
        points = [p.strip() for p in points if p.strip()]
        return points
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response from the model."""
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=self.max_input_length)
            inputs = inputs.to(self.device)
            
            outputs = self.model.generate(
                **inputs,
                max_length=self.max_output_length,
                num_beams=4,
                length_penalty=2.0,
                early_stopping=True
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return ""
    
    def process_segment(self, text: str) -> Dict[str, List[str]]:
        """
        Process a transcript segment and extract structured information.
        
        Args:
            text: The transcript text to process
            
        Returns:
            Dictionary containing main_points, key_discussion, and related_topics
        """
        try:
            # Preprocess text
            cleaned_text = self._preprocess_text(text)
            truncated_text = self._truncate_text(cleaned_text)
            
            results = {}
            
            # Process each category
            for category, template in self.prompt_templates.items():
                prompt = template.format(text=truncated_text)
                response = self._generate_response(prompt)
                points = self._extract_bullet_points(response)
                
                # Ensure we have at least some results
                if not points:
                    points = ["No {category} identified"]
                
                results[category] = points[:3]  # Limit to top 3 points for visualization
            
            return results
            
        except Exception as e:
            print(f"Error processing segment: {str(e)}")
            return {
                "main_points": ["Error processing text"],
                "key_discussion": ["Error processing text"],
                "related_topics": ["Error processing text"]
            }
    
    @staticmethod
    def format_for_visualization(results: Dict[str, List[str]]) -> Dict[str, str]:
        """Format results for visualization nodes."""
        return {
            category: "\\n".join(points)  # Use \n for Graphviz line breaks
            for category, points in results.items()
        } 