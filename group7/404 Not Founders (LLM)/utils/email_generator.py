import requests
import json
import os
from typing import Literal, Optional

class EmailGenerator:
    """Email generator and improver using Mistral API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-small-latest"):
        """
        Initialize the email generator using Mistral API

        Args:
            api_key (str): Your Mistral API key
            model (str): Model name (e.g. mistral-small-latest, mistral-medium-latest)
        """
        self.api_key = api_key or os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError("API key required. Set MISTRAL_API_KEY environment variable or pass api_key")

        self.api_base = "https://api.mistral.ai/v1/chat/completions"
        self.model = model

    def _generate(self, prompt: str) -> str:
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_base, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                return f"❌ Error: API request failed with status {response.status_code}"
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            return f"❌ Error: {e}"

    def generate_email(
        self,
        description: str,
        tone: Literal['professional', 'friendly'] = 'professional',
        length: Literal['short', 'medium', 'long'] = 'medium'
    ) -> str:
        tone_style = {
            'professional': 'formal and business-like',
            'friendly': 'warm and conversational'
        }

        length_guide = {
            'short': '2-4 sentences',
            'medium': '1-2 paragraphs',
            'long': '3-4 detailed paragraphs'
        }

        prompt = f"""
Write an email that is {tone_style[tone]} and has a length of {length_guide[length]}.
Topic: {description}

Structure:
- Subject line
- Greeting
- Body (based on tone and length)
- Closing and signature

Respond with the full email only.
"""
        return self._generate(prompt)

    def improve_email(
        self,
        draft: str,
        tone: Literal['professional', 'friendly'] = 'professional',
        length: Literal['short', 'medium', 'long'] = 'medium'
    ) -> str:
        if not draft.strip():
            return "❌ Error: Draft email is empty."

        prompt = f"""
Improve the following draft email:

{draft}

Make it:
- More {tone}
- {length} in length
- Clear, grammatically correct, and well-formatted

Keep the message intent the same. Provide only the improved email.
"""
        return self._generate(prompt)


# Function-style API
def generate_email(description: str, tone="professional", length="medium", api_key=None):
    return EmailGenerator(api_key).generate_email(description, tone, length)

def improve_email(draft: str, tone="professional", length="medium", api_key=None):
    return EmailGenerator(api_key).improve_email(draft, tone, length)


# Example usage
if __name__ == "__main__":
    os.environ["MISTRAL_API_KEY"] = "your-mistral-api-key-here"

    gen = EmailGenerator()

    generated = gen.generate_email("Update client on project delay", tone="professional", length="medium")
    print("📧 Generated Email:\n", generated)

    improved = gen.improve_email("hey just wanted to say it's late sorry", tone="professional", length="medium")
    print("\n✅ Improved Email:\n", improved)