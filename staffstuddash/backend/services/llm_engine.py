import os
from groq import Groq
from dotenv import load_dotenv

# Load env vars from .env file if present
load_dotenv()

# Initialize Groq client
# Ensure GROQ_API_KEY is set in your environment
api_key = os.environ.get("GROQ_API_KEY")
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")


def analyze_thinking_quality(previous_text: str, current_text: str) -> float:
    """
    Uses Groq API to analyze the quality of thinking between two drafts.
    Returns a score between 0.0 and 1.0.
    """
    
    prompt = f"""
    You are an AI that evaluates student effort and thinking quality.
    Compare the following two drafts of a student's answer.
    
    Draft 1 (Previous):
    "{previous_text}"
    
    Draft 2 (Current):
    "{current_text}"
    
    Analyze the changes. Did the student improve their reasoning, add new details, or refine their understanding? 
    Or is it just a trivial change (spelling, minor formatting)?
    
    Return ONLY a single float number between 0.0 (no thinking/effort) and 1.0 (deep thinking/high effort).
    Do not add any explanation or text, just the number.
    """

    try:
        if not client:
            raise ValueError("Groq client not initialized (missing API key)")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a scoring engine. Output only a float score.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192", # Defaulting to a strong model on Groq
            temperature=0.0,
        )
        
        content = chat_completion.choices[0].message.content.strip()
        
        # specific safeguard for non-numeric return
        try:
           score = float(content)
           # Clamp between 0 and 1 just in case
           return max(0.0, min(score, 1.0))
        except ValueError:
           # Fallback if model talks instead of giving a number
           return 0.5 

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        # Fallback to simple heuristic if API fails (e.g. no key)
        if len(current_text) > len(previous_text) * 1.2:
            return 0.7
        return 0.3

