from enum import Enum


class Status(Enum):
    success = "success",
    valueError = "value error"
    internalError =  "internal error"