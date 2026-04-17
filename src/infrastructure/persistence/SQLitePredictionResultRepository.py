import json
import sqlite3
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from src.domain import AssertionConcern, ErrorMsg
from src.domain.predictionModel import FeatureVector
from src.domain.predictionModel import PredictionResult
from src.domain.predictionModel import PredictionResultRepository
from ..DatabaseConnection import DatabaseConnection
from ..DbError import DbError


class SQLitePredictionResultRepository(PredictionResultRepository):
    def __init__(self, database: DatabaseConnection):
        self._database = database

    def saveAll(self, predictionResults: List[PredictionResult]) -> None:
        AssertionConcern.assertListItemsIsOfType(predictionResults, PredictionResult,
                                                 ErrorMsg.PredictionResultRepoInvalidPredictionResult.value)

        try:
            with self._database.getConnection() as conn:
                cursor = conn.cursor()
                data = [
                    (
                        str(pr.id()),
                        pr.modelName(),
                        json.dumps(pr.featureVector().__json__()),
                        1 if pr.isMalignant() else 0,
                        pr.timeStamp().isoformat()
                    )
                    for pr in predictionResults
                ]
                cursor.executemany('''
                    INSERT INTO prediction_results 
                    (id, model_name, feature_vector, is_malignant, time_stamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', data)
                conn.commit()
        except Exception as e:
            raise DbError(f"Failed to save PredictionResults to database: {str(e)}")

    def findById(self, predictionId: UUID) -> Optional[PredictionResult]:
        AssertionConcern.assertIsType(predictionId, UUID,
                                      ErrorMsg.PredictionResultRepoInvalidPredictionId.value)

        try:
            with self._database.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM prediction_results WHERE id = ?
                ''', (str(predictionId),))
                row = cursor.fetchone()

                if row is None:
                    return None

                return self._mapRowToPredictionResult(row)
        except Exception as e:
            raise DbError(f"Failed to retrieve PredictionResult by ID: {str(e)}")

    def findAll(self) -> List[PredictionResult]:
        try:
            with self._database.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM prediction_results ORDER BY time_stamp DESC')
                rows = cursor.fetchall()

                return [self._mapRowToPredictionResult(row) for row in rows]
        except Exception as e:
            raise DbError(f"Failed to retrieve all PredictionResults: {str(e)}")

    def findByModelName(self, modelName: str) -> List[PredictionResult]:
        AssertionConcern.assertIsType(modelName, str, ErrorMsg.PredictionResultRepoInvalidPredictionModelName.value)
        AssertionConcern.assertItemIn(modelName, ["NaiveBayes", "SVM", "DecisionTree"],
                                      ErrorMsg.PredictionResultRepoInvalidPredictionModelName.value)

        try:
            with self._database.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM prediction_results 
                    WHERE model_name = ? 
                    ORDER BY time_stamp DESC
                ''', (modelName,))
                rows = cursor.fetchall()

                return [self._mapRowToPredictionResult(row) for row in rows]
        except Exception as e:
            raise DbError(f"Failed to retrieve PredictionResults by model name: {str(e)}")

    def delete(self, predictionId: UUID) -> bool:
        AssertionConcern.assertIsType(predictionId, UUID, ErrorMsg.PredictionResultRepoInvalidPredictionId.value)

        try:
            with self._database.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM prediction_results WHERE id = ?
                ''', (str(predictionId),))
                conn.commit()

                return cursor.rowcount > 0
        except Exception as e:
            raise DbError(f"Failed to delete PredictionResult: {str(e)}")

    def _mapRowToPredictionResult(self, row: sqlite3.Row) -> PredictionResult:
        # Deserialize the feature vector from JSON
        featureVectorData = json.loads(row['feature_vector'])
        feature_vector = FeatureVector(
            age=featureVectorData['age'],
            sex=featureVectorData['sex'],
            cp=featureVectorData['cp'],
            trestbps=featureVectorData['trestbps'],
            chol=featureVectorData['chol'],
            fbs=featureVectorData['fbs'],
            restecg=featureVectorData['restecg'],
            thalach=featureVectorData['thalach'],
            exang=featureVectorData['exang'],
            oldpeak=featureVectorData['oldpeak'],
            slope=featureVectorData['slope'],
            ca=featureVectorData['ca'],
            thal=featureVectorData['thal']
        )

        return PredictionResult(
            Id=UUID(row['id']),
            modelName=row['model_name'],
            featureVector=feature_vector,
            isMalignant=bool(row['is_malignant']),
            timeStamp=datetime.fromisoformat(row['time_stamp'])
        )
