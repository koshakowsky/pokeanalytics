from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, aliased
from database import get_db
from models import Type, TypeEffectiveness
from schemas import TypeSchema

router = APIRouter(prefix="/api/types", tags=["Types"])


@router.get("/", response_model=list[TypeSchema])
def list_types(db: Session = Depends(get_db)):
    return db.query(Type).order_by(Type.name).all()


@router.get("/{type_id}/effectiveness")
def type_effectiveness(type_id: int, db: Session = Depends(get_db)):
    """Type effectiveness table."""
    if db.get(Type, type_id) is None:
        raise HTTPException(status_code=404, detail="Type not found")

    DefType = aliased(Type)
    AtkType = aliased(Type)

    # Single query each, joining the related type name instead of N+1 lookups.
    attacking = (
        db.query(DefType.name.label("type"), TypeEffectiveness.multiplier)
        .join(DefType, TypeEffectiveness.defending_type_id == DefType.id)
        .filter(TypeEffectiveness.attacking_type_id == type_id)
        .all()
    )
    defending = (
        db.query(AtkType.name.label("type"), TypeEffectiveness.multiplier)
        .join(AtkType, TypeEffectiveness.attacking_type_id == AtkType.id)
        .filter(TypeEffectiveness.defending_type_id == type_id)
        .all()
    )

    return {
        "attacking": [{"type": r.type, "multiplier": r.multiplier} for r in attacking],
        "defending": [{"type": r.type, "multiplier": r.multiplier} for r in defending],
    }
