"""Unit tests for the fake gateway's card logic.

No app, no database, no HTTP - `billing_cards` is deliberately free of all
three, and these tests import it directly. That is the point of the split: the
arithmetic is settled here, cheaply and exhaustively, so the API-level cases
(TC-BILL-04/05/06 in the poketests catalog) are left to prove that the router
wires the rules to the right status codes rather than re-deriving them.
"""

from datetime import datetime, timezone

import pytest

import billing_cards as cards


def _future_year(offset: int = 2) -> int:
    return datetime.now(timezone.utc).year + offset


class TestNormalisation:
    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("4242424242424242", "4242424242424242"),
            ("4242 4242 4242 4242", "4242424242424242"),
            ("4242-4242-4242-4242", "4242424242424242"),
            ("4242 4242-4242 4242", "4242424242424242"),
        ],
    )
    def test_separators_are_stripped(self, raw, expected):
        assert cards.normalize_number(raw) == expected


class TestLuhn:
    @pytest.mark.parametrize(
        "number",
        ["4242424242424242", "378282246310005", "4000000000000002", "4222222222222"],
    )
    def test_accepts_valid_checksums(self, number):
        assert cards.luhn_valid(number)

    @pytest.mark.parametrize(
        "number, why",
        [
            ("4242424242424241", "last digit flipped"),
            ("4242424242424252", "transposed digits"),
            ("", "empty"),
            ("4242abcd42424242", "non-digits"),
        ],
    )
    def test_rejects_invalid(self, number, why):
        assert not cards.luhn_valid(number), why


class TestBrandDetection:
    @pytest.mark.parametrize(
        "number, brand",
        [
            ("4242424242424242", "visa"),
            ("378282246310005", "amex"),      # 37 prefix
            ("341111111111111", "amex"),      # 34 prefix
            ("5105105105105100", "mastercard"),
            ("2221000000000009", "mastercard"),  # 2-series, lower bound
            ("2720999999999996", "mastercard"),  # 2-series, upper bound
            ("2220000000000006", "unknown"),     # just below the 2-series
            ("6011111111111117", "unknown"),     # discover is not modelled
        ],
    )
    def test_prefix_maps_to_brand(self, number, brand):
        assert cards.detect_brand(number) == brand

    @pytest.mark.parametrize("brand, length", [("amex", 4), ("visa", 3), ("mastercard", 3), ("unknown", 3)])
    def test_cvc_length_follows_brand(self, brand, length):
        assert cards.expected_cvc_length(brand) == length


class TestValidateCard:
    """The same decision table the API cases assert, one layer down."""

    def test_accepts_a_good_card_and_returns_the_brand(self):
        assert cards.validate_card("4242 4242 4242 4242", 12, _future_year(), "123") == "visa"

    @pytest.mark.parametrize(
        "number, month, year, cvc, error_code",
        [
            ("424242424242", 12, _future_year(), "123", "invalid_number"),        # 12 digits
            ("4" * 20, 12, _future_year(), "123", "invalid_number"),              # 20 digits
            ("4242424242424241", 12, _future_year(), "123", "invalid_number"),    # Luhn
            ("4242424242424242", 0, _future_year(), "123", "invalid_expiry"),
            ("4242424242424242", 13, _future_year(), "123", "invalid_expiry"),
            ("4242424242424242", 12, 2000, "123", "card_expired"),
            ("4242424242424242", 12, _future_year(), "12", "invalid_cvc"),
            ("4242424242424242", 12, _future_year(), "1234", "invalid_cvc"),      # 4 is amex-only
            ("378282246310005", 12, _future_year(), "123", "invalid_cvc"),        # amex needs 4
            ("4242424242424242", 12, _future_year(), "12a", "invalid_cvc"),
        ],
    )
    def test_rejects_with_a_specific_code(self, number, month, year, cvc, error_code):
        with pytest.raises(cards.CardError) as exc:
            cards.validate_card(number, month, year, cvc)
        assert exc.value.error_code == error_code

    def test_number_is_checked_before_expiry(self):
        """Order matters: the API contract promises one reason per rejection, and
        the tests upstream assert a specific code for each bad input."""
        with pytest.raises(cards.CardError) as exc:
            cards.validate_card("4242424242424241", 99, 2000, "1")
        assert exc.value.error_code == "invalid_number"

    @pytest.mark.parametrize("length", [13, 16, 19])
    def test_accepts_the_full_documented_length_range(self, length):
        # Build a Luhn-valid number of exactly `length` digits.
        base = "4" + "0" * (length - 2)
        for check in range(10):
            candidate = base + str(check)
            if cards.luhn_valid(candidate):
                break
        assert cards.validate_card(candidate, 12, _future_year(), "123") == "visa"


class TestCharge:
    def test_a_normal_card_is_charged(self):
        assert cards.charge("4242424242424242") is None

    @pytest.mark.parametrize(
        "number, error_code",
        [("4000000000000002", "card_declined"), ("4000000000009995", "insufficient_funds")],
    )
    def test_test_cards_are_declined(self, number, error_code):
        with pytest.raises(cards.PaymentError) as exc:
            cards.charge(number)
        assert exc.value.error_code == error_code

    def test_decline_cards_are_luhn_valid(self):
        """Otherwise they would fail validation and never reach the charge step,
        so the 402 branch would be unreachable."""
        for number in cards.DECLINE_CARDS:
            assert cards.luhn_valid(number), number
