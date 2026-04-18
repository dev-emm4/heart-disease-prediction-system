from typing import Optional, List
from uuid import UUID

from domain.predictionModel import PredictionResultRepository
from src.domain import ErrorMsg, AssertionConcern
from src.domain.modelPerformanceCalculator import ModelPerformanceCalculator, PerformanceResult
from src.domain.predictionModel import FeatureVector, NaiveBayes, PredictionResult, SVM, DecisionTree


class PredictionApplicationService:
    def __init__(self, repository: PredictionResultRepository):
        self._repository = repository

    def makePrediction(self, modelName: str, featureVectors: list[FeatureVector]) -> list[PredictionResult]:
        AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionServiceInvalidModelName.value)
        AssertionConcern.assertListItemsIsOfType(featureVectors, FeatureVector,
                                                 ErrorMsg.PredictionServiceInvalidFeatureVector.value)
        AssertionConcern.assertTrue((len(featureVectors) > 0), ErrorMsg.PredictionServiceInvalidFeatureVector.value)

        predictionResults: list[PredictionResult]

        if modelName == NaiveBayes.__name__:
            predictionResults = NaiveBayes().makePrediction(featureVectors)
        elif modelName == SVM.__name__:
            predictionResults = SVM().makePrediction(featureVectors)
        elif modelName == DecisionTree.__name__:
            predictionResults = DecisionTree().makePrediction(featureVectors)
        else:
            raise TypeError(ErrorMsg.PredictionServiceInvalidModelName.value)

        self._repository.saveAll(predictionResults)

        return predictionResults

    def calculatePerformance(self, modelName: str, featureVectors: list[FeatureVector],
                             target: list[float | int]) -> PerformanceResult:
        AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionServiceInvalidModelName.value)
        AssertionConcern.assertListItemsIsOfType(featureVectors, FeatureVector,
                                                 ErrorMsg.PredictionServiceInvalidFeatureVector.value)
        AssertionConcern.assertTrue((len(featureVectors) > 0), ErrorMsg.PredictionServiceInvalidFeatureVector.value)
        AssertionConcern.assertListItemsIsOfType(target, (float | int), ErrorMsg.PredictionServiceInvalidTarget.value)

        performanceResult: PerformanceResult

        if modelName == NaiveBayes.__name__:
            performanceResult = ModelPerformanceCalculator().calculatePerformance(NaiveBayes(), featureVectors,
                                                                                  target)
        elif modelName == SVM.__name__:
            performanceResult = ModelPerformanceCalculator().calculatePerformance(SVM(), featureVectors,
                                                                                  target)
        elif modelName == DecisionTree.__name__:
            performanceResult = ModelPerformanceCalculator().calculatePerformance(DecisionTree(), featureVectors,
                                                                                  target)
        else:
            raise TypeError(ErrorMsg.PredictionServiceInvalidModelName.value)

        return performanceResult

    def retrievePredictionById(self, predictionId: UUID) -> Optional[PredictionResult]:
        AssertionConcern.assertIsType(predictionId, UUID, ErrorMsg.PredictionServiceInvalidPredictionId.value)

        return self._repository.findById(predictionId)

    def retrieveAllPredictions(self) -> List[PredictionResult]:
        return self._repository.findAll()

    def retrievePaginatedPredictions(self, page: (int | float), pageSize: (int | float)) -> list[PredictionResult]:
        AssertionConcern.assertIsType(page, (float, int), ErrorMsg.PredictionServiceInvalidPage.value)
        AssertionConcern.assertIsType(pageSize, (float, int), ErrorMsg.PredictionServiceInvalidPageSize.value)
        AssertionConcern.asserFalse(page <= 0, ErrorMsg.PredictionServiceInvalidPage.value)
        AssertionConcern.asserFalse(pageSize < 0, ErrorMsg.PredictionServiceInvalidPageSize.value)

        return self._repository.findAllPaginated(page, pageSize)

    def retrievePredictionByNamePaginated(self, modelName: str, page: (int | float), pageSize: (int | float)) -> list[
        PredictionResult]:
        AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionServiceInvalidModelName.value)
        AssertionConcern.assertItemIn(modelName, [NaiveBayes.__name__, DecisionTree.__name__, SVM.__name__],
                                      ErrorMsg.PredictionServiceInvalidModelName.value)
        AssertionConcern.assertIsType(page, (float, int), ErrorMsg.PredictionServiceInvalidPage.value)
        AssertionConcern.assertIsType(pageSize, (float, int), ErrorMsg.PredictionServiceInvalidPageSize.value)
        AssertionConcern.asserFalse(page <= 0, ErrorMsg.PredictionServiceInvalidPage.value)
        AssertionConcern.asserFalse(pageSize < 0, ErrorMsg.PredictionServiceInvalidPageSize.value)

        return self._repository.findByNamePaginated(modelName, page, pageSize)

    def retrievePredictionsByModel(self, modelName: str) -> List[PredictionResult]:
        AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionServiceInvalidModelName.value)
        AssertionConcern.assertItemIn(modelName, [NaiveBayes.__name__, DecisionTree.__name__, SVM.__name__],
                                      ErrorMsg.PredictionServiceInvalidModelName.value)

        return self._repository.findByModelName(modelName)

    def deletePrediction(self, predictionId: UUID) -> bool:
        AssertionConcern.assertIsType(predictionId, UUID, ErrorMsg.PredictionServiceInvalidPredictionId.value)

        return self._repository.delete(predictionId)

    def deleteAllPrediction(self) -> int:
        return self._repository.deleteAll()

    def getPredictionCount(self) -> int:
        return self._repository.countAll()

    def getModelPredictionCount(self, modelName: str):
        AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionServiceInvalidModelName.value)
        AssertionConcern.assertItemIn(modelName, [NaiveBayes.__name__, DecisionTree.__name__, SVM.__name__],
                                      ErrorMsg.PredictionServiceInvalidModelName.value)

        return self._repository.countByName(modelName)

    def getModelStatistics(self) -> dict:
        allPredictions = self._repository.findAll()
        statistics = {}

        for prediction in allPredictions:
            modelName = prediction.modelName()
            statistics[modelName] = statistics.get(modelName, 0) + 1

        return statistics
