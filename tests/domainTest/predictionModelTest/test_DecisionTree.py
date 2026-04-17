import os
import sys

from src.domain import ErrorMsg
from src.domain.predictionModel import DecisionTree
from src.domain.predictionModel import FeatureVector
from src.domain.predictionModel import PredictionResult


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class TestDecisionTree:
    def test_makePrediction_givenListOfFeatureVector_returnsListOfPredictionResult(self):
        model = DecisionTree()
        feature_vector: FeatureVector = FeatureVector(50, 1, 0, 120, 200, 0, 1,
                                                      150, 0, 1.0, 1, 0, 3)
        feature_vectors: list[FeatureVector] = [feature_vector]

        result = model.makePrediction(feature_vectors)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], PredictionResult)
        assert result[0].modelName() == "DecisionTree"
        assert result[0].featureVector() == feature_vector

    def test_makePrediction_givenEmptyListOfFeatureVector_raisesException(self):
        model = DecisionTree()
        feature_vectors = []

        try:
            model.makePrediction(feature_vectors)
            assert False, "Expected an exception to be raised"
        except TypeError as e:
            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value

    def test_makePrediction_givenListOfNonFeatureVector_raisesException(self):
        model = DecisionTree()
        featureVectors = ["not a feature vector"]

        try:
            model.makePrediction(featureVectors)
            assert False, "Expected an exception to be raised"
        except TypeError as e:

            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value

    def test_makePrediction_givenNone_raisesException(self):
        model = DecisionTree()

        try:
            model.makePrediction(None)
            assert False, "Expected an exception to be raised"
        except TypeError as e:
            assert str(e) == ErrorMsg.PredictionModelInvalidFeatureVector.value
