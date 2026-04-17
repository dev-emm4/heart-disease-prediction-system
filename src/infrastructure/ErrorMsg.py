from enum import Enum


class ErrorMsg(Enum):
    InvalidNumberOfColumns = "Invalid number of columns"
    CsvIsOutOfIndex = "Column index out of range."
    InvalidFilePath = "Csv path is Invalid"
    InvalidDropColumnOption = "Invalid drop column option"
    InvalidTargetColumnOption = "Invalid target column option"
