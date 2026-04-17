import os
import sys
from uuid import uuid4

import pytest

from src.domain.predictionModel import NaiveBayes, SVM, DecisionTree
from src.application import PredictionApplicationService
from src.controller import PredictionController, Status, ResponseMsg
from src.domain.predictionModel import FeatureVector, FeatureVectorAttributes
from src.infrastructure import DatabaseConnection, FeatureVectorLoader
from src.infrastructure.persistence import SQLitePredictionResultRepository

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))


@pytest.fixture
def CSVLocation():
    return "/home/emmanuel/Desktop/heart-disease-prediction-system/tests/infrastructureTest/heart.csv"


@pytest.fixture
def CSVLength():
    return 1025


@pytest.fixture
def in_memory_db():
    db = DatabaseConnection(db_path=":memory:")
    yield db
    db.close()


@pytest.fixture
def repository(in_memory_db):
    return SQLitePredictionResultRepository(in_memory_db)


@pytest.fixture
def service(repository):
    return PredictionApplicationService(repository)


@pytest.fixture
def controller(service):
    return PredictionController(service, FeatureVectorLoader())


@pytest.fixture
def sampleFeatureVector():
    return FeatureVector(
        age=63.0,
        sex=1.0,
        cp=1.0,
        trestbps=145.0,
        chol=233.0,
        fbs=1.0,
        restecg=2.0,
        thalach=150.0,
        exang=0.0,
        oldpeak=2.3,
        slope=0.0,
        ca=0.0,
        thal=1.0
    )


@pytest.fixture
def sampleFeatureJson():
    return {
        FeatureVectorAttributes.age.value: 50.0,
        FeatureVectorAttributes.sex.value: 0.0,
        FeatureVectorAttributes.cp.value: 2.0,
        FeatureVectorAttributes.trestbps.value: 120.0,
        FeatureVectorAttributes.chol.value: 200.0,
        FeatureVectorAttributes.fbs.value: 0.0,
        FeatureVectorAttributes.restecg.value: 1.0,
        FeatureVectorAttributes.thalach.value: 130.0,
        FeatureVectorAttributes.exang.value: 0.0,
        FeatureVectorAttributes.oldpeak.value: 1.0,
        FeatureVectorAttributes.slope.value: 1.0,
        FeatureVectorAttributes.ca.value: 0.0,
        FeatureVectorAttributes.thal.value: 2.0
    }


