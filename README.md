# 🤖 AI Chatbot

A conversational AI chatbot built with FastAPI, Streamlit and Ollama.

## 🚀 Tech Stack
- **Frontend:** Streamlit
- **Backend:** FastAPI
- **LLM Engine:** Ollama (Llama 3.2:3b)

## ⚙️ Setup

### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-chatbot.git

### 2. Install dependencies
pip install -r requirements.txt

### 3. Create .env file
OLLAMA_URL=http://localhost:11434

### 4. Run Ollama
ollama serve
ollama pull llama3.2:3b

### 5. Start Backend
uvicorn main:app --reload

### 6. Start Frontend
streamlit run frontend.py

## 📌 Features
- 💬 Real time streaming responses
- 🌗 Dark/Light theme toggle
- 📜 Chat history
- 🗑️ Clear chat button
- 🧠 Conversation memory
