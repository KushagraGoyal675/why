# llm/groq_api.py

from typing import Dict, Any
from groq import Groq
from api_keys import GROQ_API_KEY

class GroqAPI:
    def __init__(self):
        if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
            raise ValueError("Please set your GROQ_API_KEY in api_keys.py")
        
        self.client = Groq(api_key=GROQ_API_KEY)
    
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
            print(f"Error in Groq API call: {str(e)}")
            return {
                "error": str(e),
                "response": None
            }

# Global instance
groq_api = GroqAPI()

if __name__ == "__main__":
    # Test the API
    test_prompt = "What is the role of a judge in an Indian court?"
    result = groq_api.generate_response(test_prompt)
    print(f"Test response: {result}")