class TestPredictionController:
    def test_makePrediction_withValidParameters_shouldReturnPrediction(self, controller, sampleFeatureJson):
        response = controller.makePrediction(NaiveBayes.__name__, sampleFeatureJson)

        assert response["status"] == Status.success.value
        assert isinstance(response["message"], dict)
        assert response["message"].get("modelName") == NaiveBayes.__name__
        assert response["message"].get("featureVector") == sampleFeatureJson

    def test_makePrediction_withInvalidParameter_returnError(self, controller, sampleFeatureJson):
        for i in range(5):
            if i == 0:
                response = controller.makePrediction("InvalidModel", sampleFeatureJson)

            elif i == 1:
                response = controller.makePrediction(NaiveBayes.__name__, "sampleFeatureJson")

            elif i == 2:
                response = controller.makePrediction(None, sampleFeatureJson)

            elif i == 3:
                response = controller.makePrediction("NaiveBayes", None)

            else:
                response = controller.makePrediction(NaiveBayes.__name__, {})

            assert response["status"] == Status.valueError.value
            assert response["message"] == ResponseMsg.InvalidValueProvided.value

    def test_makePrediction_withFeatureJsonWithInvalidAttribute_shouldReturnInternalError(self, controller):
        featureJsonWithInvalidAge = {
            FeatureVectorAttributes.age.value: "age",
            FeatureVectorAttributes.sex.value: 0.0,
            FeatureVectorAttributes.cp.value: 2.0,
            FeatureVectorAttributes.trestbps.value: 120.0,
            FeatureVectorAttributes.chol.value: 200.0,
            FeatureVectorAttributes.fbs.value: 0.0,
            FeatureVectorAttributes.restecg.value: 1.0,
            FeatureVectorAttributes.thalach.value: 130.0,
            FeatureVectorAttributes.exang.value: 0.0,
            FeatureVectorAttributes.oldpeak.value: 1.0,
            FeatureVectorAttributes.slope.value: 1.0,
            FeatureVectorAttributes.ca.value: 0.0,
            FeatureVectorAttributes.thal.value: 2.0
        }
        response = controller.makePrediction(NaiveBayes.__name__, featureJsonWithInvalidAge)

        assert response["status"] == Status.valueError.value
        assert response["message"] == ResponseMsg.InvalidValueProvided.value

    def test_makePrediction_SVMFeaturesCombinedWithDifferentModel_returnError(self, controller):
        SVMFeature = {
            FeatureVectorAttributes.age.value: 50.0,
            FeatureVectorAttributes.cp.value: 2.0,
            FeatureVectorAttributes.trestbps.value: 120.0,
            FeatureVectorAttributes.chol.value: 200.0,
            FeatureVectorAttributes.restecg.value: 1.0,
            FeatureVectorAttributes.thalach.value: 130.0,
            FeatureVectorAttributes.exang.value: 0.0,
            FeatureVectorAttributes.oldpeak.value: 1.0,
            FeatureVectorAttributes.slope.value: 1.0,
            FeatureVectorAttributes.ca.value: 0.0,
            FeatureVectorAttributes.thal.value: 2.0
        }  # fbs and sex attribute is missing which signifies svm features parameter

        response = controller.makePrediction(NaiveBayes.__name__, SVMFeature)

        assert response["status"] == Status.valueError.value
        assert response["message"] == ResponseMsg.InvalidValueProvided.value

    def test_makePrediction_SVMFeaturesCombinedWithSVM_returnPrediction(self, controller):
        SVMFeature = {
            FeatureVectorAttributes.age.value: 50,
            FeatureVectorAttributes.cp.value: 2,
            FeatureVectorAttributes.trestbps.value: 120,
            FeatureVectorAttributes.chol.value: 200,
            FeatureVectorAttributes.restecg.value: 1,
            FeatureVectorAttributes.thalach.value: 130,
            FeatureVectorAttributes.exang.value: 0,
            FeatureVectorAttributes.oldpeak.value: 1,
            FeatureVectorAttributes.slope.value: 1,
            FeatureVectorAttributes.ca.value: 0,
            FeatureVectorAttributes.thal.value: 2
        }  # fbs and sex attribute is missing which signifies svm features parameter

        expectedMsg = {
            FeatureVectorAttributes.age.value: 50.0,
            FeatureVectorAttributes.sex.value: None,
            FeatureVectorAttributes.cp.value: 2.0,
            FeatureVectorAttributes.trestbps.value: 120.0,
            FeatureVectorAttributes.chol.value: 200.0,
            FeatureVectorAttributes.fbs.value: None,
            FeatureVectorAttributes.restecg.value: 1.0,
            FeatureVectorAttributes.thalach.value: 130.0,
            FeatureVectorAttributes.exang.value: 0.0,
            FeatureVectorAttributes.oldpeak.value: 1.0,
            FeatureVectorAttributes.slope.value: 1.0,
            FeatureVectorAttributes.ca.value: 0.0,
            FeatureVectorAttributes.thal.value: 2.0
        }

        response = controller.makePrediction(SVM.__name__, SVMFeature)

        assert response["status"] == Status.success.value
        assert isinstance(response["message"], dict)
        assert response["message"].get("modelName") == SVM.__name__
        assert response["message"].get("featureVector") == expectedMsg

    def test_makeBulkPredictions_withValidParameters_returnPredictions(self, controller, CSVLocation, CSVLength):
        response = controller.makeBulkPredictions(NaiveBayes.__name__, CSVLocation,
                                                  dropColumn=[13])  # dropping the target column

        assert response["status"] == "success"
        assert isinstance(response["message"], list)
        assert len(response["message"]) == CSVLength
        for prediction in response["message"]:
            assert isinstance(prediction, dict)
            assert prediction.get("modelName") == NaiveBayes.__name__

    def test_makeBulkPredictions_withInvalidParameters_returnError(self, controller, CSVLocation):
        for i in range(6):
            if i == 0:
                response = controller.makeBulkPredictions("InvalidModel", CSVLocation, dropColumn=[13])
            elif i == 1:
                response = controller.makeBulkPredictions(NaiveBayes.__name__, 1000, dropColumn=[13])
            elif i == 3:
                response = controller.makeBulkPredictions(NaiveBayes.__name__, CSVLocation, "13")
            elif i == 4:
                response = controller.makeBulkPredictions(None, CSVLocation, dropColumn=[13])
            elif i == 5:
                response = controller.makeBulkPredictions(NaiveBayes.__name__, None, dropColumn=[13])
            else:
                response = controller.makeBulkPredictions(NaiveBayes.__name__, CSVLocation, None)

            assert response["status"] == Status.valueError.value
            assert response["message"] == ResponseMsg.InvalidValueProvided.value

    def test_makeBulkPredictions_InvalidCsv_returnError(self, controller, CSVLocation):
        for i in range(4):
            if i == 0:
                response = controller.makeBulkPredictions(NaiveBayes.__name__, CSVLocation, dropColumn=[100]) # dropColumn exceed the maximum number of column in Csv
            elif i == 1:
                response = controller.makeBulkPredictions(NaiveBayes.__name__, CSVLocation, dropColumn=[1, 2, 3,
                                                                                                        4])  # will produce invalid feature of length 10
            elif i == 2:
                response = controller.makeBulkPredictions(NaiveBayes.__name__, "InvalidFilePath", dropColumn=[13])
            else:
                response = controller.makeBulkPredictions(NaiveBayes.__name__, CSVLocation,
                                                          [])  # will produce invalid feature of length 14

            assert response["status"] == Status.valueError.value
            assert response["message"] == ResponseMsg.csvIsInvalid.value

    def test_makeBulkPrediction_SVMFeaturesCombinedWithDifferentModel_returnError(self, controller,
                                                                                                CSVLocation):
        response = controller.makeBulkPredictions(NaiveBayes.__name__, CSVLocation,
                                                  dropColumn=[1, 5, 13])  # dropping sex and fbs and target

        assert response["status"] == Status.valueError.value
        assert response["message"] == ResponseMsg.csvIsInvalid.value

    def test_makeBulkPrediction_SVMFeaturesCombinedWithSVM_returnPredictions(self, controller, CSVLocation,
                                                                                   CSVLength):
        response = controller.makeBulkPredictions(SVM.__name__, CSVLocation,
                                                  dropColumn=[1, 5, 13])  # dropping sex and fbs and target

        assert response["status"] == Status.success.value
        assert isinstance(response["message"], list)
        assert len(response["message"]) == CSVLength
        for prediction in response["message"]:
            assert isinstance(prediction, dict)
            assert prediction.get("modelName") == SVM.__name__

    def test_calculatePerformance_withValidParameters_returnPerformance(self, controller, CSVLocation):
        response = controller.calculatePerformance(DecisionTree.__name__, CSVLocation, [], 13)

        assert isinstance(response, dict)
        assert response["status"] == Status.success.value
        assert isinstance(response["message"], dict)
        assert response["message"]["modelName"] == DecisionTree.__name__

    def test_calculatePerformance_withInvalidParameters_returnError(self, controller, CSVLocation):
        for i in range(7):
            if i == 0:
                response = controller.calculatePerformance("InvalidModel", CSVLocation, [], 13)
            elif i == 1:
                response = controller.calculatePerformance(NaiveBayes.__name__, 1000, [], 13)
            elif i == 2:
                response = controller.calculatePerformance(NaiveBayes.__name__, CSVLocation, "[]", 13)
            elif i == 3:
                response = controller.calculatePerformance(NaiveBayes.__name__, CSVLocation, [], "13")
            elif i == 4:
                response = controller.calculatePerformance(None, CSVLocation, [], 13)
            elif i == 5:
                response = controller.calculatePerformance(NaiveBayes.__name__, None, [], 13)
            elif i == 6:
                response = controller.calculatePerformance(NaiveBayes.__name__, CSVLocation, None, 13)
            else:
                response = controller.calculatePerformance(NaiveBayes.__name__, CSVLocation, [], None)

            assert response["status"] == Status.valueError.value
            assert response["message"] == ResponseMsg.InvalidValueProvided.value

    def test_calculatePerformance_withInvalidCSV_returnError(self, controller, CSVLocation):
        for i in range(3):
            if i == 0:
                response = controller.calculatePerformance(NaiveBayes.__name__, CSVLocation, [100], 13) # dropColumn exceed the maximum number of column in Csv
            elif i == 1:
                response = controller.calculatePerformance(NaiveBayes.__name__, CSVLocation, [1, 2, 3, 4],
                                                           13)  # will produce invalid feature of length 9
            else:
                response = controller.calculatePerformance(NaiveBayes.__name__, "InvalidFilePath", [], 13)

            assert response["status"] == Status.valueError.value
            assert response["message"] == ResponseMsg.csvIsInvalid.value

    def test_calculatePerformance_SVMFeaturesCombinedWithDifferentModel_returnError(self, controller,
                                                                                          CSVLocation):
        response = controller.calculatePerformance(DecisionTree.__name__, CSVLocation, [1, 5],
                                                   13)  # dropping sex and fbs and target

        assert response["status"] == Status.valueError.value
        assert response["message"] == ResponseMsg.csvIsInvalid.value

    def test_calculatePerformance_SVMFeaturesCombinedWithSVM_returnPerformance(self, controller, CSVLocation):
        response = controller.calculatePerformance(SVM.__name__, CSVLocation, [1, 5], 13)

        assert isinstance(response, dict)
        assert response["status"] == Status.success.value
        assert isinstance(response["message"], dict)
        assert response["message"]["modelName"] == SVM.__name__

    def test_getAllPredictions_withStoredPredictions_returnPredictions(self, controller, sampleFeatureJson):
        response1 = controller.makePrediction(NaiveBayes.__name__, sampleFeatureJson)
        response2 = controller.makePrediction(SVM.__name__, sampleFeatureJson)

        storedPredictionResults = controller.getAllPredictions()

        assert storedPredictionResults["status"] == Status.success.value
        assert isinstance(storedPredictionResults, dict)
        assert isinstance(storedPredictionResults["message"], list)
        assert storedPredictionResults["message"][0] in [response1["message"], response2["message"]]
        assert storedPredictionResults["message"][1] in [response1["message"], response2["message"]]

    def test_getAllPredictions_withNoStoredPredictions_returnEmptyList(self, controller):
        storedPredictionResults = controller.getAllPredictions()

        assert storedPredictionResults["status"] == Status.success.value
        assert isinstance(storedPredictionResults, dict)
        assert isinstance(storedPredictionResults["message"], list)
        assert len(storedPredictionResults["message"]) == 0

    def test_getPredictionByModel_withValidPredictionName_returnPredictions(self, controller, sampleFeatureJson):
        controller.makePrediction(NaiveBayes.__name__, sampleFeatureJson)
        response1 = controller.makePrediction(SVM.__name__, sampleFeatureJson)
        response2 = controller.makePrediction(SVM.__name__, sampleFeatureJson)

        storedPredictionResults = controller.getPredictionsByModel(SVM.__name__)

        assert storedPredictionResults["status"] == Status.success.value
        assert isinstance(storedPredictionResults, dict)
        assert isinstance(storedPredictionResults["message"], list)
        assert len(storedPredictionResults["message"]) == 2

        for predictionResult in storedPredictionResults["message"]:
            assert predictionResult in [response1["message"], response2["message"]]

    def test_getPredictionByModel_withInvalidPredictionName_returnError(self, controller, sampleFeatureJson):
        for i in range(2):
            if i == 0:
                response = controller.getPredictionsByModel("InvalidPredictionModel")
            else:
                response = controller.getPredictionsByModel(None)

            assert response["status"] == Status.valueError.value
            assert response["message"] == ResponseMsg.InvalidValueProvided.value

    def test_deletePrediction_withExistingPrediction_returnTrueInMessage(self, controller, sampleFeatureJson):
        prediction = controller.makePrediction(NaiveBayes.__name__, sampleFeatureJson)["message"]
        controller.makePrediction(SVM.__name__, sampleFeatureJson)
        controller.makePrediction(SVM.__name__, sampleFeatureJson)

        response = controller.deletePrediction(prediction["Id"])

        assert response["status"] == Status.success.value
        assert response["message"] == True

        storedPredictionResults = controller.getAllPredictions()["message"]

        assert prediction not in [storedPredictionResults]

    def test_deletePrediction_withNonExistingPrediction_returnFalseInMessage(self, controller, sampleFeatureJson):
        response = controller.deletePrediction(str(uuid4()))

        assert response["status"] == Status.success.value
        assert response["message"] == False

    def test_deletePrediction_withInvalidPredictionId_returnError(self, controller):
        for i in range(2):
            if i == 0:
                response = controller.deletePrediction("invalidId")
            else:
                response = controller.deletePrediction(None)

            assert response["status"] == Status.valueError.value
            assert response["message"] == ResponseMsg.InvalidValueProvided.value

    def test_getStatistics_withStoredPredictions_returnStat(self, controller, sampleFeatureJson):
        controller.makePrediction(NaiveBayes.__name__, sampleFeatureJson)
        controller.makePrediction(SVM.__name__, sampleFeatureJson)
        controller.makePrediction(SVM.__name__, sampleFeatureJson)

        response = controller.getStatistics()

        assert response["status"] == Status.success.value
        assert isinstance(response["message"], dict)
        assert isinstance(response["message"]["stat"], dict)
        assert response["message"]["totalCount"] == 3
        assert response["message"]["stat"][NaiveBayes.__name__] == 1
        assert response["message"]["stat"][SVM.__name__] == 2

    def test_getStatistics_withStoredPredictions_returnEmptyStat(self, controller):
        response = controller.getStatistics()

        assert response["status"] == Status.success.value
        assert isinstance(response["message"], dict)
        assert isinstance(response["message"]["stat"], dict)
        assert response["message"]["totalCount"] == 0
        assert response["message"]["stat"] == {}

