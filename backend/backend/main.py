from fastapi import FastAPI
from pydantic import BaseModel
from state_machine import handle_message

app = FastAPI(title="Novex AI Service Desk")

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    state: str

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = handle_message(
        session_id=req.session_id,
        message=req.message
    )
    return {
        "reply": result["reply"],
        "state": result["state"]
    }
