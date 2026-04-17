from enum import Enum


class ResponseMsg(Enum):
    InvalidValueProvided = "Input provided is invalid"
    UnexpectedErrorEncountered = "Unexpected error encountered"
    csvIsInvalid = "CSV or CSV location is invalid"
