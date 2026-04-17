from enum import Enum


class Status(Enum):
    success = "success",
    notFound = "not found",
    valueError = "value error"
    internalError =  "internal error"