
"""billing package – public façade over billing.calculator"""
from importlib import metadata as _metadata
from .calculator import (
    price_with_tax, apply_coupon, compute_total, compute_subtotal,
    booking_fee, convert_currency, loyalty_points_earned, compute_bulk_total, split_payment,
    validate_coupon, parse_iso_date,compute_refund, bulk_discount, compute_bulk_total, 
    tax_breakdown, validate_tax_number, apply_dynamic_tax, loyalty_points_earned, apply_loyalty_discount,
    cap_price, round_money, is_weekend_rate
)

__all__ = [
    "price_with_tax", "apply_coupon", "compute_total", "compute_subtotal",
    "booking_fee", "convert_currency", "loyalty_points_earned",
    "compute_bulk_total", "split_payment", "validate_coupon", "parse_iso_date", "compute_refund"
    "bulk_discount", "compute_bulk_total", "tax_breakdown", "validate_tax_number", "apply_dynamic_tax",
    "loyalty_points_earned", "apply_loyalty_discount", "cap_price", "round_money", "is_weekend_rate"
]
try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError:
    __version__ = "0.1.0"
