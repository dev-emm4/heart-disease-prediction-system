from typing import Any

import pandas as pd

from domain import AssertionConcern, ErrorMsg
from src.domain.predictionModel import FeatureVector


class FeatureVectorLoader:
    def initiateFeatureVectorsFromCsv(self, filePath: str, dropColumns: list[int | float]) -> list[FeatureVector]:
        AssertionConcern.assertIsType(filePath, str, ErrorMsg.FeatureVectorLoaderInvalidFilePath.value)
        AssertionConcern.assertListItemsIsOfType(dropColumns, (int, float),
                                                 ErrorMsg.FeatureVectorLoaderInvalidDropColumnOption.value)

        features, numColumnsLeft = self._loadFeaturesFromCsv(filePath, dropColumns)

        if numColumnsLeft == 11:
            return self._initiateFeatureVectorForSVM(features)
        if numColumnsLeft == 13:
            return self._initiateFeatureVectorForNaiveBayesAndDecisionTree(features)

        raise IndexError(ErrorMsg.FeatureVectorLoaderInvalidCSVLength.value)

    def _loadFeaturesFromCsv(self, filePath: str, dropColumn: list[int | float]) -> tuple[list[list[Any]], int]:
        df: pd.DataFrame = pd.read_csv(filePath, header=None)
        # Remove duplicates and sort descending so dropping columns doesn't affect subsequent indexes
        unique_indexes = sorted(set(int(i) for i in dropColumn), reverse=True)

        for colIndex in unique_indexes:
            if colIndex < 0 or colIndex >= df.shape[1]:
                raise IndexError(ErrorMsg.FeatureVectorLoaderDropColOutOfBounds.value)
            df = df.drop(df.columns[colIndex], axis=1)

        data: list[list[Any]] = df.values.tolist()
        numColumnsLeft: int = df.shape[1]

        return data, numColumnsLeft

    def initiateFeatureVectorsAndTargetFromCsv(self, filePath: str, dropColumns: list[int | float],
                                               targetColumn: int | float) -> tuple[
        list[FeatureVector], list[Any]]:
        AssertionConcern.assertIsType(filePath, str, ErrorMsg.FeatureVectorLoaderInvalidFilePath.value)
        AssertionConcern.assertListItemsIsOfType(dropColumns, (int, float),
                                                 ErrorMsg.FeatureVectorLoaderInvalidDropColumnOption.value)
        AssertionConcern.assertIsType(targetColumn, (int, float),
                                      ErrorMsg.FeatureVectorLoaderInvalidTargetColumnOption.value)

        features, numColumnsLeft, targets = self._loadFeaturesAndTargetFromCsv(filePath, dropColumns, targetColumn)


        if numColumnsLeft == 11:
            return self._initiateFeatureVectorForSVM(features), targets
        if numColumnsLeft == 13:
            return self._initiateFeatureVectorForNaiveBayesAndDecisionTree(features), targets

        raise IndexError(ErrorMsg.FeatureVectorLoaderInvalidCSVLength.value)

    def _loadFeaturesAndTargetFromCsv(self,
                                      filePath: str,
                                      dropColumns: list[int | float],
                                      targetColumn: int | float
                                      ) -> tuple[list[list], int, list[Any]]:
        df: pd.DataFrame = pd.read_csv(filePath, header=None)
        if targetColumn < 0 or targetColumn >= df.shape[1]:
            raise IndexError(ErrorMsg.FeatureVectorLoaderTargetColOutOfBounds.value)

        target: list[Any] = df.iloc[:, targetColumn].tolist()

        # Prepare columns to drop (including target column)
        all_drop_indexes = set(int(i) for i in dropColumns)
        all_drop_indexes.add(targetColumn)
        unique_indexes = sorted(all_drop_indexes, reverse=True)

        for colIndex in unique_indexes:
            if colIndex < 0 or colIndex >= df.shape[1]:
                raise IndexError(ErrorMsg.FeatureVectorLoaderDropColOutOfBounds.value)
            df = df.drop(df.columns[colIndex], axis=1)

        data: list[list[Any]] = df.values.tolist()
        numColumnsLeft: int = df.shape[1]
        return data, numColumnsLeft, target

    def _initiateFeatureVectorForSVM(self, features: list[list]) -> list[FeatureVector]:
        featureVectors: list[FeatureVector] = []

        for feature in features:
            featureVector: FeatureVector = FeatureVector(feature[0], None, feature[1], feature[2], feature[3], None,
                                                         feature[4], feature[5],
                                                         feature[6], feature[7], feature[8], feature[9], feature[10])
            featureVectors.append(featureVector)

        return featureVectors

    def _initiateFeatureVectorForNaiveBayesAndDecisionTree(self, features: list[list]) -> list[FeatureVector]:
        featureVectors: list[FeatureVector] = []

        for feature in features:
            featureVector: FeatureVector = FeatureVector(feature[0], feature[1], feature[2], feature[3],
                                                         feature[4], feature[5],
                                                         feature[6], feature[7], feature[8], feature[9], feature[10],
                                                         feature[11], feature[12])
            featureVectors.append(featureVector)

        return featureVectors
