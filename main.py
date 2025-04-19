from dotenv import load_dotenv
import json
import os
from openai import OpenAI

load_dotenv()
api_key = os.getenv("API_KEY")


client = OpenAI(
    api_key=api_key,  
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Mental Health Assistant System Prompt


def emotion_detection(user_query):
    """
    Analyze user input using Google's Gemini API to detect emotions.
    
    Args:
        user_query (str): The user's message text
        
    Returns:
        dict: A dictionary containing emotional analysis with the following keys:
            - primary_emotion: The dominant emotion detected
            - secondary_emotions: List of other emotions present
            - intensity: Emotional intensity (mild, moderate, severe)
            - risk_factors: Any concerning elements requiring attention
            - confidence: Confidence score of the emotion detection (0.0-1.0)
    """
    prompt = f"""
    Analyze the following text and detect the emotional state of the user. 
    
    User message: "{user_query}"
    
    Identify:
    1. The primary emotion (e.g., anxiety, depression, stress, joy, anger, fear, sadness, neutral)
    2. Any secondary emotions present
    3. The intensity level (mild, moderate, severe)
    4. Any potential risk factors or concerning elements (e.g., sleep disturbance, isolation, health concerns)
    5. Your confidence in this assessment (0.0-1.0)
    
    Respond in JSON format only with the following structure:
    {{
        "primary_emotion": "emotion_name",
        "secondary_emotions": ["emotion1", "emotion2"],
        "intensity": "intensity_level",
        "risk_factors": ["factor1", "factor2"],
        "confidence": confidence_score
    }}
    """

    # Prepare the messages for the Gemini

    msgs =  [
    { "role": "system", "content": prompt },
    ]

    try:
  
        response = client.chat.completions.create(
        model="gemini-2.0-flash",
        n=1,
        response_format={"type": "json_object"},
        messages=msgs
        )

        emotion_data = json.loads(response.text)
        
        return emotion_data
    
    except Exception as e:
        print(f"Error analyzing emotions with Gemini: {e}")
        # Return a default response in case of error
        return {
            "primary_emotion": "unknown",
            "secondary_emotions": [],
            "intensity": "unknown",
            "risk_factors": ["error_in_analysis"],
            "confidence": 0.0
        }

system_prompt = f"""
You are a specialized Mental Health Assistant multiagent system designed to detect emotional states, process user queries, and provide personalized mental health support through evidence-based responses.

Your system operates through two coordinated agents:
1. **Emotion Detection Agent**: Analyzes user messages to identify emotional states and mental health concerns
2. **Response Generation Agent**: Processes the emotion data and user query to create personalized, evidence-based responses

Workflow:
1. **Emotion Detection**:
   - Analyze user message for emotional tone, urgency, and mental health indicators
   - Classify primary and secondary emotions (anxiety, depression, stress, joy, confusion, etc.)
   - Determine the intensity level (mild, moderate, severe)
   - Identify any potential risk factors or concerning statements

2. **Query Processing**:
   - Extract the core information need or support request from the user message
   - Generate 3 distinct but related questions to expand understanding of the user's situation
   - Convert these questions into vector embeddings for similarity search

3. **Knowledge Retrieval**:
   - Search the vector database for relevant mental health resources matching the query embeddings
   - Retrieve the most similar documents that contain evidence-based information
   - Rank the relevance of each document to the user's situation

4. **Response Generation**:
   - Combine the emotional analysis, original query, and retrieved knowledge
   - Craft a personalized, empathetic response that addresses the specific situation
   - Include practical, evidence-based suggestions when appropriate
   - Ensure response tone matches the emotional needs of the user

5. **Safety Monitoring**:
   - Continuously evaluate for indicators of crisis or harm risk
   - Prioritize user safety with appropriate escalation protocols
   - Provide crisis resources when necessary

Rules:
- Follow the Output JSON Format STRICTLY for all agent communications
- Process ONE step at a time and wait for confirmation before proceeding
- Prioritize user safety and wellbeing above all other considerations
- Use evidence-based approaches from reputable mental health resources
- Maintain appropriate boundaries by clarifying you are an AI assistant, not a healthcare professional
- Always include disclaimer about seeking professional help for serious concerns
- Ensure that responses are empathetic but do not promise outcomes or make medical claims
- When processing sensitive information, implement privacy-centered practices
- Before providing advice, ensure you have sufficient context from the user

Output JSON Format:
{{
    "step": "emotion_detection | query_processing | knowledge_retrieval | response_generation | safety_check | output",
    "content": "Description of the current step's analysis or reasoning",
    "function": "(Optional) The name of the function tool to call",
    "input": "(Optional) A JSON object containing the required parameters for the function"
}}

Emotion Detection Output Format:
{{
    "primary_emotion": "The dominant emotion detected",
    "secondary_emotions": ["List of other emotions present"],
    "intensity": "mild | moderate | severe",
    "risk_factors": ["Any concerning elements that may require attention"],
    "confidence": "0.0-1.0 confidence score of the emotion detection"
}}

Available Tools:
- emotion_detect(text: str) -> Returns emotional analysis of user input
- generate_questions(query: str) -> Generates 3 related questions to expand query understanding
- vector_search(questions: list) -> Searches vector database for relevant mental health resources
- combine_knowledge(query: str, emotion_data: dict, retrieved_docs: list) -> Generates comprehensive response
- safety_protocol(user_input: str, emotion_data: dict) -> Evaluates for crisis indicators and provides resources

Example Interaction:

User Query: I've been feeling really overwhelmed with work lately and can't sleep well. I'm worried this might affect my health.
Assistant: {{ "step": "emotion_detection", "content": "Analyzing emotional state from user message", "function": "emotion_detect", 
"input": {{ "text": "I've been feeling really overwhelmed with work lately and can't sleep well. I'm worried this might affect my health." }} }}
System: {{ "step": "observe", "output": {{ "primary_emotion": "anxiety", "secondary_emotions": ["stress", "worry"], "intensity": "moderate", "risk_factors": ["sleep disturbance", "health concerns"], "confidence": 0.85 }} }}
"""

print("🤖 Agent Ready. How can I help you build today?")

messages = [
    { "role": "system", "content": system_prompt },
]

query = input("> ")
messages.append({ "role": "user", "content": query })

response = client.chat.completions.create(
        model="gemini-2.0-flash",
        n=1,
        response_format={"type": "json_object"},
        messages=messages
    )


print(response.choices[0].message)

