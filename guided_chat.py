from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import UserResponse, User, Scheme
from services.matching import find_matching_schemes
from services.rag import get_full_rag_context
import requests

router = APIRouter()

class GuidedChatRequest(BaseModel):
    user_id: int
    age: int
    gender: str
    occupation: str
    income: float
    state: str

def call_ollama(prompt: str) -> str:
    """
    Call Ollama LLaMA 3 Instruct API for AI responses with RAG
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
            return result.get("response", "Unable to get AI response")
        else:
            return "Unable to get AI response"
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama server"
    except Exception as e:
        return f"Error: {str(e)}"

@router.post("/")
def guided_chat(request: GuidedChatRequest, db: Session = Depends(get_db)):
    """
    Guided chat flow with RAG for eligibility checking
    
    Flow:
    1. RETRIEVE: Get matching schemes from database + user profile
    2. AUGMENT: Create prompt with retrieved context
    3. GENERATE: Send augmented prompt to AI
    """
    
    # Check if user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Store user responses
    user_response = UserResponse(
        user_id=request.user_id,
        age=request.age,
        gender=request.gender,
        occupation=request.occupation,
        income=request.income,
        state=request.state
    )
    
    db.add(user_response)
    db.commit()
    
    # Prepare user data for matching
    user_data = {
        "age": request.age,
        "gender": request.gender,
        "occupation": request.occupation,
        "income": request.income,
        "state": request.state
    }
    
    # Find top 5 matching schemes
    matching_schemes = find_matching_schemes(user_data, db, limit=5)
    
    # RETRIEVE: Format schemes for RAG context
    schemes_context = "📋 TOP MATCHING SCHEMES FROM DATABASE:\n\n"
    for index, item in enumerate(matching_schemes, 1):
        scheme = item["scheme"]
        score = item["score"]
        schemes_context += f"""{index}. **{scheme.name}** ({score}% match)
   - Description: {scheme.description}
   - Category: {scheme.category}
   - Eligibility: {scheme.eligibility}
   - Benefits: {scheme.benefits}

"""
    
    # AUGMENT: Create prompt with context
    augmented_prompt = f"""You are an expert in Indian government schemes with access to a database.

📊 USER PROFILE:
- Age: {request.age} years
- Gender: {request.gender}
- Occupation: {request.occupation}
- Annual Income: ₹{request.income:,}
- State: {request.state}

{schemes_context}

TASK:
Analyze the user profile against the matching schemes provided above.
Explain which schemes they are most eligible for and why.
Reference the specific eligibility criteria and benefits from the database.
Provide personalized advice (3-4 sentences).

ANSWER:
"""
    
    # GENERATE: Get AI response with augmented context
    ai_explanation = call_ollama(augmented_prompt)
    
    # Format response
    return {
        "status": "success",
        "message": "Eligibility check completed successfully",
        "user_profile": {
            "age": request.age,
            "gender": request.gender,
            "occupation": request.occupation,
            "income": request.income,
            "state": request.state
        },
        "matching_schemes": [
            {
                "rank": index + 1,
                "name": item["scheme"].name,
                "category": item["scheme"].category,
                "description": item["scheme"].description,
                "match_percentage": item["percentage"],
                "eligibility": item["scheme"].eligibility,
                "benefits": item["scheme"].benefits
            }
            for index, item in enumerate(matching_schemes)
        ],
        "ai_recommendation": ai_explanation,
        "rag_info": {
            "source": "RAG (Retrieval-Augmented Generation)",
            "retrieved_schemes": len(matching_schemes),
            "context_used": "Database schemes + User profile"
        }
    }