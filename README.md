# 🧠 AI Task Management Dashboard with Agent Automation

This project is an intelligent task management backend built with **FastAPI** and **SQLite**. It includes AI agents that automate **task assignment**, **employee notifications**, and **daily task summary generation** using LLMs.

---

## 🚀 Features

- **Role-Based User System**: Register as `admin`, `manager`, or `employee`
- **Task Assignment Agent**: Automatically assigns tasks based on employee skills
- **Notification Agent**: Notifies employees upon task assignment or summary
- **Summary Agent**: Generates daily reports and summaries using LLM
- **FastAPI Swagger Docs** for testing all endpoints interactively
- SQLite database for lightweight and easy storage

---

## 🛠 Tech Stack

- **Python 3.10+**
- **FastAPI** - Web framework
- **SQLite** - Relational database
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **dotenv** - Environment variable management
- **httpx / requests** - HTTP calls
- **Any LLM provider** (like AllTogetherAI / OpenAI) for summaries

---


---

## ⚙️ Setup Instructions

 1. Clone the repository
git clone https://github.com/RautAtharv07/AI_Task_dashboard.git
cd AI_Task_dashboard

 2. Create a virtual environment
python -m venv .venv

 3. Activate the virtual environment
 On Windows:
.venv\Scripts\activate
 On macOS/Linux:
source .venv/bin/activate

 4. Install dependencies
pip install -r requirements.txt

 5. Create a .env file in the root directory with the following keys
(Use your actual API key and email config)
-echo "OPENAI_API_KEY=your_openai_key_here
-EMAIL_SENDER=your_verified_email@example.com
-SMTP_PASSWORD=your_smtp_password
-SMTP_SERVER=smtp.your_email_provider.com
-SMTP_PORT=587" > .env

 7. Start the FastAPI server
uvicorn main:app --reload

Open your browser at: http://127.0.0.1:8000/docs
