import os
import sys

from common.ErrorMsg import ErrorMsg
from src.domain.modelPerformanceCalculator import ModelPerformanceCalculator
from src.domain.modelPerformanceCalculator import PerformanceResult
from src.domain.predictionModel import FeatureVector
from src.domain.predictionModel import NaiveBayes

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class TestModelPerformanceCalculator:
    def test_calculatePerformance_withValidInput_shouldReturnPerformanceResult(self):
        modelPerformanceCalculator = ModelPerformanceCalculator()

        featureVectors: list[FeatureVector] = [
            FeatureVector(
                45, 1, 3, 130, 250, 0, 1, 150,
                1, 2, 2, 0, 3),
            FeatureVector(
                50, 0, 2, 120, 200, 1,
                0, 140, 0, 1.5, 1, 1, 2)
        ]

        originalResults: list[float] = [0, 1]

        performanceResult: PerformanceResult = modelPerformanceCalculator.calculatePerformance(NaiveBayes(),
                                                                                               featureVectors,
                                                                                               originalResults)

        assert isinstance(performanceResult, PerformanceResult)
        assert performanceResult.modelName() == "NaiveBayes"

    def test_calculatePerformance_withInvalidParameters_throwError(self):
        modelPerformanceCalculator: ModelPerformanceCalculator = ModelPerformanceCalculator()
        featureVectors: list[FeatureVector] = [
            FeatureVector(
                45, 1, 3, 130, 250, 0, 1, 150,
                1, 2, 2, 0, 3),
            FeatureVector(
                50, 0, 2, 120, 200, 1,
                0, 140, 0, 1.5, 1, 1, 2)
        ]
        target: list[float] = [0, 1]

        try:
            for i in range(4):
                if i == 0:
                    modelPerformanceCalculator.calculatePerformance("invalidModel", featureVectors, target)
                elif i == 1:
                    modelPerformanceCalculator.calculatePerformance(NaiveBayes(), "invalidFeatureVectors",
                                                                    target)
                elif i == 2:
                    modelPerformanceCalculator.calculatePerformance(NaiveBayes(), [],
                                                                    target)
                else:
                    modelPerformanceCalculator.calculatePerformance(NaiveBayes(), featureVectors,
                                                                    "invalidOriginalResults")

            assert False, "Expected an error to be thrown for invalid parameters"
        except Exception as e:
            assert str(e) in (ErrorMsg.ModelPerformanceCalculatorInvalidPredictionModel.value,
                              ErrorMsg.ModelPerformanceCalculatorTarget.value,
                              ErrorMsg.ModelPerformanceCalculatorFeatureVectors.value)

    def test_calculatePerformance_withNoneParameters_throwError(self):
        modelPerformanceCalculator: ModelPerformanceCalculator = ModelPerformanceCalculator()
        featureVectors: list[FeatureVector] = [
            FeatureVector(
                45, 1, 3, 130, 250, 0, 1, 150,
                1, 2, 2, 0, 3),
            FeatureVector(
                50, 0, 2, 120, 200, 1,
                0, 140, 0, 1.5, 1, 1, 2)
        ]
        target: list[float] = [0, 1]

        try:
            for i in range(3):
                if i == 0:
                    modelPerformanceCalculator.calculatePerformance(None, featureVectors, target)
                elif i == 1:
                    modelPerformanceCalculator.calculatePerformance(NaiveBayes(), None, target)
                else:
                    modelPerformanceCalculator.calculatePerformance(NaiveBayes(), featureVectors, None)
            assert False, "Expected an error to be thrown for None parameters"
        except Exception as e:
            assert str(e) in (ErrorMsg.ModelPerformanceCalculatorInvalidPredictionModel.value,
                              ErrorMsg.ModelPerformanceCalculatorTarget.value,
                              ErrorMsg.ModelPerformanceCalculatorFeatureVectors.value)

    def test_calculatePerformance_withEmptyFeatureVectors_throwError(self):
        modelPerformanceCalculator: ModelPerformanceCalculator = ModelPerformanceCalculator()
        target: list[float] = [0, 1]

        try:
            modelPerformanceCalculator.calculatePerformance(NaiveBayes(), [], target)
            assert False, "Expected an error to be thrown for empty feature vectors"
        except Exception as e:
            assert str(e) == ErrorMsg.ModelPerformanceCalculatorFeatureVectors.value
