from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.retriever import retrieve
from typing import Optional
from uuid import uuid4
import json
import urllib.request
import urllib.error

# Temporary conversation memory 
conversation_memory = {}
MAX_HISTORY = 10


app = FastAPI(
    title="GeoPulse AI",
    description="Agentic AI platform for geopolitical intelligence",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@app.get("/")
def home():
    return {
        "message": "Welcome to GeoPulse AI",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }




@app.post("/api/agent")
def chat(request: ChatRequest):
    import json
    import urllib.request
    import urllib.error

    conversation_id = request.conversation_id or str(uuid4())
    history = conversation_memory.get(conversation_id, [])
    history_text = "\n".join(
        f"{item['role']}: {item['content']}" for item in history)

    results = retrieve(request.message)
    print("\n--- RETRIEVED CONTEXT --- ")
    for result in results:
        print("SOURCE:", result.get("filename"))
        print(result.get("context", ""))

    if not results:
        return {
            "conversation_id": conversation_id,
            "question": request.message,
            "answer": (
                "I couldn't find relevant information "
                "in the GeoPulse knowledge base."
            ),
            "sources": []
        }

    context = "\n\n".join(
        result["content"]
        for result in results
        if result.get("content")
    )

    source_names = list(dict.fromkeys(
        result["filename"]
        for result in results
        if result.get("filename")
    ))

    prompt = f"""
You are GeoPulse AI, a geopolitical research assistant.

Answer the user's question using only the supplied context.
Do not invent facts or claim the context supports something it does not.
If the context is insufficient, clearly say so.
Write a clear, concise answer.

Distinguish facts explicitly stated in the context from explanations or inteferences.
Do not invent historical or legal reasons that the context does not provide.
If the context does not explain why something is true, say so.
Preserve important qualifications and exceptions from the context.

CONVERSATION HISTORY:
{history_text}


CONTEXT:
{context}

USER QUESTION:
{request.message}
"""

    payload = {
        "model": "llama3.2:1b",
        "prompt": prompt,
        "stream": False
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = result.get("response", "").strip()

      
    except urllib.error.URLError:
        return {
            "conversation_id": conversation_id,
            "question": request.message,
            "answer": "GeoPulse AI could not connect to Ollama. Please make sure Ollama is running.",
            "sources": source_names
        }
  

        
    if not answer:
     answer = "The local model returned an empty answer."

# Save the current question and answer
    history.append({
    "role": "user",
    "content": request.message
})

    history.append({
    "role": "assistant",
    "content": answer
})

# Keep only the latest MAX_HISTORY messages
    conversation_memory[conversation_id] = history[-MAX_HISTORY:]

    return {
        "conversation_id": conversation_id,
        "question": request.message,
        "answer": answer,
        "sources": source_names
}
