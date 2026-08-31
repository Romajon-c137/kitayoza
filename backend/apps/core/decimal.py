from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANT = Decimal("0.01")
QTY_QUANT = Decimal("0.001")


def money(value: Decimal | str | int) -> Decimal:
    return Decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def quantity(value: Decimal | str | int) -> Decimal:
    return Decimal(value).quantize(QTY_QUANT, rounding=ROUND_HALF_UP)


def divide_money(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == 0:
        return money("0")
    return money(numerator / denominator)
