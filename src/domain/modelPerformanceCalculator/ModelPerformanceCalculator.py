import math

from sklearn.metrics import precision_score, recall_score, accuracy_score

from common.AssertionConcern import AssertionConcern
from common.ErrorMsg import ErrorMsg
from .PerformanceResult import PerformanceResult
from ..predictionModel import FeatureVector
from ..predictionModel import PredictionModel
from ..predictionModel import PredictionResult


class ModelPerformanceCalculator:
    def calculatePerformance(self, predictionModel: PredictionModel, featureVectors: list[FeatureVector],
                             target: list[float]):
        AssertionConcern.assertIsType(predictionModel, PredictionModel,
                                      ErrorMsg.ModelPerformanceCalculatorInvalidPredictionModel.value)
        AssertionConcern.assertListItemsIsOfType(featureVectors, FeatureVector,
                                                 ErrorMsg.ModelPerformanceCalculatorFeatureVectors.value)
        AssertionConcern.assertTrue((len(featureVectors) > 0), ErrorMsg.ModelPerformanceCalculatorFeatureVectors.value)
        AssertionConcern.assertListItemsIsOfType(target, (float, int), ErrorMsg.ModelPerformanceCalculatorTarget.value)

        predictionResults: list[PredictionResult] = predictionModel.makePrediction(featureVectors)
        predictionResultInFloatFormat: list[float] = self._transformPredictionResultToFloatFormat(predictionResults)

        accuracy = accuracy_score(target, predictionResultInFloatFormat)
        accuracy = math.trunc(accuracy * 100)

        precision = precision_score(target, predictionResultInFloatFormat, average='weighted')
        precision = math.trunc(precision * 100)

        recall = recall_score(target, predictionResultInFloatFormat, average='weighted')
        recall = math.trunc(recall * 100)

        return PerformanceResult(predictionModel.__class__.__name__, recall, accuracy, precision)

    def _transformPredictionResultToFloatFormat(self, predictionResults: list[PredictionResult]) -> list[float]:
        predictionResultInFloatFormat: list[float] = []

        for predictionResult in predictionResults:
            if predictionResult.isMalignant():
                predictionResultInFloatFormat.append(1)
            else:
                predictionResultInFloatFormat.append(0)

        return predictionResultInFloatFormat
