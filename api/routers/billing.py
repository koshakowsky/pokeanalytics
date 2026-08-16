import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import billing_cards
from auth import get_current_user
from database import get_db
from models import IdempotencyKey, Subscription, User
from schemas import CheckoutRequest, PlanOut, SubscriptionOut

router = APIRouter(prefix="/api/billing", tags=["Billing"])

PLANS = {
    "premium": {
        "id": "premium",
        "name": "Premium",
        "price_cents": 999,
        "currency": "eur",
        "interval": "month",
    },
}

PERIOD_DAYS = 30


def _sub_out(sub: Subscription) -> SubscriptionOut:
    return SubscriptionOut.model_validate(sub)


@router.get("/plans", response_model=list[PlanOut])
def list_plans():
    return list(PLANS.values())


@router.get("/subscription", response_model=SubscriptionOut)
def get_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub is None:
        return SubscriptionOut(status="none")
    return _sub_out(sub)


@router.post("/checkout", response_model=SubscriptionOut)
def checkout(
    body: CheckoutRequest,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.idempotency_key:
        cached = db.get(IdempotencyKey, {"user_id": user.id, "key": body.idempotency_key})
        if cached is not None:
            response.status_code = cached.status_code
            return json.loads(cached.response_json)

    plan = PLANS.get(body.plan_id)
    if plan is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            {"error_code": "unknown_plan", "message": "Unknown plan."},
        )

    existing = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if existing is not None and existing.status == "active":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            {"error_code": "already_subscribed", "message": "Subscription is already active."},
        )

    card = body.card
    try:
        brand = billing_cards.validate_card(card.number, card.exp_month, card.exp_year, card.cvc)
        billing_cards.charge(card.number)
    except billing_cards.CardError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            {"error_code": e.error_code, "message": e.message})
    except billing_cards.PaymentError as e:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED,
                            {"error_code": e.error_code, "message": e.message})

    last4 = billing_cards.normalize_number(card.number)[-4:]
    period_end = datetime.now(timezone.utc) + timedelta(days=PERIOD_DAYS)
    if existing is None:
        sub = Subscription(user_id=user.id)
        db.add(sub)
    else:
        sub = existing                      # reactivate subscription
    sub.plan = plan["id"]
    sub.status = "active"
    sub.card_brand = brand
    sub.card_last4 = last4
    sub.current_period_end = period_end

    user.tier = "premium"
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        winner = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if winner is None:
            raise
        return _sub_out(winner)
    db.refresh(sub)

    out = _sub_out(sub)

    if body.idempotency_key:
        db.add(IdempotencyKey(
            key=body.idempotency_key,
            user_id=user.id,
            status_code=status.HTTP_200_OK,
            response_json=json.dumps(jsonable_encoder(out)),
        ))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()

    return out


@router.post("/cancel", response_model=SubscriptionOut)
def cancel(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if sub is None or sub.status != "active":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            {"error_code": "no_active_subscription", "message": "No active subscription to cancel."},
        )
    sub.status = "canceled"
    user.tier = "free"
    db.commit()
    db.refresh(sub)
    return _sub_out(sub)
