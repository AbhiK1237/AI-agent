import gradio as gr
from agent1 import detect_emotion
import random
import time

# ------------------------------------
# Emotion mapping for compatibility
# ------------------------------------

def map_emotion_to_ui_category(detected_emotion):
    """
    Maps the emotions returned by detect_emotion() to UI categories
    This ensures compatibility between the emotion detection and UI
    """
    # From your code, detect_emotion returns:
    # - "sadness" (not "sad")
    # - "anxiety" (not "stressed")
    # - "neutral"
    
    emotion_map = {
        "sadness": "sad",
        "anxiety": "stressed",  # Map to stressed UI category
        "neutral": "neutral",
        # Add any other mappings needed
        "anger": "angry",
        "stress": "stressed",
        "worry": "anxiety",
        # Fallback cases
        "sad": "sad",
        "angry": "angry",
        "stressed": "stressed"
    }
    
    return emotion_map.get(detected_emotion.lower(), "neutral")

# ------------------------------------
# Dynamic activities for each emotion
# ------------------------------------

def get_activity_for_emotion(emotion):
    """Return tailored activities based on detected emotion."""
    
    # First map the emotion to a UI category if needed
    ui_emotion = map_emotion_to_ui_category(emotion)
    
    activities = {
        "angry": {
            "title": "Release Your Tension",
            "description": "Click the button below to virtually release your anger.",
            "button_label": "💥 RELEASE",
            "style": "angry",
            "background": "linear-gradient(135deg, #ff4d4d, #ff8080)"
        },
        "sad": {
            "title": "Gentle Uplift",
            "description": random.choice([
                "You're stronger than you think. Each moment is a chance to begin again. 🌈",
                "Even the darkest nights end with dawn. Your light is still there. ☀️",
                "Take a deep breath. This feeling will pass, and you'll find your way through. 💜"
            ]),
            "button_label": "💖 More Support",
            "style": "sad",
            "background": "linear-gradient(135deg, #88bef5, #b8d8ff)"
        },
        "stressed": {
            "title": "Breathing Space",
            "description": "Let's take a moment to breathe together. Follow the pattern below.",
            "button_label": "🧘 Begin Breathing",
            "style": "stressed",
            "background": "linear-gradient(135deg, #ffbf00, #ffd966)"
        },
        "anxiety": {
            "title": "Grounding Exercise",
            "description": "Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.",
            "button_label": "🍃 Start Grounding",
            "style": "anxiety",
            "background": "linear-gradient(135deg, #a991ff, #c7b9ff)"
        }
    }
    
    # Default/neutral option
    default = {
        "title": "Let's Explore Together",
        "description": "How else can I support you today? Share more about what's on your mind.",
        "button_label": "✨ Continue",
        "style": "neutral",
        "background": "linear-gradient(135deg, #777, #999)"
    }
    
    return activities.get(ui_emotion, default)

# -----------------------------
# Custom HTML Components
# -----------------------------

def create_breathe_component():
    """Creates a simplified breathing animation that works in Gradio."""
    return """
    <div style="text-align: center; margin: 20px 0;">
        <div id="breathe-circle" style="
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: radial-gradient(circle, #ffbf00, #ffd966);
            box-shadow: 0 0 30px rgba(255, 191, 0, 0.5);
            margin: 0 auto;
            transition: transform 4s ease;
        "></div>
        <p id="breathe-text" style="
            margin-top: 15px;
            font-size: 1.2em;
            font-weight: 500;
            color: #555;
        ">Inhale...</p>
    </div>
    
    <script>
        setTimeout(function() {
            const circle = document.getElementById('breathe-circle');
            const text = document.getElementById('breathe-text');
            
            if (circle && text) {
                // Initial inhale
                circle.style.transform = 'scale(1.5)';
                text.innerText = 'Inhale...';
                
                // Animation sequence
                setTimeout(() => {
                    text.innerText = 'Hold...';
                    setTimeout(() => {
                        circle.style.transform = 'scale(1)';
                        text.innerText = 'Exhale...';
                    }, 7000);
                }, 4000);
            }
        }, 500);
    </script>
    """

