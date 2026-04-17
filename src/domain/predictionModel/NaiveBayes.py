import os
import uuid
from datetime import datetime
from typing import LiteralString

import onnxruntime as rt
from onnxruntime.capi.onnxruntime_pybind11_state import InferenceSession

from .FeatureVector import FeatureVector
from .PredictionModel import PredictionModel
from .PredictionResult import PredictionResult
from common.AssertionConcern import AssertionConcern
from common.ErrorMsg import ErrorMsg


class NaiveBayes(PredictionModel):
    def __init__(self):
        self._trainedNB: InferenceSession = rt.InferenceSession(self._getAddressOfModelFile())
        self._inputName = self._trainedNB.get_inputs()[0].name
        self._labelName = self._trainedNB.get_outputs()[0].name

    def _getAddressOfModelFile(self) -> (LiteralString | str | bytes):
        script_dir = os.path.dirname(__file__)
        return os.path.join(script_dir, "NaiveBayes.onnx")

    def makePrediction(self, featureVectors: list[FeatureVector]) -> list[PredictionResult]:
        AssertionConcern.assertListItemsIsOfType(featureVectors, FeatureVector, ErrorMsg.PredictionModelInvalidFeatureVector.value)
        AssertionConcern.asserFalse(len(featureVectors) == 0, ErrorMsg.PredictionModelInvalidFeatureVector.value)

        twoDimensionalArray: list[list[float]] = self._transformFeatureVectorListTo2dArray(featureVectors)
        resultsInIntegerFormat: list[float] = \
            self._trainedNB.run([self._labelName], {self._inputName: twoDimensionalArray})[0]
        resultsInBoolFormat: list[bool] = self._transformResultsFromIntegerToBoolFormat(resultsInIntegerFormat)

        return self._createPredictionResults(featureVectors, resultsInBoolFormat)

    def _transformFeatureVectorListTo2dArray(self, featureVectors: list[FeatureVector]) -> list[list[float]]:
        twoDimensionalArray: list[list[float]] = []
        for featureVector in featureVectors:
            twoDimensionalArray.append(featureVector.getOptimizedFeaturesForNaiveBayesAndDecisionTree())

        return twoDimensionalArray

    def _transformResultsFromIntegerToBoolFormat(self, resultsInIntegerFormat: list[float]) -> list[bool]:
        resultsInBoolFormat: list[bool] = []
        for result in resultsInIntegerFormat:
            if result > 0:
                resultsInBoolFormat.append(True)
            else:
                resultsInBoolFormat.append(False)

        return resultsInBoolFormat

    def _createPredictionResults(self, featureVectors: list[FeatureVector], resultsInBoolFormat: list[bool]):
        predictionResults: list[PredictionResult] = []

        for index in range(len(featureVectors)):
            predictionResults.append(PredictionResult(uuid.uuid4(), self.__class__.__name__, featureVectors[index],
                                                      resultsInBoolFormat[index],
                                                      datetime.now()))

        return predictionResults
