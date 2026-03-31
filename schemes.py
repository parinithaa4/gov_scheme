from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Scheme

router = APIRouter()

class SchemeRequest(BaseModel):
    name: str
    description: str
    category: str
    eligibility: str
    state: str
    benefits: str

class SchemeResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    eligibility: str
    state: str
    benefits: str

    class Config:
        from_attributes = True

@router.post("/")
def create_scheme(scheme: SchemeRequest, db: Session = Depends(get_db)):
    """Create a new scheme (Admin only)"""
    db_scheme = Scheme(**scheme.dict())
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)
    return {
        "message": "Scheme created successfully",
        "scheme": db_scheme
    }

@router.get("/")
def get_all_schemes(
    category: str = Query(None, description="Filter by category"),
    state: str = Query(None, description="Filter by state"),
    db: Session = Depends(get_db)
):
    """Get all schemes with optional filters"""
    query = db.query(Scheme)
    
    # Filter by category
    if category:
        query = query.filter(Scheme.category.ilike(f"%{category}%"))
    
    # Filter by state
    if state:
        query = query.filter(
            (Scheme.state.ilike(f"%{state}%")) | 
            (Scheme.state.ilike("%all%"))
        )
    
    schemes = query.all()
    
    return {
        "count": len(schemes),
        "filters": {
            "category": category,
            "state": state
        },
        "schemes": schemes
    }

@router.get("/{scheme_id}")
def get_scheme(scheme_id: int, db: Session = Depends(get_db)):
    """Get a specific scheme by ID"""
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@router.put("/{scheme_id}")
def update_scheme(scheme_id: int, scheme: SchemeRequest, db: Session = Depends(get_db)):
    """Update a scheme"""
    db_scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not db_scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    for key, value in scheme.dict().items():
        setattr(db_scheme, key, value)
    
    db.commit()
    db.refresh(db_scheme)
    return {
        "message": "Scheme updated successfully",
        "scheme": db_scheme
    }

@router.delete("/{scheme_id}")
def delete_scheme(scheme_id: int, db: Session = Depends(get_db)):
    """Delete a scheme"""
    db_scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not db_scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    db.delete(db_scheme)
    db.commit()
    return {"message": "Scheme deleted successfully"}