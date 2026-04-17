from datetime import datetime
from uuid import UUID

from common.AssertionConcern import AssertionConcern
from common.ErrorMsg import ErrorMsg
from .FeatureVector import FeatureVector


class PredictionResult:
    def __init__(self, Id: UUID, modelName: str, featureVector: FeatureVector, isMalignant: bool, timeStamp: datetime):
        AssertionConcern.assertIsType(Id, UUID, ErrorMsg.PredictionResultInvalidId.value)
        AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionResultInvalidModelName.value)
        AssertionConcern.assertItemIn(modelName, ["NaiveBayes", "SVM", "DecisionTree"],
                                      ErrorMsg.PredictionResultInvalidModelName.value)
        AssertionConcern.assertIsType(featureVector, FeatureVector, ErrorMsg.PredictionResultInvalidFeatureVector.value)
        AssertionConcern.assertIsType(isMalignant, bool, ErrorMsg.PredictionResultInvalidDiag.value)
        AssertionConcern.assertIsType(timeStamp, datetime, ErrorMsg.PredictionResultInvalidTimeStamp.value)

        self._Id: UUID = Id
        self._modelName: str = modelName
        self._featureVector: FeatureVector = featureVector
        self._isMalignant: bool = isMalignant
        self._timeStamp: datetime = timeStamp

    def id(self) -> UUID:
        return self._Id

    def modelName(self) -> str:
        return self._modelName

    def featureVector(self) -> FeatureVector:
        return self._featureVector

    def isMalignant(self) -> bool:
        return self._isMalignant

    def timeStamp(self) -> datetime:
        return self._timeStamp

    def __str__(self):
        return f"PredictionResult(Id: {self._Id}, Model: {self._modelName}, FeatureVector: {self._featureVector}, IsMalignant: {self._isMalignant}, TimeStamp: {self._timeStamp})"

    def __repr__(self):
        return self.__str__()

    def __json__(self):
        return {
            "Id": str(self._Id),
            "modelName": self._modelName,
            "featureVector": self._featureVector.__json__(),
            "isMalignant": self._isMalignant,
            "timeStamp": self._timeStamp.isoformat()
        }
