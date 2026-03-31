from sqlalchemy.orm import Session
from models import Scheme

def calculate_match_score(user_data: dict, scheme: Scheme) -> int:
    """
    Calculate eligibility score for a user against a scheme
    Returns score out of 100
    """
    score = 0
    
    # Check income eligibility
    if user_data.get("income"):
        income = user_data["income"]
        
        # Lower income = higher priority for most schemes
        if income < 200000:
            score += 40
        elif income < 500000:
            score += 20
    
    # Check age eligibility
    if user_data.get("age"):
        age = user_data["age"]
        
        if 18 <= age <= 35:
            score += 20
        elif 35 < age <= 65:
            score += 10
    
    # Check state eligibility
    if user_data.get("state"):
        state = user_data["state"].lower()
        scheme_eligibility = scheme.eligibility.lower()
        
        if state in scheme_eligibility or "all" in scheme_eligibility:
            score += 15
    
    # Check occupation eligibility
    if user_data.get("occupation"):
        occupation = user_data["occupation"].lower()
        scheme_eligibility = scheme.eligibility.lower()
        
        if occupation in scheme_eligibility:
            score += 25
    
    # Check gender eligibility
    if user_data.get("gender"):
        gender = user_data["gender"].lower()
        scheme_eligibility = scheme.eligibility.lower()
        
        if gender in scheme_eligibility or "all" in scheme_eligibility:
            score += 10
    
    return min(score, 100)  # Cap at 100


def find_matching_schemes(user_data: dict, db: Session, limit: int = 5):
    """
    Find top matching schemes for a user
    """
    schemes = db.query(Scheme).all()
    
    # Calculate scores for each scheme
    scheme_scores = []
    for scheme in schemes:
        score = calculate_match_score(user_data, scheme)
        scheme_scores.append({
            "scheme": scheme,
            "score": score,
            "percentage": f"{score}%"
        })
    
    # Sort by score (highest first)
    scheme_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top N schemes
    return scheme_scores[:limit]