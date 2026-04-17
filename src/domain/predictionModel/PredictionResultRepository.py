from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from .PredictionResult import PredictionResult


class PredictionResultRepository(ABC):
    # @abstractmethod
    # def save(self, prediction_result: PredictionResult) -> None:
    #     """
    #     Persist a PredictionResult to the repository.
    #
    #     Args:
    #         prediction_result: The PredictionResult aggregate to persist
    #
    #     Raises:
    #         ValueError: If the prediction result is invalid
    #         Exception: If persistence fails
    #     """
    #     pass

    @abstractmethod
    def saveAll(self, prediction_results: List[PredictionResult]) -> None:
        """
        Persist multiple PredictionResults to the repository.

        Args:
            prediction_results: A list of PredictionResult aggregates to persist

        Raises:
            ValueError: If any prediction result is invalid
            Exception: If persistence fails
        """
        pass

    @abstractmethod
    def findById(self, prediction_id: UUID) -> Optional[PredictionResult]:
        """
        Retrieve a PredictionResult by its unique identifier.

        Args:
            prediction_id: The UUID of the PredictionResult to retrieve

        Returns:
            The PredictionResult if found, None otherwise
        """
        pass

    @abstractmethod
    def findAll(self) -> List[PredictionResult]:
        """
        Retrieve all PredictionResults from the repository.

        Returns:
            A list of all PredictionResult aggregates
        """
        pass

    @abstractmethod
    def findByModelName(self, model_name: str) -> List[PredictionResult]:
        """
        Retrieve all PredictionResults created by a specific model.

        Args:
            model_name: The name of the model

        Returns:
            A list of PredictionResults created by the specified model
        """
        pass

    @abstractmethod
    def delete(self, prediction_id: UUID) -> bool:
        """
        Delete a PredictionResult from the repository.

        Args:
            prediction_id: The UUID of the PredictionResult to delete

        Returns:
            True if deletion was successful, False if the entity was not found
        """
        pass
