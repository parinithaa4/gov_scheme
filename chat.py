from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import User
from services.rag import get_full_rag_context
import requests

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    question: str

def call_ollama(prompt: str) -> str:
    """
    Call Ollama LLaMA 3 Instruct API for AI responses
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:instruct",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response from AI")
        else:
            return f"Ollama error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Make sure 'ollama serve' is running"
    except Exception as e:
        return f"Error: {str(e)}"

@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    General chat endpoint with RAG (Retrieval-Augmented Generation)
    
    Flow:
    1. RETRIEVE: Search database for relevant schemes
    2. AUGMENT: Add context to prompt
    3. GENERATE: Send augmented prompt to AI
    """
    
    # Get user
    user = db.query(User).filter(User.id == request.user_id).first()
    
    # RETRIEVE + AUGMENT: Get context from database
    augmented_prompt, retrieved_count = get_full_rag_context(
        request.question, 
        request.user_id, 
        db
    )
    
    # GENERATE: Get AI response with context
    ai_response = call_ollama(augmented_prompt)
    
    return {
        "user_id": request.user_id,
        "question": request.question,
        "answer": ai_response,
        "retrieved_schemes": retrieved_count,
        "note": "Answer generated using RAG (Retrieval-Augmented Generation)"
    }