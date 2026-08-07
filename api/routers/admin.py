from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import require_tier
from database import get_db
from models import User
from schemas import UserOut

# Every route in this router requires the admin tier.
router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_tier("admin"))],
)


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()