def create_grounding_component():
    """Creates a simplified grounding exercise that works in Gradio."""
    return """
    <div style="
        margin: 20px 0;
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(169, 145, 255, 0.1);
    ">
        <div id="ground-step-1" style="
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            background-color: #a991ff;
            color: white;
            font-weight: bold;
            transform: translateX(10px);
            transition: all 0.5s ease;
            box-shadow: 0 5px 15px rgba(169, 145, 255, 0.4);
        ">5 things you can SEE</div>
        <div id="ground-step-2" style="
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            background-color: white;
            color: #666;
            opacity: 0.7;
            transition: all 0.5s ease;
        ">4 things you can TOUCH</div>
        <div id="ground-step-3" style="
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            background-color: white;
            color: #666;
            opacity: 0.7;
            transition: all 0.5s ease;
        ">3 things you can HEAR</div>
        <div id="ground-step-4" style="
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            background-color: white;
            color: #666;
            opacity: 0.7;
            transition: all 0.5s ease;
        ">2 things you can SMELL</div>
        <div id="ground-step-5" style="
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            background-color: white;
            color: #666;
            opacity: 0.7;
            transition: all 0.5s ease;
        ">1 thing you can TASTE</div>
    </div>
    """

# -----------------------------
# Main handler for user input
# -----------------------------

def process_input(user_text):
    """Process user input and adapt to the emotion detection output."""
    if not user_text.strip():
        return (
            "Please share your thoughts so I can understand your emotions.",
            "I'm Here to Listen",
            "Share what's on your mind and I'll respond with understanding.",
            "✏️ Start Typing",
            "neutral",
            "",  # No custom HTML content yet
            "linear-gradient(135deg, #777, #999)"  # Default background
        )
    
    # Detect emotion using the agent
    result = detect_emotion(user_text)
    
    # Debug print to see what's being returned
    print(f"Emotion detection result: {result}")
    
    # Extract relevant information
    primary_emotion = result.get("primary_emotion", "neutral")
    intensity = result.get("intensity", "moderate")
    secondary_emotions = result.get("secondary_emotions", [])
    
    # Get appropriate activity for the emotion
    activity = get_activity_for_emotion(primary_emotion)
    
    # Generate custom HTML content based on mapped emotion
    custom_html = ""
    ui_emotion = map_emotion_to_ui_category(primary_emotion)
    if ui_emotion == "stressed":
        custom_html = create_breathe_component()
    elif ui_emotion == "anxiety":
        custom_html = create_grounding_component()
    
    # Format emotional response
    emotion_display = f"**{primary_emotion.upper()}**"
    if secondary_emotions:
        emotion_display += f" with {', '.join(secondary_emotions)}"
    
    return (
        f"Detected Emotion: {emotion_display} (Intensity: {intensity})",
        activity["title"],
        activity["description"],
        activity["button_label"],
        activity["style"],
        custom_html,
        activity["background"]
    )

# -----------------------------
# Response handlers
# -----------------------------

def on_action_btn(emotion):
    """Handle action button clicks based on emotion."""
    # Map the emotion to UI category if needed
    ui_emotion = map_emotion_to_ui_category(emotion)
    
    responses = {
        "angry": {
            "message": "💥 Feel the tension release. What helped trigger these feelings today?"
        },
        "sad": {
            "message": random.choice([
                "💫 You're not alone in this. What small joy can you find today?",
                "🌱 Every feeling is valid. Would sharing more help lighten your load?",
                "🌈 I'm here with you. What's one tiny step that might feel possible right now?"
            ])
        },
        "stressed": {
            "message": "🧘 Notice how your breath centers you. What's one thing you could let go of today?"
        },
        "anxiety": {
            "message": "🍃 Grounding helps bring us back to the present. What's one thing you notice right now?"
        },
        "neutral": {
            "message": "Thank you for sharing. What else is on your mind today?"
        }
    }
    
    response = responses.get(ui_emotion, responses["neutral"])
    
    # Simulate processing time for better UX
    time.sleep(0.5)
    
    return gr.Markdown.update(value=response["message"])

# -----------------------------
# Gradio UI Configuration
# -----------------------------

