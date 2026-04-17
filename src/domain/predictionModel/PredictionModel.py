from abc import ABC, abstractmethod

from .FeatureVector import FeatureVector
from .PredictionResult import PredictionResult


class PredictionModel(ABC):
    @abstractmethod
    def makePrediction(self, featureVector: list[FeatureVector]) -> list[PredictionResult]:
        pass
