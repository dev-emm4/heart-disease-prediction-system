class AssertionConcern:
    @staticmethod
    def assertIsType(input_value, expected_type, error_message: str):
        if not isinstance(input_value, expected_type):
            raise TypeError(error_message)

        return input_value

    @staticmethod
    def assertIsNotNone(input_value, error_message: str):
        if input_value is None:
            raise TypeError(error_message)

        return input_value

    @staticmethod
    def assertListItemsIsOfType(inputValue, expectedType, errorMessage: str):
        if not isinstance(inputValue, list):
            raise TypeError(errorMessage)

        for element in inputValue:
            if not isinstance(element, expectedType):
                raise TypeError(errorMessage)

        return inputValue

    @staticmethod
    def assertItemIn(item, arr: list, errorMessage: str):
        if not isinstance(arr, list):
            raise TypeError(errorMessage)

        if item not in arr:
            raise TypeError(errorMessage)

    @staticmethod
    def assertItemInList(input_value, expected_values: list, error_message: str):
        if input_value not in expected_values:
            raise TypeError(error_message)

        return input_value

    @staticmethod
    def asserFalse(condition: bool, error_message: str):
        if condition:
            raise TypeError(error_message)

    @staticmethod
    def assertTrue(condition: bool, error_message: str):
        if not condition:
            raise TypeError(error_message)
