import os
import sys
from datetime import datetime
from uuid import uuid4

from src.domain import ErrorMsg
from src.domain.predictionModel import FeatureVector
from src.domain.predictionModel import PredictionResult

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class TestPredictionResult:
    def test_constructor_withValidParameters_createsPredictionResult(self):
        Id = uuid4()
        modelName = "NaiveBayes"
        featureVector = FeatureVector(50, 1, 0, 120, 200, 0, 1,
                                      150, 0, 1.0, 1, 0, 3)
        isMalignant = True
        timeStamp = datetime.now()

        prediction_result = PredictionResult(Id, modelName, featureVector, isMalignant, timeStamp)

        assert prediction_result.id() == Id
        assert prediction_result.modelName() == modelName
        assert prediction_result.featureVector() == featureVector
        assert prediction_result.isMalignant() == isMalignant
        assert prediction_result.timeStamp() == timeStamp

    def test_constructor_withInvalidParameters_raisesException(self):
        Id = uuid4()
        modelName = "NaiveBayes"
        featureVector = FeatureVector(50, 1, 0, 120, 200, 0, 1,
                                      150, 0, 1.0, 1, 0, 3)
        isMalignant = True
        timeStamp = datetime.now()

        for i in range(11):
            try:
                if i == 0:
                    PredictionResult("invalid_id", modelName, featureVector, isMalignant, timeStamp)
                elif i == 1:
                    PredictionResult(Id, 123, featureVector, isMalignant, timeStamp)
                elif i == 2:
                    PredictionResult(Id, modelName, "invalid_feature_vector", isMalignant, timeStamp)
                elif i == 3:
                    PredictionResult(Id, modelName, featureVector, "invalid_is_malignant", timeStamp)
                elif i == 4:
                    PredictionResult(Id, modelName, featureVector, isMalignant, "invalid_time_stamp")
                if i == 5:
                    PredictionResult(None, modelName, featureVector, isMalignant, timeStamp)
                elif i == 6:
                    PredictionResult(Id, None, featureVector, isMalignant, timeStamp)
                elif i == 7:
                    PredictionResult(Id, modelName, None, isMalignant, timeStamp)
                elif i == 8:
                    PredictionResult(Id, modelName, featureVector, None, timeStamp)
                elif i == 9:
                    PredictionResult(Id, modelName, featureVector, isMalignant, None)
                elif i == 10:
                    PredictionResult(Id, modelName, [], isMalignant, timeStamp)
                else:
                    PredictionResult(Id, "invalidModelName", featureVector, isMalignant, timeStamp)

                assert False, "Expected an exception to be raised"
            except TypeError as e:
                assert str(e) in (ErrorMsg.PredictionResultInvalidId.value,
                                  ErrorMsg.PredictionResultInvalidModelName.value,
                                  ErrorMsg.PredictionResultInvalidFeatureVector.value,
                                  ErrorMsg.PredictionResultInvalidDiag.value,
                                  ErrorMsg.PredictionResultInvalidTimeStamp.value)

    def test_strAndRepr_returnsStringRepresentation(self):
        Id = uuid4()
        modelName = "NaiveBayes"
        featureVector = FeatureVector(50, 1, 0, 120, 200, 0, 1,
                                      150, 0, 1.0, 1, 0, 3)
        isMalignant = True
        timeStamp = datetime.now()

        prediction_result = PredictionResult(Id, modelName, featureVector, isMalignant, timeStamp)

        expected_str = f"PredictionResult(Id: {Id}, Model: {modelName}, FeatureVector: {featureVector}, IsMalignant: {isMalignant}, TimeStamp: {timeStamp})"
        assert str(prediction_result) == expected_str
        assert repr(prediction_result) == expected_str

    def test_json_returnsJsonRepresentation(self):
        Id = uuid4()
        modelName = "NaiveBayes"
        featureVector = FeatureVector(50, 1, 0, 120, 200, 0, 1,
                                      150, 0, 1.0, 1, 0, 3)
        isMalignant = True
        timeStamp = datetime.now()

        prediction_result = PredictionResult(Id, modelName, featureVector, isMalignant, timeStamp)

        expected_json = {
            "Id": str(Id),
            "modelName": modelName,
            "featureVector": featureVector.__json__(),
            "isMalignant": isMalignant,
            "timeStamp": timeStamp.isoformat()
        }
        assert prediction_result.__json__() == expected_json
