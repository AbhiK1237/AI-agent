import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from agent1 import detect_emotion

# Load environment variables
load_dotenv()

# Retrieve the Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# Define system prompt for the Gemini model
SYSTEM_PROMPT = """
You are a specialized Mental Health Assistant multiagent system designed to detect emotional states, process user queries, and provide personalized mental health support through evidence-based responses.
Your system operates through two coordinated agents:
1. Emotion Detection Agent
2. Response Generation Agent

Workflow:
1. Detect emotion from the user input
2. Generate relevant questions to understand the query better
3. Search vector DB for evidence-based content
4. Generate a supportive response
5. Run safety checks

Output JSON format:
{
 "step": "emotion_detection | query_processing | knowledge_retrieval | response_generation | safety_check | output",
 "content": "Step description",
 "function": "(Optional) Function to call",
 "input": "(Optional) Parameters for the function"
}
"""

# Dispatcher: maps function names to Python functions
def function_dispatcher(function_name, input_data):
    if function_name == "emotion_detect":
        return detect_emotion(input_data["text"])
    else:
        return {"error": f"Function '{function_name}' not implemented."}

# Main entry function
def main():
    try:
        query = input("\n👤 User: ").strip()
        
        # Create a generative model instance
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        
        # Send request to Gemini model
        response = model.generate_content(
            contents=SYSTEM_PROMPT + "\nUser: " + query,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=512
            )
        )
        
        # Get text from response
        assistant_msg = response.text
        
        print("\n🤖 Assistant Response:")
        print(assistant_msg)
        
        # Try to parse the response into JSON
        parsed = json.loads(assistant_msg)
        step = parsed.get("step")
        function_name = parsed.get("function")
        input_data = parsed.get("input")
        
        if function_name and input_data:
            print(f"\n⚙️ Executing Function: {function_name}")
            result = function_dispatcher(function_name, input_data)
            print("✅ Function Output:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\n📌 Step: {step}")
            print(f"📝 Content: {parsed.get('content')}")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()