def create_ui():
    """Create and configure the Gradio UI."""
    
    # Simplified CSS with fewer animations to avoid compatibility issues
    custom_css = """
    /* Base Styles */
    .container { max-width: 800px; margin: 0 auto; }
    
    /* Card styling */
    .emotion-card {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        padding: 20px;
        margin-top: 20px;
        transition: all 0.5s ease;
        position: relative;
        overflow: hidden;
    }
    
    /* Button Styles */
    .angry-button {
        background-color: #ff4d4d !important; 
        color: white !important; 
        border-radius: 25px !important;
        font-weight: bold !important;
    }
    
    .sad-button {
        background-color: #88bef5 !important; 
        color: white !important; 
        border-radius: 25px !important;
        font-weight: bold !important;
    }
    
    .stressed-button {
        background-color: #ffbf00 !important; 
        color: white !important; 
        border-radius: 25px !important;
        font-weight: bold !important;
    }
    
    .anxiety-button {
        background-color: #a991ff !important; 
        color: white !important; 
        border-radius: 25px !important;
        font-weight: bold !important;
    }
    
    .neutral-button {
        background-color: #777 !important; 
        color: white !important; 
        border-radius: 25px !important;
        font-weight: bold !important;
    }
    
    /* Simple fade-in animation */
    .fade-in {
        opacity: 0;
        animation: simpleFadeIn 0.8s forwards;
    }
    
    @keyframes simpleFadeIn {
        to { opacity: 1; }
    }
    
    /* Input Enhancement */
    .input-area textarea {
        border-radius: 15px !important;
        border: 2px solid #ddd !important;
        transition: all 0.3s ease !important;
    }
    
    .input-area textarea:focus {
        border-color: #888 !important;
        box-shadow: 0 0 0 2px rgba(136, 136, 136, 0.2) !important;
    }
    
    /* Header Styles */
    .header {
        background: linear-gradient(90deg, #5856d6, #7e7cef);
        color: white;
        padding: 20px;
        border-radius: 15px 15px 0 0;
        text-align: center;
        margin-bottom: 0;
    }
    
    .subheader {
        background-color: #F7FAFC;
        color: #4A5568;
        padding: 15px;
        text-align: center;
        border-radius: 0 0 15px 15px;
        margin-top: 0;
        margin-bottom: 25px;
    }
    """

    with gr.Blocks(css=custom_css) as demo:
        # Header Section with simplified styling
        gr.HTML("""
        <div class="header">
            <h2 style="margin:0">🧠 Emotion-Aware Assistant</h2>
        </div>
        <div class="subheader">
            <p style="margin:0">Share your feelings, and I'll provide personalized support.</p>
        </div>
        """)
        
        # Input Area
        with gr.Row():
            with gr.Column(elem_classes=["input-area"]):
                user_input = gr.Textbox(
                    placeholder="What's on your mind today? I'm here to listen...",
                    label="Your Thoughts",
                    lines=3
                )
                submit_btn = gr.Button("Analyze My Feelings", variant="primary")
        
        # Create a container for the dynamic content
        with gr.Row() as emotion_container:
            # This will hold our dynamic content
            with gr.Column(elem_classes=["emotion-card"]) as emotion_card:
                emotion_out = gr.Markdown("", elem_classes=["fade-in"])
                title_out = gr.Markdown("", elem_classes=["fade-in"])
                desc_out = gr.Markdown("", elem_classes=["fade-in"])
                
                # Container for custom HTML content (breathing animations, etc.)
                custom_html_out = gr.HTML("")
                
                action_btn = gr.Button("", elem_id="action_button")
        
        # Hidden states
        hidden_emotion = gr.State(value="neutral")
        background_style = gr.State(value="")
        
        # Set up event handlers
        def update_ui(user_text):
            try:
                emo_label, title, desc, btn_label, style, custom_html, bg = process_input(user_text)
                
                # Update button class based on emotion
                class_map = {
                    "angry": "angry-button",
                    "sad": "sad-button",
                    "stressed": "stressed-button",
                    "anxiety": "anxiety-button",
                    "neutral": "neutral-button"
                }
                action_btn.elem_classes = [class_map.get(style, "neutral-button")]
                
                # Update the card style
                emotion_card.style.update(background=bg)
                
                # Return the values needed for updates
                return emo_label, title, desc, btn_label, style, custom_html, bg
            except Exception as e:
                print(f"Error in update_ui: {e}")
                # Return defaults in case of error
                return (
                    "Error processing emotions",
                    "Let's try again",
                    f"There was an error: {str(e)}. Please try a different phrase.",
                    "Try Again",
                    "neutral",
                    "",
                    "linear-gradient(135deg, #777, #999)"
                )
        
        submit_btn.click(
            fn=update_ui, 
            inputs=[user_input], 
            outputs=[emotion_out, title_out, desc_out, action_btn, hidden_emotion, custom_html_out, background_style]
        )
        
        # Handle action button clicks
        action_btn.click(
            fn=on_action_btn, 
            inputs=[hidden_emotion], 
            outputs=[desc_out]
        )
        
        # JavaScript for updating background
        gr.HTML("""
        <script>
        // Simple function to update card background
        function updateCardBackground(bgValue) {
            const card = document.querySelector('.emotion-card');
            if (card && bgValue) {
                card.style.background = bgValue;
                card.style.transition = 'background 0.5s ease';
            }
        }
        </script>
        """)

    return demo

# -----------------------------
# Launch the Gradio app
# -----------------------------

if __name__ == "__main__":
    app = create_ui()
    app.launch(share=True)