from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import rag

app = FastAPI(title="Bulking RAG Chatbot")
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatIn(BaseModel):
    question: str


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.post("/api/chat")
def chat(body: ChatIn):
    question = body.question.strip()
    if not question:
        return {"answer": "Please ask a question.", "sources": []}
    return rag.answer(question)
