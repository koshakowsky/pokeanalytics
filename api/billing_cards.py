"""Fake payment gateway logic: card validation and charge simulation.

No DB or FastAPI here, just functions over card data, so the validation core
can be unit-tested on its own. Test card numbers follow the Stripe style: all
are Luhn-valid, so a decline is a gateway decision rather than a format error.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class CardError(Exception):
    """Bad card format/data, maps to HTTP 422."""
    error_code: str
    message: str


@dataclass
class PaymentError(Exception):
    """Valid card, gateway declined the charge, maps to HTTP 402."""
    error_code: str
    message: str


# Luhn-valid numbers the gateway always declines.
DECLINE_CARDS = {
    "4000000000000002": ("card_declined", "Your card was declined."),
    "4000000000009995": ("insufficient_funds", "Your card has insufficient funds."),
}


def normalize_number(number: str) -> str:
    return number.replace(" ", "").replace("-", "")


def luhn_valid(number: str) -> bool:
    if not number.isdigit():
        return False
    total = 0
    for i, ch in enumerate(reversed(number)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def detect_brand(number: str) -> str:
    if number.startswith("4"):
        return "visa"
    if number[:2] in {"34", "37"}:
        return "amex"
    if number[:2] in {str(p) for p in range(51, 56)}:
        return "mastercard"
    if number[:4].isdigit() and 2221 <= int(number[:4]) <= 2720:
        return "mastercard"
    return "unknown"


def expected_cvc_length(brand: str) -> int:
    return 4 if brand == "amex" else 3


def _now() -> datetime:
    return datetime.now(timezone.utc)


def validate_card(number: str, exp_month: int, exp_year: int, cvc: str) -> str:
    """Validate card format/data. Returns the brand or raises CardError.

    Check order is fixed: tests rely on a specific error_code per bad input.
    """
    num = normalize_number(number)

    if not num.isdigit() or not (13 <= len(num) <= 19):
        raise CardError("invalid_number", "Card number must be 13–19 digits.")
    if not luhn_valid(num):
        raise CardError("invalid_number", "Card number failed the Luhn check.")

    brand = detect_brand(num)

    if not (1 <= exp_month <= 12):
        raise CardError("invalid_expiry", "Expiry month must be between 1 and 12.")

    now = _now()
    if (exp_year, exp_month) < (now.year, now.month):
        raise CardError("card_expired", "The card has expired.")

    if not cvc.isdigit() or len(cvc) != expected_cvc_length(brand):
        raise CardError(
            "invalid_cvc",
            f"CVC must be {expected_cvc_length(brand)} digits for {brand}.",
        )

    return brand


def charge(number: str) -> None:
    num = normalize_number(number)
    if num in DECLINE_CARDS:
        code, message = DECLINE_CARDS[num]
        raise PaymentError(code, message)
