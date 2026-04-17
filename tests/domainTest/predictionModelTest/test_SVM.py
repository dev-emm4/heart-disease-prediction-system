import os
import sys

from src.domain import ErrorMsg
from src.domain.predictionModel import FeatureVector
from src.domain.predictionModel import PredictionResult
from src.domain.predictionModel import SVM

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class TestSVM:
    def test_makePrediction_givenListOfFeatureVector_returnsListOfPredictionResult(self):
        model = SVM()
        feature_vector = FeatureVector(50, 1, 0, 120, 200, 0, 1, 150, 0, 1.0, 1, 0, 3)
        feature_vectors = [feature_vector]

        result = model.makePrediction(feature_vectors)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], PredictionResult)

    def test_makePrediction_givenEmptyListOfFeatureVector_raisesException(self):
        model = SVM()
        feature_vectors = []

        try:
            model.makePrediction(feature_vectors)
            assert False, "Expected an exception to be raised"
        except TypeError as e:
            print(e)
            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value

    def test_makePrediction_givenListOfNonFeatureVector_raisesException(self):
        model = SVM()
        feature_vectors = ["not a feature vector"]

        try:
            model.makePrediction(feature_vectors)
            assert False, "Expected an exception to be raised"
        except TypeError as e:
            print(e)
            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value

    def test_makePrediction_givenNone_raisesException(self):
        model = SVM()

        try:
            model.makePrediction(None)
            assert False, "Expected an exception to be raised"
        except TypeError as e:
            print(e)
            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value
