from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .PredictionResult import PredictionResult


class PredictionResultRepository(ABC):
    @abstractmethod
    def saveAll(self, prediction_results: list[PredictionResult]) -> None:
        pass

    @abstractmethod
    def findById(self, prediction_id: UUID) -> Optional[PredictionResult]:
        pass

    @abstractmethod
    def findAll(self) -> list[PredictionResult]:
        pass

    @abstractmethod
    def findAllPaginated(self, page: (int | float), pageSize: (int | float)) -> list[PredictionResult]:
        pass

    @abstractmethod
    def findByModelName(self, model_name: str) -> list[PredictionResult]:
        pass

    @abstractmethod
    def delete(self, prediction_id: UUID) -> bool:
        pass

    @abstractmethod
    def deleteAll(self) -> int:
        pass

    @abstractmethod
    def findByNamePaginated(self, modeName: str, page: (int | float), pageSize: (int | float)) -> list[
        PredictionResult]:
        pass

    @abstractmethod
    def countByName(self, modelName: str) -> int:
        pass

    @abstractmethod
    def countAll(self) -> int:
        pass
