import os
import requests

ALLTOGETHER_API_KEY = os.getenv("ALLTOGETHER_API_KEY")
LLM_ENDPOINT = "https://api.together.xyz/v1/chat/completions"

def get_summary_from_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {ALLTOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "messages": [
            {"role": "user", "content": f"Summarize the following task updates:\n{prompt}"}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = requests.post(LLM_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Failed to get summary: {str(e)}"
