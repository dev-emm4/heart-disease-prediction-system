import os
import sys
from uuid import uuid4

import pytest

from src.application import PredictionApplicationService
from src.domain import ErrorMsg
from src.domain.predictionModel import FeatureVector, DecisionTree, NaiveBayes, SVM
from src.infrastructure import DatabaseConnection
from src.infrastructure.persistence import SQLitePredictionResultRepository

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))


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


class TestPredictionResultApplicationService:

    def test_makePrediction_withValidParameters_shouldReturnAndSavePrediction(self, service, sampleFeatureVector):
        results = service.makePrediction("NaiveBayes", [sampleFeatureVector])
        assert len(results) == 1
        assert results[0].modelName() == "NaiveBayes"
        assert results[0].featureVector() == sampleFeatureVector

        retrieved = service.retrievePredictionById(results[0].id())

        assert retrieved is not None
        assert retrieved.id() == results[0].id()

    def test_makePrediction_withInvalidParameters_shouldRaiseError(self, service, sampleFeatureVector):
        for i in range(6):
            try:
                if i == 0:
                    service.makePrediction("InvalidModel", [sampleFeatureVector])
                elif i == 1:
                    service.makePrediction("NaiveBayes", "InvalidFeatureVector")
                elif i == 2:
                    service.makePrediction("NaiveBayes", [])
                elif i == 3:
                    service.makePrediction(None, [sampleFeatureVector])
                elif i == 4:
                    service.makePrediction("NaiveBayes", None)
                elif i == 5:
                    service.makePrediction(1000, [sampleFeatureVector])
                else:
                    service.makePrediction("NaiveBayes", ["InvalidFeatureVector"])

                assert False, "Expected ValueError was not raised"
            except TypeError as e:
                assert str(e) in [ErrorMsg.PredictionServiceInvalidModelName.value,
                                  ErrorMsg.PredictionServiceInvalidFeatureVector.value]

    def test_calculatePerformance_withValidParameters_shouldReturnPerformance(self, service, sampleFeatureVector):
        targets = [1.0]  # Assuming original result is malignant
        performance = service.calculatePerformance("NaiveBayes", [sampleFeatureVector], targets)
        assert performance is not None
        assert performance.modelName() == "NaiveBayes"

    def test_calculatePerformance_withInvalidParameters_shouldRaiseError(self, service, sampleFeatureVector):
        for i in range(6):
            try:
                if i == 0:
                    service.calculatePerformance("InvalidModel", [sampleFeatureVector], [1.0])
                elif i == 1:
                    service.calculatePerformance("NaiveBayes", ["InvalidFeatureVector"], [1.0])
                if i == 2:
                    service.calculatePerformance(None, [sampleFeatureVector], [1.0])
                elif i == 3:
                    service.calculatePerformance("NaiveBayes", None, [1.0])
                elif i == 4:
                    service.calculatePerformance("NaiveBayes", [sampleFeatureVector], None)
                else:
                    service.calculatePerformance("NaiveBayes", [sampleFeatureVector], "InvalidOriginalResults")

                assert False, "Expected ValueError was not raised"
            except TypeError as e:
                assert str(e) in [ErrorMsg.PredictionServiceInvalidModelName.value,
                                  ErrorMsg.PredictionServiceInvalidFeatureVector.value,
                                  ErrorMsg.PredictionServiceInvalidTarget.value]

    def test_retrievePredictionById_withValidId_returnPrediction(self, service, sampleFeatureVector):
        results = service.makePrediction("NaiveBayes", [sampleFeatureVector])
        assert len(results) == 1

        retrieved = service.retrievePredictionById(results[0].id())
        assert retrieved is not None
        assert retrieved.id() == results[0].id()
        assert retrieved.modelName() == "NaiveBayes"
        assert retrieved.featureVector().__json__() == sampleFeatureVector.__json__()
        assert retrieved.isMalignant() == results[0].isMalignant()
        assert retrieved.timeStamp() == results[0].timeStamp()

    def test_retrievePredictionById_withInvalidId_returnPrediction(self, service, sampleFeatureVector):
        for i in range(2):
            try:
                if i == 0:
                    service.retrievePredictionById("invalidId")
                else:
                    service.retrievePredictionById(None)

                assert False, "Expected ValueError was not raised"
            except TypeError as e:
                assert str(e) == ErrorMsg.PredictionServiceInvalidPredictionId.value

    def test_retrieveAllPredictions_returnAllPredictions(self, service, sampleFeatureVector):
        prediction1 = service.makePrediction("NaiveBayes", [sampleFeatureVector])
        prediction2 = service.makePrediction("SVM", [sampleFeatureVector])

        results = service.retrieveAllPredictions()
        model_names = [result.modelName() for result in results]

        assert len(results) == 2
        assert "NaiveBayes" in model_names
        assert "SVM" in model_names
        assert any(result.featureVector().__json__() == sampleFeatureVector.__json__() for result in results)
        assert any(result.isMalignant() == prediction1[0].isMalignant() for result in results)
        assert any(result.isMalignant() == prediction2[0].isMalignant() for result in results)
        assert any(result.timeStamp() == prediction1[0].timeStamp() for result in results)
        assert any(result.timeStamp() == prediction2[0].timeStamp() for result in results)
        assert any(result.id() == prediction1[0].id() for result in results)
        assert any(result.id() == prediction2[0].id() for result in results)

    def test_deletePrediction_withValidId_delete(self, service, sampleFeatureVector):
        results = service.makePrediction("NaiveBayes", [sampleFeatureVector])
        assert len(results) == 1

        deleted = service.deletePrediction(results[0].id())
        assert deleted is True

        retrieved = service.retrievePredictionById(results[0].id())
        assert retrieved is None

    def test_deletePrediction_withInvalidParameter_raiseException(self, service, sampleFeatureVector):
        for i in range(2):
            try:
                if i == 0:
                    service.deletePrediction("invalidId")
                else:
                    service.deletePrediction(None)
                assert False, "Expected ValueError wan not thrown"
            except TypeError as e:
                assert str(e) == ErrorMsg.PredictionServiceInvalidPredictionId.value

    def test_deletePrediction_withNonExistentId_shouldReturnFalse(self, service):
        non_existent_id = uuid4()
        deleted = service.deletePrediction(non_existent_id)
        assert deleted is False

    def test_getPredictionCount_returnCount(self, service, sampleFeatureVector):
        initial_count = service.getPredictionCount()

        service.makePrediction("NaiveBayes", [sampleFeatureVector])
        service.makePrediction("SVM", [sampleFeatureVector])

        count = service.getPredictionCount()
        assert count == initial_count + 2

    def test_getModelStatistics_returnStat(self, service, sampleFeatureVector):
        models = ["DecisionTree", "NaiveBayes", "SVM", "DecisionTree"]
        for model in models:
            service.makePrediction(model, [sampleFeatureVector])

        stats = service.getModelStatistics()
        assert stats["DecisionTree"] == 2
        assert stats["NaiveBayes"] == 1
        assert stats["SVM"] == 1

    def test_retrievePredictionsByModel_withValidModelName_returnPredictions(self, service, sampleFeatureVector):
        service.makePrediction(DecisionTree.__name__, [sampleFeatureVector])
        service.makePrediction(NaiveBayes.__name__, [sampleFeatureVector])
        service.makePrediction(SVM.__name__, [sampleFeatureVector])
        service.makePrediction(DecisionTree.__name__, [sampleFeatureVector])

        decision_tree_predictions = service.retrievePredictionsByModel(DecisionTree.__name__)

        assert len(decision_tree_predictions) == 2

        for prediction in decision_tree_predictions:
            assert prediction.modelName() == "DecisionTree"
            assert prediction.featureVector().__json__() == sampleFeatureVector.__json__()

    def test_retrievePredictionsByModel_withInvalidModelName_returnPredictions(self, service):
        for i in range(3):
            try:
                if i == 0:
                    service.retrievePredictionsByModel(100)
                elif i == 1:
                    service.retrievePredictionsByModel("InvalidModelName")
                else:
                    service.retrievePredictionsByModel(None)

                assert False, "Expected ValueError wan not thrown"
            except TypeError as e:
                assert str(e) == ErrorMsg.PredictionServiceInvalidModelName.value
