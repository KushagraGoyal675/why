# llm/groq_api.py

from typing import Dict, Any
from groq import Groq

class GroqAPI:
    def __init__(self):
        # Directly define the API key here
        self.api_key = "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"  # <-- Replace with your actual Groq API key

        if not self.api_key or self.api_key == "YOUR_GROQ_API_KEY_HERE":
            raise ValueError("Please set your GROQ_API_KEY in groq_api.py")
        
        self.client = Groq(api_key=self.api_key)
    
    def generate_response(self, prompt: str, model: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a legal expert assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            return {
                "response": completion.choices[0].message.content,
                "model": model,
                "usage": completion.usage
            }
        except Exception as e:
            return {
                "error": str(e),
                "response": None
            }

# Global instance
groq_api = GroqAPI()
