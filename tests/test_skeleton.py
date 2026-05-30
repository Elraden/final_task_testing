"""
Starter tests for Mutation Shootout.
"""
import pytest
from billing import (
    price_with_tax, apply_coupon, compute_total, booking_fee,
    compute_subtotal, convert_currency, split_payment, validate_coupon, parse_iso_date,
    compute_refund, bulk_discount, compute_bulk_total, tax_breakdown, validate_tax_number,
    apply_dynamic_tax, loyalty_points_earned, apply_loyalty_discount, cap_price, round_money,
    is_weekend_rate
)
from datetime import datetime, date
from billing.calculator import COUPON_CODES


class TestCouponCodes:
    def test_coupon_codes_are_configured(self):
        assert COUPON_CODES == {
            "SPORT10": 0.10,
            "NEWUSER5": 0.05,
            "BLACKFRIDAY": 0.25,
        }


class TestPriceWithTax:
    def test_positive_value(self):
        tax = 100
        expected = 121
        assert price_with_tax(tax) == expected


    def test_zero_returns_zero(self):
        tax = 0
        assert price_with_tax(tax) == tax

    @pytest.mark.parametrize("negative", [-1.0, -100])
    def test_negative_raises(self, negative):
        with pytest.raises(ValueError) as e:
            price_with_tax(negative)
        assert e.value.args == ("net must be non‑negative",)


class TestApplyCoupon:
    def test_valid_coupon(self):
        gross = 100
        expected = 90
        assert apply_coupon(gross, "SPORT10") == expected


    def test_invalid_coupon(self):
        gross = 100
        assert apply_coupon(gross, "TestCoupon") == gross

class TestComputeSubtotal:
    @pytest.mark.parametrize("price, qty, eepted", 
        [
            (150.3, 10, 1503.0),
            (211.7, 13, 2752.1),
            (55.3, 7, 387.1),
            (21.3, 1, 21.3),
        ])
    def test_positive_qty(self, price, qty, eepted):
        assert compute_subtotal(price, qty) == eepted

    @pytest.mark.parametrize("price, qty", 
        [
            (150.3, 0),
            (211.7, -10),
            (55.3, -3) 
        ])
    def test_negative_or_zero_qty_raises(self, price, qty):
        with pytest.raises(ValueError) as e:
            compute_subtotal(price, qty)
        assert e.value.args == ("qty must be positive",)
        

class TestValidateCoupon:
    @pytest.mark.parametrize("coupon", ["SPORT10", "NEWUSER5", "BLACKFRIDAY"])
    def test_valid_coupon_returns_true(self, coupon):
        assert validate_coupon(coupon) is True

    @pytest.mark.parametrize("coupon", ["sport10", "Sport10", "SPORT10"])
    def test_valid_coupon_case(self, coupon):
        assert validate_coupon(coupon) is True

    def test_invalid_coupon_returns_false(self):
        coupon = "Test Coupon"
        assert validate_coupon(coupon) is False


class TestSplitPayment:
    @pytest.mark.parametrize("total, parts, expected",
    [
        (100, 2, [50, 50]),
        (90, 3, [30, 30, 30]),
        (10, 4, [2.5, 2.5, 2.5, 2.5]),
        (50, 1, [50.0]),
        (10, 6, [1.67, 1.67, 1.67, 1.67, 1.67, 1.65])
    ])
    def test_split_into_parts(self, total, parts, expected):
        assert split_payment(total, parts) == expected


    def test_split_with_correct_rounding(self):
        total = 100
        parts = 3
        expected = [33.33, 33.33, 33.34]
        assert split_payment(total, parts) == expected

    @pytest.mark.parametrize("parts", [0, -1, -10])
    def test_invalid_parts_raises(self, parts):
        total = 100
        with pytest.raises(ValueError) as e:
            split_payment(total, parts)
        assert e.value.args == ("parts must be > 0",)

class TestConvertCurrency:

    @pytest.mark.parametrize(
        "amount_eur, currency, expected",
        [
            (100, "EUR", 100.00),
            (100, "USD", 108.70),
            (100, "GBP", 86.96)
        ]
    )
    def test_convert_correct_currency(self, amount_eur, currency, expected):
        assert convert_currency(amount_eur, currency) == expected

    @pytest.mark.parametrize("currency", ["usd", "UsD", "USD"])
    def test_currency_case(self, currency):
        amount = 100
        assert convert_currency(amount, currency) == 108.70

    @pytest.mark.parametrize("uns_currency", ["RUB", "ABC", "CDE"])
    def test_unsupported_currency_raises(self, uns_currency):
        amount = 100
        with pytest.raises(KeyError) as e:
            convert_currency(amount, uns_currency)
        assert e.value.args == (f"Unsupported currency {uns_currency}",)


class TestParseIsoDate:
    def test_parse_correct_iso_date(self):
        date_str = "2026-05-30"
        expected = datetime(2026, 5, 30, 0, 0)
        assert parse_iso_date(date_str) == expected

    def test_parse_valid_iso_datetime(self):
        date_str = "2026-05-30T12:30:00"
        expected = datetime(2026, 5, 30, 12, 30, 0)
        assert parse_iso_date(date_str) == expected

    @pytest.mark.parametrize("invalid_str", ["abcde", "123456", "3000-50-50"])
    def test_invalid_date_raises(self, invalid_str):
        with pytest.raises(ValueError):
            parse_iso_date(invalid_str)


