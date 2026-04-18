import os
import sys
from datetime import datetime
from typing import Optional
from uuid import uuid4

import pytest

from src.application import PredictionApplicationService
from src.domain import ErrorMsg
from src.domain.predictionModel import FeatureVector
from src.domain.predictionModel import PredictionResult
from src.infrastructure import DatabaseConnection
from src.infrastructure.persistence import SQLitePredictionResultRepository

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


@pytest.fixture
def inMemoryDb():
    db = DatabaseConnection(db_path=":memory:")
    yield db
    db.close()


@pytest.fixture
def repository(inMemoryDb):
    return SQLitePredictionResultRepository(inMemoryDb)


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


@pytest.fixture
def samplePrediction(sampleFeatureVector):
    """Create a sample prediction result for testing."""
    return PredictionResult(
        Id=uuid4(),
        modelName="NaiveBayes",
        featureVector=sampleFeatureVector,
        isMalignant=True,
        timeStamp=datetime.now()
    )


class TestSQLitePredictionResultRepository:
    def test_saveAll_withValidPredictions_shouldPersistAll(self, repository, sampleFeatureVector):
        predictions = [
            PredictionResult(
                Id=uuid4(),
                modelName="NaiveBayes",
                featureVector=sampleFeatureVector,
                isMalignant=True,
                timeStamp=datetime.now()
            ),
            PredictionResult(
                Id=uuid4(),
                modelName="SVM",
                featureVector=sampleFeatureVector,
                isMalignant=False,
                timeStamp=datetime.now()
            )
        ]

        repository.saveAll(predictions)

        allResults = repository.findAll()
        assert len(allResults) == 2

        retrieved_ids = {r.id() for r in allResults}

        for pred in predictions:
            assert isinstance(pred, PredictionResult)
            assert pred.id() in retrieved_ids

    def test_saveAll_withInvalidPredictionResult_shouldRaiseError(self, repository, sampleFeatureVector):
        for i in range(3):
            try:
                if i == 0:
                    repository.saveAll(["invalid_prediction"])
                elif i == 1:
                    repository.saveAll("invalid_prediction")
                else:
                    repository.saveAll(None)

                assert False, "Exception Expected"
            except TypeError as e:
                assert str(e) == ErrorMsg.PredictionResultRepoInvalidPredictionResult.value

    def test_findById_WithExistingPrediction_returnPrediction(self, repository, samplePrediction):
        repository.saveAll([samplePrediction])

        result = repository.findById(samplePrediction.id())

        assert isinstance(result, PredictionResult)
        assert result is not None
        assert result.id() == samplePrediction.id()
        assert result.isMalignant() == samplePrediction.isMalignant()

    def test_findById_withNonExistingPrediction_returnNone(self, repository):
        nonExistingId = uuid4()
        result = repository.findById(nonExistingId)
        assert result is None

    def test_findById_withInvalidId_raiseException(self, repository):
        for i in range(2):
            try:
                if i == 0:
                    repository.findById("invalid_id")
                else:
                    repository.findById(None)

                assert False, "Exception Expected"
            except TypeError as e:
                assert str(e) == ErrorMsg.PredictionResultRepoInvalidPredictionId.value

    def test_findAll_withNoPredictionsStored_returnEmptyList(self, repository):
        results = repository.findAll()
        assert results == []

    def test_findAll_withPredictionsStored_returnAll(self, repository, sampleFeatureVector):
        predictionResults: list[PredictionResult] = []

        for i in range(3):
            pred = PredictionResult(
                Id=uuid4(),
                modelName="NaiveBayes",
                featureVector=sampleFeatureVector,
                isMalignant=i % 2 == 0,
                timeStamp=datetime.now()
            )
            predictionResults.append(pred)

        repository.saveAll(predictionResults)
        retrievedResults = repository.findAll()
        assert len(retrievedResults) == 3

        retrieved_ids = [r.id() for r in retrievedResults]
        for predictionResult in predictionResults:
            assert isinstance(predictionResult, PredictionResult)
            assert predictionResult.id() in retrieved_ids

    def test_findByModelName_withExistingModel_returnPredictions(self, repository, sampleFeatureVector):
        pred1 = PredictionResult(
            Id=uuid4(),
            modelName="DecisionTree",
            featureVector=sampleFeatureVector,
            isMalignant=True,
            timeStamp=datetime.now()
        )
        pred2 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )

        repository.saveAll([pred1, pred2])

        results = repository.findByModelName("DecisionTree")
        for result in results:
            assert isinstance(result, PredictionResult)

        assert len(results) == 1
        assert results[0].modelName() == "DecisionTree"

    def test_findByModelName_withNonExistingModel_returnEmptyList(self, repository):
        results = repository.findByModelName("DecisionTree")
        assert results == []

    def test_findByModelName_withInvalidModelNameType_raiseException(self, repository):
        for i in range(3):
            try:
                if i == 0:
                    repository.findByModelName(123)
                elif i == 1:
                    repository.findByModelName("inValidModelName")
                else:
                    repository.findByModelName(None)

                assert False, "should raise exception"
            except TypeError as e:
                assert str(e) == ErrorMsg.PredictionResultRepoInvalidPredictionModelName.value

    def test_findAllPaginated_withValidPageAndPageSize_returnPredictions(self, repository, sampleFeatureVector):
        pred1 = PredictionResult(
            Id=uuid4(),
            modelName="DecisionTree",
            featureVector=sampleFeatureVector,
            isMalignant=True,
            timeStamp=datetime.now()
        )
        pred2 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )
        pred3 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )
        repository.saveAll([pred1, pred2, pred3])

        predictionResults: list[PredictionResult] = repository.findAllPaginated(1, 2)

        assert len(predictionResults) == 2

    def test_findAllPaginated_withInvalidPageAndPageSize_raiseException(self, repository):
        for i in range(8):
            try:
                if i == 0:
                    repository.findAllPaginated("0", 40)
                elif i == 1:
                    repository.findAllPaginated(1, "40")
                elif i == 2:
                    repository.findAllPaginated(None, 50)
                elif i == 3:
                    repository.findAllPaginated(0, 50)
                elif i == 4:
                    repository.findAllPaginated(-2, 50)
                elif i == 5:
                    repository.findAllPaginated(2, -1)
                else:
                    repository.findAllPaginated(2, None)
            except TypeError as e:
                assert str(e) in [ErrorMsg.PredictionResultRepoInvalidPageSize.value,
                                  ErrorMsg.PredictionResultRepoInvalidPage.value]

    def test_findByNamePaginated_withValidParameters_returnPredictions(self, repository, sampleFeatureVector):
        pred1 = PredictionResult(
            Id=uuid4(),
            modelName="DecisionTree",
            featureVector=sampleFeatureVector,
            isMalignant=True,
            timeStamp=datetime.now()
        )
        pred2 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )
        pred3 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )
        repository.saveAll([pred1, pred2, pred3])

        predictionResults: list[PredictionResult] = repository.findByNamePaginated("NaiveBayes", 1, 3)

        assert len(predictionResults) == 2

    def test_findByNamePaginated_withInvalidParameters_raiseException(self, repository):
        for i in range(11):
            try:
                if i == 0:
                    repository.findByNamePaginated("NaiveBayes", "0", 40)
                elif i == 1:
                    repository.findByNamePaginated("NaiveBayes", 1, "40")
                elif i == 2:
                    repository.findByNamePaginated("NaiveBayes", None, 50)
                elif i == 3:
                    repository.findByNamePaginated("NaiveBayes", 0, 50)
                elif i == 4:
                    repository.findByNamePaginated("NaiveBayes", -2, 50)
                elif i == 5:
                    repository.findByNamePaginated("NaiveBayes", 2, -1)
                elif i == 6:
                    repository.findByNamePaginated("invalidModelName", 0, 50)
                elif i == 7:
                    repository.findByNamePaginated(10, -2, 50)
                elif i == 8:
                    repository.findByNamePaginated(None, 2, -1)
                else:
                    repository.findByNamePaginated("NaiveBayes", 2, None)
            except TypeError as e:
                assert str(e) in [ErrorMsg.PredictionResultRepoInvalidPageSize.value,
                                  ErrorMsg.PredictionResultRepoInvalidPage.value,
                                  ErrorMsg.PredictionResultRepoInvalidPredictionModelName.value]

    def test_countByName_withValidParameters_returnNumberOfModelPrediction(self, repository, sampleFeatureVector):
        pred1 = PredictionResult(
            Id=uuid4(),
            modelName="DecisionTree",
            featureVector=sampleFeatureVector,
            isMalignant=True,
            timeStamp=datetime.now()
        )
        pred2 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )
        pred3 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )

        repository.saveAll([pred1, pred2, pred3])

        numOfNBPrediction: int = repository.countByName("NaiveBayes")
        assert numOfNBPrediction == 2

        numOfDTPrediction: int = repository.countByName("DecisionTree")
        assert numOfDTPrediction == 1

    def test_countByName_withInvalidParameters_raiseException(self, repository):
        for i in range(4):
            try:
                if i == 0:
                    repository.countByName("invalidModelName")
                if i == 1:
                    repository.countByName(10)
                else:
                    repository.countByName(None)
            except TypeError as e:
                assert str(e) == ErrorMsg.PredictionResultRepoInvalidPredictionModelName.value

    def test_countAll_returnNumberOfPredictions(self, repository, sampleFeatureVector):
        pred1 = PredictionResult(
            Id=uuid4(),
            modelName="DecisionTree",
            featureVector=sampleFeatureVector,
            isMalignant=True,
            timeStamp=datetime.now()
        )
        pred2 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )
        pred3 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )

        repository.saveAll([pred1, pred2, pred3])

        numOfPrediction: int = repository.countAll()
        assert numOfPrediction == 3

    def test_delete_withExistingPrediction_shouldDelete(self, repository, samplePrediction):
        repository.saveAll([samplePrediction])

        deleted = repository.delete(samplePrediction.id())
        assert deleted is True

        result = repository.findById(samplePrediction.id())
        assert result is None

    def test_delete_withNonExistingPrediction_shouldReturnFalse(self, repository):
        nonExistingId = uuid4()
        deleted = repository.delete(nonExistingId)
        assert deleted is False

    def test_delete_withInvalidPredictionResultId_raiseException(self, repository):
        for i in range(3):
            try:
                if i == 0:
                    repository.delete(123)
                elif i == 1:
                    repository.delete("inValidId")
                else:
                    repository.delete(None)

                assert False, "Exception Expected"
            except TypeError as e:
                assert str(e) == ErrorMsg.PredictionResultRepoInvalidPredictionId.value

    def test_deleteAll_returnRowCountOfDeletedRows(self, repository, sampleFeatureVector):
        pred1 = PredictionResult(
            Id=uuid4(),
            modelName="DecisionTree",
            featureVector=sampleFeatureVector,
            isMalignant=True,
            timeStamp=datetime.now()
        )
        pred2 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )
        pred3 = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=False,
            timeStamp=datetime.now()
        )

        repository.saveAll([pred1, pred2, pred3])
        numOfDeletedCol = repository.deleteAll()

        assert numOfDeletedCol == 3

        numOfDeletedCol = repository.deleteAll()

        assert numOfDeletedCol == 0

    def test_featureVectorSerialization(self, repository, sampleFeatureVector):
        prediction = PredictionResult(
            Id=uuid4(),
            modelName="NaiveBayes",
            featureVector=sampleFeatureVector,
            isMalignant=True,
            timeStamp=datetime.now()
        )

        repository.saveAll([prediction])
        retrieved: Optional[PredictionResult] = repository.findById(prediction.id())

        if retrieved is None:
            pytest.fail("Failed to retrieve the saved prediction result for feature vector serialization test.")

        original_fv = prediction.featureVector()
        retrieved_fv = retrieved.featureVector()

        assert original_fv.__json__() == retrieved_fv.__json__()
