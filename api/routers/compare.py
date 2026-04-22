from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import CompareRequest, CompareResponse
from services.compare_service import compare_pokemon

router = APIRouter(prefix="/api/compare", tags=["Compare"])


@router.post("/", response_model=CompareResponse)
def compare(request: CompareRequest, db: Session = Depends(get_db)):
    """Compare Pokemon"""
    if len(request.pokemon_ids) < 2:
        raise HTTPException(400, "At least 2 Pokemon are required")
    if len(request.pokemon_ids) > 6:
        raise HTTPException(400, "The maximum is 6 Pokemon")
    
    try:
        return compare_pokemon(db, request.pokemon_ids)
    except ValueError as e:
        raise HTTPException(400, str(e))