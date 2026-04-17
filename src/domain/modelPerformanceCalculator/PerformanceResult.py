from common.AssertionConcern import AssertionConcern
from common.ErrorMsg import ErrorMsg


class PerformanceResult:
    def __init__(self, modelName: str, recall: float, accuracy: float, precision: float):
        AssertionConcern.assertIsType(modelName, str, ErrorMsg.PerformanceResultInvalidModelName.value)
        AssertionConcern.assertItemIn(modelName, ["NaiveBayes", "SVM", "DecisionTree"],
                                      ErrorMsg.PerformanceResultInvalidModelName.value)
        AssertionConcern.assertIsType(recall, (float, int), ErrorMsg.PerformanceResultInvalidRecall.value)
        AssertionConcern.assertIsType(accuracy, (float, int), ErrorMsg.PerformanceResultInvalidAccuracy.value)
        AssertionConcern.assertIsType(precision, (float, int), ErrorMsg.PerformanceResultInvalidPrecision.value)

        self.__modelName: str = modelName
        self.__recall: float = recall
        self.__accuracy: float = accuracy
        self.__precision: float = precision

    def modelName(self) -> str:
        return self.__modelName

    def accuracy(self) -> float:
        return self.__accuracy

    def recall(self) -> float:
        return self.__recall

    def precision(self) -> float:
        return self.__precision

    def __str__(self):
        return f"Model: {self.__modelName}, Recall: {self.__recall:.4f}, Accuracy: {self.__accuracy:.4f}, Precision: {self.__precision:.4f}"

    def __repr__(self):
        return self.__str__()

    def __json__(self):
        return {
            "modelName": self.__modelName,
            "recall": self.__recall,
            "accuracy": self.__accuracy,
            "precision": self.__precision
        }
