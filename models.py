from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, conint


class Status(Enum):
    error = "error"


class ErrorResponse(BaseModel):
    status: Status
    errmsg: str


class Status_1(Enum):
    ok = "ok"


class SuccessResponse(BaseModel):
    status: Status_1


class Status_2(Enum):
    ok = "ok"


class TestListResponse(BaseModel):
    status: Status_2


class Status_3(Enum):
    ok = "ok"


class TestResponse(BaseModel):
    status: Status_3


class TestData(BaseModel):
    key_1: str
    key_2: str


class BasicErrorModel(BaseModel):
    message: str
    code: conint(ge=100.0, le=600.0)


class ExtendedErrorModel(BasicErrorModel):
    rootCause: str
