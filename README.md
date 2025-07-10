# 🧠 AI Email Bot for Insurance Industry

An AI-powered email assistant designed for insurance companies to automatically respond to customer queries with contextual awareness, intelligent automation, and seamless integration with internal systems.

---

## 🚀 Features

- 📄 **Policy Copy Generation**  
  Fetches customer data from the database, generates a policy PDF from a template, and sends it via email.

- 🛠️ **Claim Status & Registration**  
  Provides real-time claim status or registers new claims using internal databases.

- 📚 **RAG-Based General Queries**  
  Answers general insurance-related questions using Retrieval-Augmented Generation (RAG) from internal documents.

- 😠 **Sentiment & Tone Detection**  
  Detects urgency or negative sentiment in customer messages and prioritizes accordingly if the task fails. 

---

## 📦 Installing Dependencies

Make sure you have [uv](https://pypi.org/project/uv/) and Python 3.10+ installed.

```bash
uv pip install -r requirements.txt
```

## 🖥️ Running the Application

# 🔧 Run the Backend (FastAPI)

```bash
uvicorn main:app --reload --port 8000
```

# 💡 Run the Frontend (Streamlit)

```bash
streamlit run streamlit_app.py
```
