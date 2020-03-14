from __future__ import annotations

from pydantic import BaseModel, conint


class Positions(BaseModel):
    stock: str
    symbol: str
    quantity: conint(ge=0.0)
    avg_buy_price: conint(ge=0.0)
    avg_sell_price: conint(ge=0.0)


class BasicErrorModel(BaseModel):
    message: str
    code: conint(ge=100.0, le=600.0)


class ExtendedErrorModel(BasicErrorModel):
    rootCause: str


class AccountDetails(BaseModel):
    cash: int
    positions: Positions

