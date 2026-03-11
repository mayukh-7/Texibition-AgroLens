from flask import Flask, render_template, request, jsonify, session
from transformers import pipeline
from PIL import Image
import io
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

app = Flask(__name__)
app.secret_key = "super_secret_agrolens_key" 

print("Loading Vision Model...")
viz_pipe = pipeline("image-classification", model="wambugu71/crop_leaf_diseases_vit")
print("Vision Model Loaded.")

def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview", 
        temperature=0.7,
        api_key=api_key
    )

def parse_prediction(label):
    known_crops = ["Corn", "Potato", "Rice", "Wheat"]
    detected_crop = "Unidentified"
    clean_label = label.replace("___", " ").replace("_", " ")
    for crop in known_crops:
        if crop.lower() in clean_label.lower():
            detected_crop = crop
            break 
    detected_disease = clean_label.replace(detected_crop, "").strip() if detected_crop != "Unidentified" else clean_label
    return detected_crop, detected_disease.title()

def get_expert_remedy(disease, crop, llm, language, weather):
    template = """
    You are an expert agriculturalist and plant doctor.
    The user has uploaded a photo of a {crop} leaf. 
    Our vision system has detected the condition: "{disease}".
    Current Local Weather: {weather}
    
    Please provide:
    1. A brief confirmation of what this disease looks like.
    2. A step-by-step recommended treatment. If the weather affects the treatment (like rain washing away spray), mention it.
    3. A preventative measure.
    
    CRITICAL INSTRUCTION: You must translate your entire response into {language}. Keep it simple for a farmer to understand.
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm 
    
    try:
        response = chain.invoke({
            "crop": crop, 
            "disease": disease, 
            "language": language, 
            "weather": weather
        })
        
        # Manually extract text from 3.1 Flash-Lite's list format
        content = response.content
        if isinstance(content, list):
            return content[0].get('text', '')
        return str(content)
        
    except Exception as e:
        print(f"LLM Error in analyze: {str(e)}")
        return f"⚠️ AI Error generating prescription: {str(e)}"

@app.route('/')
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    language = request.form.get('language', 'English')
    weather = request.form.get('weather', 'Unknown')
    
    image = Image.open(io.BytesIO(file.read()))
    
    results = viz_pipe(image)
    top = results[0]
    final_crop, final_disease = parse_prediction(top['label'])
    confidence = top['score']
    
    llm = get_llm()
    if not llm:
        return jsonify({"error": "Backend Error: GOOGLE_API_KEY is missing from .env!"}), 500
        
    # GUARD CLAUSE: Prevent LLM hallucination on non-leaf images
    if final_crop == "Unidentified" or "Invalid" in final_disease or "background" in final_disease.lower():
        final_disease = "Not a Supported Leaf"
        remedy = "⚠️ The vision system could not recognize a supported crop. Please ensure you are uploading a clear, focused photo of a Corn, Potato, Rice, or Wheat leaf."
    else:
        remedy = get_expert_remedy(final_disease, final_crop, llm, language, weather)
    
    return jsonify({
        "crop": final_crop,
        "disease": final_disease,
        "confidence": confidence,
        "remedy": remedy,
        "is_healthy": "Healthy" in final_disease
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('message')
    language = data.get('language', 'English')
    weather = data.get('weather', 'Unknown')
    
    llm = get_llm()
    if not llm:
        return jsonify({"response": "⚠️ Backend Error: GOOGLE_API_KEY is missing from .env!"}), 500
    
    lc_history = []
    for msg in session.get('chat_history', []):
        if msg['role'] == 'user':
            lc_history.append(HumanMessage(content=msg['content']))
        else:
            lc_history.append(AIMessage(content=msg['content']))
            
    system_prompt = """
    You are AgroBot, an expert AI Agricultural Consultant. 
    Current Local Weather of the farmer: {weather}. Use this to give smart advice if relevant.
    Answer questions practically and concisely. 
    CRITICAL: You must reply entirely in {language}.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm 
    
    try:
        response = chain.invoke({
            "history": lc_history,
            "input": user_query,
            "language": language,
            "weather": weather
        })
        
        # Manually extract text from 3.1 Flash-Lite's list format
        content = response.content
        if isinstance(content, list):
            response_text = content[0].get('text', '')
        else:
            response_text = str(content)
            
    except Exception as e:
        print(f"LLM Error in chat: {str(e)}")
        return jsonify({"response": f"⚠️ AI Error: {str(e)}"}), 500
    
    history = session.get('chat_history', [])
    history.append({'role': 'user', 'content': user_query})
    history.append({'role': 'assistant', 'content': response_text})
    session['chat_history'] = history
    
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)
