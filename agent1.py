import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv


# Internal setup
def _load_api_key():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise EnvironmentError("API_KEY not found in .env file")
    return api_key


def _configure_gemini(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-pro")


def _extract_json(response_text: str):
    """Safely extracts JSON content from the model's response."""
    try:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("No valid JSON found in Gemini output.")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decoding failed: {e}")


# Main entry function
def detect_emotion(text):
    # Stubbed version; replace with real logic or ML model
    text = text.lower()
    if "not good" in text or "sad" in text:
        return {
            "primary_emotion": "sadness",
            "secondary_emotions": ["hopelessness"],
            "intensity": "moderate",
            "risk_factors": ["low mood"],
            "confidence": 0.82
        }
    elif "stressed" in text or "overwhelmed" in text:
        return {
            "primary_emotion": "anxiety",
            "secondary_emotions": ["stress", "worry"],
            "intensity": "high",
            "risk_factors": ["burnout risk"],
            "confidence": 0.88
        }
    else:
        return {
            "primary_emotion": "neutral",
            "secondary_emotions": [],
            "intensity": "mild",
            "risk_factors": [],
            "confidence": 0.65
        }
    

if __name__ == "__main__":
    text = input("Enter text: ")
    print(detect_emotion(text))