class TestComputeRefund:
    @pytest.mark.parametrize("percentage, expected", 
        [
            (0, 0.0),
            (0.5, 103.0),
            (1, 206.0)
        ]
    )
    def test_valid_percentage(self, percentage, expected):
        total_paid = 206
        assert compute_refund(total_paid, percentage) == expected
    
    @pytest.mark.parametrize("percentage", [-0.1, 1.1, 2])
    def test_invalid_percentage(self, percentage):
        total_paid = 206
        with pytest.raises(ValueError) as e:
            compute_refund(total_paid, percentage)
        assert e.value.args == ("percentage 0..1",)


class TestBuldDiscount:
    @pytest.mark.parametrize("qty, expected", [
        (8, 0.0),
        (10, 0.08),
        (19, 0.08),
        (20, 0.15)
    ])
    def test_invalid_percentage_raises(self, qty, expected):
        assert bulk_discount(qty) == expected

class TestComputeBulkTotal:
    
    def test_total_without_bulk_discount(self):
        qty = 9
        unit_price = 20
        assert compute_bulk_total(unit_price, qty) == 217.8

    def test_total_with_10_items(self):
        qty = 10
        unit_price = 20
        assert compute_bulk_total(unit_price, qty) == 222.64

    def test_total_with_20_items_discount(self):
        qty = 20
        unit_price = 20
        assert compute_bulk_total(unit_price, qty) == 411.4 

class TestTaxBreakdown:

    @pytest.mark.parametrize("net, exp_tax", [
        (10, (10, 2.1)),
        (0, (0, 0.0))
    ])
    def test_tax_breakdown_success(self, net, exp_tax):
        assert tax_breakdown(net) == exp_tax

class TestValidateTaxNumber:

    def test_valid_tax_number(self):
        tax_num = "LV0567890123"
        assert validate_tax_number(tax_num) is True

    @pytest.mark.parametrize('invalid_tax', ["23434", "LV123131", "LHGF12345678"])
    def test_invalid_tax_number(self, invalid_tax):
        assert validate_tax_number(invalid_tax) is False

class TestApplyDynamicTax:
    @pytest.mark.parametrize("country", ["LV", "lv", "Lv"])
    def test_lv_tax_rate(self, country):
        net = 100
        assert apply_dynamic_tax(net, country) == 121.00

    @pytest.mark.parametrize("country", ["NP", "RU", "EE"])
    def test_other_country_tax_rate(self, country):
        net = 100
        assert apply_dynamic_tax(net, country) == 120.00


class TestLoyaltyPointsEarned:
    @pytest.mark.parametrize("net, expected", [
        (250.6, 5), 
        (104.1, 2),
        (20.3, 0)
    ])
    def test_points_earned(self, net, expected):
        assert loyalty_points_earned(net) == expected


    def test_zero_net_returns_zero(self):
        net = 0.0
        assert loyalty_points_earned(net) == 0


class TestApplyLoyaltyDiscount:

    @pytest.mark.parametrize("gross, points, expected", [
        (105.1, 10, 105.0),
        (35.7, 7, 35.63),
        (234.7, 11, 234.59)
    ])
    def test_apply_points_discount(self, gross, points, expected):
        assert apply_loyalty_discount(gross, points) == expected  

    def test_zero_points_does_not_change_gross(self):
        gross = 100.5
        points = 0
        assert apply_loyalty_discount(gross, points) == gross 


    def test_discount_cannot_make_negative_total(self):
        gross = 1.00
        points = 500
        assert apply_loyalty_discount(gross, points) >= 0


class TestCapPrice:
    @pytest.mark.parametrize("price, cap, expected", [
        (10.5, 7.6, 7.6),
        (105.6, 105.6, 105.6),
        (71.7, 114.3, 71.7),
    ])
    def test_cap_price(self, price, cap, expected):
        assert cap_price(price, cap) == expected

class TestRoundMoney:
    @pytest.mark.parametrize("value, expected", [
        (101.453535345, 101.45),
        (1.456, 1.46),
        (10.4, 10.40),
    ])
    def test_round_by_default(self, value, expected):
        assert round_money(value) == expected
    
    @pytest.mark.parametrize("value, expected", [
        (101.005, 101.01),
        (1.456, 1.46),
        (10.085, 10.09),
    ])
    def test_round_half_up(self, value, expected):
        assert round_money(value) == expected  


    @pytest.mark.parametrize("decimal, expected", [
        (4, 100.1235),
        (1, 100.1),
        (3, 100.123),
    ])
    def test_round_to_other_decimals(self, decimal, expected):
        value = 100.123456789
        assert round_money(value, decimal) == expected

class TestIsWeekendRate:
    @pytest.mark.parametrize("date, expected", 
    [
        (date(2026, 5, 30), True),
        (date(2026, 5, 25), False),
        (date(2026, 5, 31), True),
    ])
    def test_weekend_rate(self, date, expected):
        assert is_weekend_rate(date) == expected


class TestPipeline:
    def test_happy_flow_eur(self):
        unit_price = 10
        qty = 2
        coupon = None
        assert compute_total(unit_price, qty, coupon) == 25.41

    def test_happy_flow_with_coupon(self):
        unit_price = 10
        qty = 2
        coupon = "SPORT10"
        assert compute_total(unit_price, qty, coupon) == 22.87
