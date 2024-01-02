from __future__ import annotations

from decimal import Decimal

from common.utils import is_seed, seed_to_decimal


def test_str_is_seed():
    assert is_seed("0")
    assert is_seed("00")
    assert is_seed("12")
    assert is_seed("12.34")
    assert is_seed(".12")
    assert is_seed(".1")
    assert is_seed("12.")
    assert is_seed("1:23.45")
    assert is_seed("123:45.67")


def test_str_is_not_seed():
    assert not is_seed(".")
    assert not is_seed("12.345")
    assert not is_seed("1:2.34")
    assert not is_seed("1:234.45")
    assert not is_seed("1:23.456")
    assert not is_seed("1:23.456")


def test_seed_to_decimal():
    assert seed_to_decimal("0") == Decimal(0)
    assert seed_to_decimal("00") == Decimal(0)
    assert seed_to_decimal("12") == Decimal(12)
    assert seed_to_decimal("12.34") == Decimal("12.34")
    assert seed_to_decimal(".12") == Decimal(".12")
    assert seed_to_decimal(".1") == Decimal(".1")
    assert seed_to_decimal("12.") == Decimal(12)
    assert seed_to_decimal("1:23.45") == Decimal("83.45")
    assert seed_to_decimal("123:45.67") == Decimal("7425.67")
