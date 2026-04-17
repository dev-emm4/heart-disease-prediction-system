import os
import sys

from src.domain import ErrorMsg
from src.domain.modelPerformanceCalculator import PerformanceResult

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class TestPerformanceResult:
    def test_constructor_withValidInputs_shouldCreateInstance(self):
        result = PerformanceResult("NaiveBayes", 0.85, 0.90, 0.80)

        assert result.modelName() == "NaiveBayes"
        assert result.recall() == 0.85
        assert result.accuracy() == 0.90
        assert result.precision() == 0.80

    def test_constructor_withInvalidInputs_shouldRaiseError(self):
        for i in range(4):
            try:
                PerformanceResult(10 if i == 0 else "NaiveBayes", 0.85 if i == 1 else "0.85",
                                  0.90 if i == 2 else "0.90",
                                  0.80 if i == 3 else "0.80")

                assert False, "Expected an error for invalid model name"
            except Exception as e:
                assert str(e) in (ErrorMsg.PerformanceResultInvalidModelName.value,
                                  ErrorMsg.PerformanceResultInvalidRecall.value,
                                  ErrorMsg.PerformanceResultInvalidAccuracy.value,
                                  ErrorMsg.PerformanceResultInvalidPrecision.value)

    def test_strAndRpr_withValidInstance_shouldReturnFormattedString(self):
        result = PerformanceResult("NaiveBayes", 0.85, 0.90, 0.80)
        expected_str = "Model: NaiveBayes, Recall: 0.8500, Accuracy: 0.9000, Precision: 0.8000"

        assert str(result) == expected_str
        assert repr(result) == expected_str

    def test_json_withValidInstance_shouldReturnJsonRepresentation(self):
        result = PerformanceResult("NaiveBayes", 0.85, 0.90, 0.80)
        expected_json = {
            "modelName": "NaiveBayes",
            "recall": 0.85,
            "accuracy": 0.90,
            "precision": 0.80
        }

        assert result.__json__() == expected_json
