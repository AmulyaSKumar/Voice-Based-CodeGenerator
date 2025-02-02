# Voice-Based Code Generator

This is a **Voice-Based Code Generator** built using **Flask, HTML, CSS, and JavaScript**. The application integrates **Gemini AI API** to generate code based on voice input.

## Features
- Voice-to-text conversion for code generation
- Gemini AI API integration for intelligent code suggestions
- Web interface built with HTML, CSS, and JavaScript
- Flask backend for API handling

---

## Installation

### **Method 1: Using System Python (Recommended)**
1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-repo/voice-code-generator.git
   cd voice-code-generator
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Create a `.env` file** and add your **Gemini API Key**:
   ```sh
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
4. **Run the Flask application:**
   ```sh
   python app.py
   ```

---

### **Method 2: Using Virtual Environment**
1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-repo/voice-code-generator.git
   cd voice-code-generator
   ```
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   - **Windows:**
     ```sh
     venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```sh
     source venv/bin/activate
     ```
4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
5. **Create a `.env` file** and add your **Gemini API Key**:
   ```sh
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
6. **Run the Flask application:**
   ```sh
   python app.py
   ```

---

## **Usage**
1. Open your browser and go to `http://127.0.0.1:5000`
2. Click the **"Start Voice Input"** button and speak your coding request
3. The generated code will be displayed based on your voice command



