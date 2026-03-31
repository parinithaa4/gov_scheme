from sqlalchemy.orm import Session
from models import Scheme

def retrieve_schemes_context(query: str, db: Session, limit: int = 5) -> str:
    """
    Retrieve relevant schemes from database based on query
    This is the RETRIEVAL part of RAG
    """
    
    # Search for schemes matching the query
    schemes = db.query(Scheme).filter(
        (Scheme.name.ilike(f"%{query}%")) |
        (Scheme.description.ilike(f"%{query}%")) |
        (Scheme.category.ilike(f"%{query}%")) |
        (Scheme.eligibility.ilike(f"%{query}%"))
    ).limit(limit).all()
    
    # If no schemes found, return empty context
    if not schemes:
        return "No specific schemes found in database."
    
    # Format schemes into context string
    context = "📋 Retrieved from Database:\n\n"
    
    for i, scheme in enumerate(schemes, 1):
        context += f"""{i}. **{scheme.name}**
   - Description: {scheme.description}
   - Category: {scheme.category}
   - Eligibility: {scheme.eligibility}
   - State: {scheme.state}
   - Benefits: {scheme.benefits}

"""
    
    return context


def generate_rag_prompt(query: str, context: str) -> str:
    """
    Create a prompt that includes retrieved context
    This is the AUGMENTATION part of RAG
    """
    
    prompt = f"""You are an expert on Indian government schemes.

📚 CONTEXT FROM DATABASE:
{context}

👤 USER QUESTION:
{query}

INSTRUCTIONS:
1. Use the context above to answer the user's question accurately
2. Reference specific scheme details from the context
3. If asked about a scheme in the context, provide all details
4. Be helpful and include eligibility criteria
5. Mention benefits clearly

ANSWER:
"""
    
    return prompt


def retrieve_user_context(user_id: int, db: Session) -> str:
    """
    Retrieve user's previous eligibility checks
    Useful for personalized recommendations
    """
    
    from models import UserResponse
    
    # Get latest user response
    user_response = db.query(UserResponse).filter(
        UserResponse.user_id == user_id
    ).order_by(UserResponse.created_at.desc()).first()
    
    if not user_response:
        return ""
    
    context = f"""📊 USER PROFILE (from previous check):
- Age: {user_response.age}
- Gender: {user_response.gender}
- Occupation: {user_response.occupation}
- Income: ₹{user_response.income:,}
- State: {user_response.state}

"""
    
    return context


def get_full_rag_context(query: str, user_id: int, db: Session) -> tuple:
    """
    Get complete RAG context: schemes + user profile
    
    Returns: (augmented_prompt, retrieved_schemes_count)
    """
    
    # Retrieve schemes matching query
    schemes_context = retrieve_schemes_context(query, db)
    
    # Retrieve user profile
    user_context = retrieve_user_context(user_id, db)
    
    # Combine contexts
    full_context = user_context + schemes_context
    
    # Generate prompt with context
    if "No specific schemes found" in schemes_context:
        # If no schemes found, just use generic context
        augmented_prompt = generate_rag_prompt(query, user_context)
    else:
        augmented_prompt = generate_rag_prompt(query, full_context)
    
    # Count how many schemes were retrieved
    retrieved_count = schemes_context.count("##") if "##" not in schemes_context else len(db.query(Scheme).filter(
        (Scheme.name.ilike(f"%{query}%")) |
        (Scheme.description.ilike(f"%{query}%")) |
        (Scheme.category.ilike(f"%{query}%"))
    ).all())
    
    return augmented_prompt, retrieved_count