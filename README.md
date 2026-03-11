# 🌿 AgroLens AI | Smart Plant Doctor

AgroLens is an AI-powered agricultural assistant designed to instantly diagnose crop diseases and provide actionable, localized expert advice to farmers. Built with a custom Flask backend and integrated with state-of-the-art vision and language models.

**🚀 Live Demo:**(https://huggingface.co/spaces/Mayukh77/AgroLens)

## ✨ Key Features
* **AI Vision Diagnostics:** Upload a leaf photo, and our Vision Transformer (ViT) model instantly detects diseases across Rice, Corn, Wheat, and Potato crops.
* **Smart Weather Context:** Automatically fetches real-time local weather data (temperature and humidity) to adjust AI prescriptions (e.g., warning against spraying fungicides before rain).
* **Multi-Lingual AgroBot:** A conversational AI assistant powered by Gemini that answers farming queries. Native translation support for English, Hindi, and Bengali.
* **Accessibility First:** Integrated Web Speech API for hands-free voice-to-text input.
* **Offline Reports:** One-click PDF generation of the diagnostic report and AI prescription for farmers to take to local agricultural stores.

## 🛠️ Technical Stack
* **Backend:** Python, Flask, Docker
* **Machine Learning:** PyTorch, Hugging Face `transformers` (`wambugu71/crop_leaf_diseases_vit`)
* **LLM Integration:** Google Gemini API (`gemini-3.1-flash-lite-preview`), LangChain
* **Frontend:** HTML5, JavaScript, Tailwind CSS (Dark Mode Glassmorphism UI)
* **APIs:** Open-Meteo (Weather), Web Speech API, Geolocation API

## 💻 Local Setup Instructions
To run AgroLens on your local machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mayukh-7/Texibition-AgroLens.git](https://github.com/mayukh-7/Texibition-AgroLens.git))
   cd AgroLens

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
