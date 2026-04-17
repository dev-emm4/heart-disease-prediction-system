from typing import Dict, Any
from typing import List
from uuid import UUID

import pandas as pd

from src.application import PredictionApplicationService
from src.domain import AssertionConcern, ErrorMsg
from src.domain.modelPerformanceCalculator import PerformanceResult
from src.domain.predictionModel import FeatureVector, PredictionResult, FeatureVectorAttributes
from src.domain.predictionModel import NaiveBayes, SVM, DecisionTree
from src.infrastructure import FeatureVectorLoader
from .ResponseMsg import ResponseMsg
from .Status import Status


class PredictionController:
    def __init__(self, application_service: PredictionApplicationService, featureVectorLoader: FeatureVectorLoader):
        self._service: PredictionApplicationService = application_service
        self._featureVectorLoader: FeatureVectorLoader = featureVectorLoader

    def makePrediction(self, modelName: str, featureJson: Dict[str, Any]) -> Dict[str, Any]:
        try:
            AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionControllerInvalidModelName.value)
            AssertionConcern.assertItemIn(modelName, [NaiveBayes.__name__, SVM.__name__, DecisionTree.__name__],
                                          ErrorMsg.PredictionControllerInvalidModelName.value)
            AssertionConcern.assertIsType(featureJson, dict, ErrorMsg.PredictionControllerInvalidFeatureJson.value)

            featureVector: list[FeatureVector] = [self._mapFeatureJsonToFeatureVector(featureJson)]
            predictionResult: list[PredictionResult] = self._service.makePrediction(modelName, featureVector)

            return self._createMessage(Status.success.value, predictionResult[0].__json__())
        except TypeError as e:
            if (str(e) in ErrorMsg.predictionControllerSpecificErrorMsg()) or str(
                    e) == ErrorMsg.FeatureVectorInvalidFeatures.value:
                return self._createMessage(Status.valueError.value, ResponseMsg.InvalidValueProvided.value)
            else:
                return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

        except Exception as e:
            return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

    def _mapFeatureJsonToFeatureVector(self, featureJson: Dict[str, Any]) -> FeatureVector:
        return FeatureVector(
            featureJson.get(FeatureVectorAttributes.age.value),
            featureJson.get(FeatureVectorAttributes.sex.value),
            featureJson.get(FeatureVectorAttributes.cp.value),
            featureJson.get(FeatureVectorAttributes.trestbps.value),
            featureJson.get(FeatureVectorAttributes.chol.value),
            featureJson.get(FeatureVectorAttributes.fbs.value),
            featureJson.get(FeatureVectorAttributes.restecg.value),
            featureJson.get(FeatureVectorAttributes.thalach.value),
            featureJson.get(FeatureVectorAttributes.exang.value),
            featureJson.get(FeatureVectorAttributes.oldpeak.value),
            featureJson.get(FeatureVectorAttributes.slope.value),
            featureJson.get(FeatureVectorAttributes.ca.value),
            featureJson.get(FeatureVectorAttributes.thal.value)
        )

    def makeBulkPredictions(self, modelName: str, filePath: str, dropColumn: list[int | float]) -> Dict[str, Any]:
        try:
            AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionControllerInvalidModelName.value)
            AssertionConcern.assertItemIn(modelName, [NaiveBayes.__name__, SVM.__name__, DecisionTree.__name__],
                                          ErrorMsg.PredictionControllerInvalidModelName.value)
            AssertionConcern.assertIsType(filePath, str, ErrorMsg.PredictionControllerInvalidFilePath.value)
            AssertionConcern.assertListItemsIsOfType(dropColumn, (int | float),
                                                     ErrorMsg.PredictionControllerInvalidDropColOption.value)

            featureVectors: List[FeatureVector] = self._featureVectorLoader.initiateFeatureVectorsFromCsv(filePath,
                                                                                                          dropColumn)
            predictionResults: List[PredictionResult] = self._service.makePrediction(modelName, featureVectors)

            return self._createMessage(Status.success.value, [p.__json__() for p in predictionResults])
        except (pd.errors.ParserError, FileNotFoundError):
            return self._createMessage(Status.valueError.value, ResponseMsg.csvIsInvalid.value)

        except (TypeError, IndexError) as e:
            if str(e) in ErrorMsg.predictionControllerSpecificErrorMsg():
                return self._createMessage(Status.valueError.value, ResponseMsg.InvalidValueProvided.value)

            elif str(e) in [ErrorMsg.FeatureVectorLoaderInvalidCSVLength.value,
                            ErrorMsg.FeatureVectorLoaderDropColOutOfBounds.value,
                            ErrorMsg.FeatureVectorInvalidFeatures.value
                            ]:
                return self._createMessage(Status.valueError.value, ResponseMsg.csvIsInvalid.value)

            else:
                return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

        except Exception as e:
            return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

    def calculatePerformance(self, modelName: str, filePath: str, dropColumn: list[int | float],
                             targetColumn: int | float) -> Dict[str, Any]:
        try:
            AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionControllerInvalidModelName.value)
            AssertionConcern.assertItemIn(modelName, [NaiveBayes.__name__, SVM.__name__, DecisionTree.__name__],
                                          ErrorMsg.PredictionControllerInvalidModelName.value)
            AssertionConcern.assertIsType(filePath, str, ErrorMsg.PredictionControllerInvalidFilePath.value)
            AssertionConcern.assertListItemsIsOfType(dropColumn, (int | float),
                                                     ErrorMsg.PredictionControllerInvalidDropColOption.value)
            AssertionConcern.assertIsType(targetColumn, (int | float),
                                          ErrorMsg.PredictionControllerInvalidTargetColOption.value)

            featureVectors, target = self._featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(filePath,
                                                                                                      dropColumn,
                                                                                                      targetColumn)
            performanceResult: PerformanceResult = self._service.calculatePerformance(modelName, featureVectors, target)

            return self._createMessage(Status.success.value, performanceResult.__json__())
        except (pd.errors.ParserError, FileNotFoundError):
            return self._createMessage(Status.valueError.value, ResponseMsg.csvIsInvalid.value)

        except (TypeError, IndexError) as e:
            if str(e) in ErrorMsg.predictionControllerSpecificErrorMsg():
                return self._createMessage(Status.valueError.value, ResponseMsg.InvalidValueProvided.value)

            elif str(e) in [ErrorMsg.FeatureVectorLoaderInvalidCSVLength.value,
                            ErrorMsg.FeatureVectorLoaderDropColOutOfBounds.value,
                            ErrorMsg.FeatureVectorLoaderTargetColOutOfBounds.value,
                            ErrorMsg.FeatureVectorInvalidFeatures.value
                            ]:
                return self._createMessage(Status.valueError.value, ResponseMsg.csvIsInvalid.value)

            else:
                return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

        except Exception as e:
            return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

    def getAllPredictions(self) -> Dict[str, Any]:
        try:
            predictions = self._service.retrieveAllPredictions()
            return self._createMessage(Status.success.value, [p.__json__() for p in predictions])

        except Exception as e:
            return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

    def getPredictionsByModel(self, modelName: str) -> dict[str, Any]:
        try:
            AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionControllerInvalidModelName.value)
            AssertionConcern.assertItemIn(modelName, [NaiveBayes.__name__, SVM.__name__, DecisionTree.__name__],
                                          ErrorMsg.PredictionControllerInvalidModelName.value)

            predictions = self._service.retrievePredictionsByModel(modelName)

            return self._createMessage(Status.success.value, [p.__json__() for p in predictions])
        except TypeError as e:
            if str(e) in ErrorMsg.predictionControllerSpecificErrorMsg():
                return self._createMessage(Status.valueError.value, ResponseMsg.InvalidValueProvided.value)
            else:
                return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)
        except Exception as e:
            return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

    def deletePrediction(self, predictionId: str) -> Dict[str, Any]:
        try:
            uuidId = self._createUUIDFromString(predictionId)
            deleted = self._service.deletePrediction(uuidId)

            return self._createMessage(Status.success.value, deleted)
        except TypeError as e:
            if str(e) in ErrorMsg.predictionControllerSpecificErrorMsg():

                return self._createMessage(Status.valueError.value, ResponseMsg.InvalidValueProvided.value)
            else:

                return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)
        except Exception as e:
            return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

    def _createUUIDFromString(self, string) -> UUID:
        try:
            return UUID(string)
        except (ValueError, TypeError) as e:
            AssertionConcern.assertTrue(False, ErrorMsg.PredictionControllerInvalidPredictionId.value)

    def getStatistics(self) -> dict[str, Any]:
        try:
            totalCount = self._service.getPredictionCount()
            modelStats = self._service.getModelStatistics()
            return self._createMessage(Status.success.value,
                                       {"stat": modelStats, "totalCount": totalCount})

        except Exception as e:
            return self._createMessage(Status.internalError.value, ResponseMsg.UnexpectedErrorEncountered.value)

    def _createMessage(self, status: str, message) -> dict:
        return {
            "status": status,
            "message": message,
        }
