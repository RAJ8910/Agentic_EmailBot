# 🧠 AI Email Bot for Insurance Industry

An AI-powered email assistant for insurance companies that automatically responds to customer queries via email and web, with contextual awareness, intelligent automation, and seamless integration with internal systems.

---

## 🚀 Features

- 📧 **Gmail Integration**  
  Automatically reads customer emails, processes queries, and sends replies directly from your Gmail inbox.

- 📄 **Policy Copy Generation**  
  Fetches customer data from the database, generates a policy PDF from a template, and sends it via email.

- 🛠️ **Claim Status & Registration**  
  Provides real-time claim status or registers new claims using internal databases.

- 📚 **RAG-Based General Queries**  
  Answers general insurance-related questions using Retrieval-Augmented Generation (RAG) from internal documents.

- 😠 **Sentiment & Tone Detection**  
  Detects urgency or negative sentiment in customer messages and prioritizes accordingly if the task fails.

- 📝 **Conversation Tracking**  
  Logs all customer interactions for audit and analytics.

---

## 📦 Installing Dependencies

Make sure you have [uv](https://pypi.org/project/uv/) and Python 3.10+ installed.

```bash
uv pip install -r requirements.txt
```

---

## 🖥️ Running the Application

### 1. 🔧 Run the Backend (FastAPI)

```bash
uvicorn main:app --reload --port 8000
```

### 2. 💡 Run the Frontend (Streamlit)

```bash
streamlit run streamlit_app.py
```

### 3. 📬 Start the Email Watcher (Gmail Integration)

```bash
python email_watcher.py
```

---

## ⚙️ Gmail Integration Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the Gmail API and create OAuth 2.0 credentials.
3. Download `credentials.json` and place it in your project root.
4. On first run, authenticate in your browser when prompted.

---

## 📁 Project Structure

- `main.py` — FastAPI backend for query processing and tracking.
- `streamlit_app.py` — Streamlit frontend for chat and analytics.
- `email_watcher.py` — Watches Gmail inbox, processes and replies to emails.

---

## 📝 Notes

- Update `.env` with your database and API keys.
- Only emails from allowed senders (see `ALLOWED_CUSTOMERS` in [`email_watcher.py`](email_watcher.py)) are processed.
- All interactions are logged in the database for audit and analytics.
