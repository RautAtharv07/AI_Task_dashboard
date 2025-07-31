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

1. **Clone the repository**  
   ```bash
   git clone https://github.com/RautAtharv07/AI_Task_dashboard.git
   cd AI_Task_dashboard
Create and activate a virtual environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Configure environment variables
Create a .env file and add your keys:

ini
Copy
Edit
LLM_API_KEY=your_api_key_here
Run the application

bash
Copy
Edit
uvicorn main:app --reload
Access Swagger Docs
Open your browser at: http://127.0.0.1:8000/docs
