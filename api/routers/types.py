from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Type, TypeEffectiveness
from schemas import TypeSchema

router = APIRouter(prefix="/api/types", tags=["Types"])


@router.get("/", response_model=list[TypeSchema])
def list_types(db: Session = Depends(get_db)):
    return db.query(Type).order_by(Type.name).all()


@router.get("/{type_id}/effectiveness")
def type_effectiveness(type_id: int, db: Session = Depends(get_db)):
    """Type effectiveness table"""
    attacking = (
        db.query(TypeEffectiveness)
        .filter(TypeEffectiveness.attacking_type_id == type_id)
        .all()
    )
    defending = (
        db.query(TypeEffectiveness)
        .filter(TypeEffectiveness.defending_type_id == type_id)
        .all()
    )
    
    return {
        "attacking": [
            {
                "type": db.query(Type).get(e.defending_type_id).name,
                "multiplier": e.multiplier,
            }
            for e in attacking
        ],
        "defending": [
            {
                "type": db.query(Type).get(e.attacking_type_id).name,
                "multiplier": e.multiplier,
            }
            for e in defending
        ],
    }