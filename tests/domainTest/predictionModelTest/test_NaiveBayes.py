import os
import sys

from common.ErrorMsg import ErrorMsg
from src.domain.predictionModel import FeatureVector
from src.domain.predictionModel import NaiveBayes
from src.domain.predictionModel import PredictionResult

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class TestNaiveBayes:
    def test_makePrediction_givenListOfFeatureVector_returnsListOfPredictionResult(self):
        model = NaiveBayes()
        feature_vector = FeatureVector(50, 1, 0, 120, 200, 0, 1, 150, 0, 1.0, 1, 0, 3)
        feature_vectors = [feature_vector]

        result = model.makePrediction(feature_vectors)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], PredictionResult)
        assert result[0].modelName() == "NaiveBayes"
        assert result[0].featureVector() == feature_vector

    def test_makePrediction_givenEmptyListOfFeatureVector_raisesException(self):
        model = NaiveBayes()
        feature_vectors = []

        try:
            model.makePrediction(feature_vectors)
            assert False, "Expected an exception to be raised"
        except TypeError as e:
            print(e)
            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value

    def test_makePrediction_givenListOfNonFeatureVector_raisesException(self):
        model = NaiveBayes()
        featureVectors = ["not a feature vector"]

        try:
            model.makePrediction(featureVectors)
            assert False, "Expected an exception to be raised"
        except TypeError as e:
            print(e)
            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value

    def test_makePrediction_givenNone_raisesException(self):
        model = NaiveBayes()

        try:
            model.makePrediction(None)
            assert False, "Expected an exception to be raised"
        except TypeError as e:
            print(e)
            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value
