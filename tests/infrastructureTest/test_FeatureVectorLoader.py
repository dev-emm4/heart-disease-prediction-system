import pytest

from src.common import ErrorMsg
from src.domain.predictionModel import FeatureVector
from src.infrastructure import FeatureVectorLoader


class TestFeatureVectorLoader:
    def setup_method(self):
        self.featureVectorLoader = FeatureVectorLoader()
        self.filePath = "/home/emmanuel/Desktop/Final Heart disease prediction system/code/tests/infrastructureTest/heart.csv"
        self.dropColumn = [0, 1]
        self.lenOfCSV = 1025

    def test_initiateFeatureVectorsFromCsv_withValid13ColumnCsv_loadFeatureVector(self):
        featureVectors: list[FeatureVector] = self.featureVectorLoader.initiateFeatureVectorsFromCsv(self.filePath,
                                                                                                     [13])

        for featureVector in featureVectors:
            assert isinstance(featureVector, FeatureVector)

        assert len(featureVectors) == self.lenOfCSV
        assert featureVectors[0]._sex is not None
        assert featureVectors[0]._fbs is not None

    def test_initiateFeatureVectorsFromCsv_withValid11ColumnCsv_loadFeatureVector(self):
        featureVectors: list[FeatureVector] = self.featureVectorLoader.initiateFeatureVectorsFromCsv(self.filePath,
                                                                                                     [1, 5, 13])

        for featureVector in featureVectors:
            assert isinstance(featureVector, FeatureVector)

        assert len(featureVectors) == self.lenOfCSV
        assert hasattr(featureVectors[0], "_sex") == False
        assert hasattr(featureVectors[0], "_fbs") == False

    def test_initiateFeatureVectorsFromCsv_withInvalidParameters_raiseException(self):
        for i in range(4):
            try:
                if i == 0:
                    self.featureVectorLoader.initiateFeatureVectorsFromCsv(0, [13])
                if i == 1:
                    self.featureVectorLoader.initiateFeatureVectorsFromCsv(self.filePath, 13)
                if i == 2:
                    self.featureVectorLoader.initiateFeatureVectorsFromCsv(None, [13])
                else:
                    self.featureVectorLoader.initiateFeatureVectorsFromCsv(self.filePath, None)

                assert False, "Exception Expected"
            except TypeError as e:
                assert str(e) in (ErrorMsg.FeatureVectorLoaderInvalidFilePath.value,
                                  ErrorMsg.FeatureVectorLoaderInvalidDropColumnOption.value)

    def test_initiateFeatureVectorsFromCsv_ifCsvColumnNotEqualTo11or13_raiseException(self):
        dropCols: list[list] = [
            [],  # csv would be loaded with 14 columns
            [1, 2],  # CSV would be loaded with 12 columns
            [1, 3, 5, 6, 7]  # CSV would be loaded with 9 columns
        ]

        for dropCol in dropCols:
            try:
                self.featureVectorLoader.initiateFeatureVectorsFromCsv(self.filePath, dropCol)

                assert False, "Exception Expected"
            except IndexError as e:
                assert str(e) == ErrorMsg.FeatureVectorLoaderInvalidCSVLength.value

    def test_initiateFeatureVectorsFromCsv_ifDropColIsOutOfBounds_raiseException(self):
        try:
            self.featureVectorLoader.initiateFeatureVectorsFromCsv(self.filePath, [20])

            assert False, "Exception Expected"
        except IndexError as e:
            assert str(e) == ErrorMsg.FeatureVectorLoaderDropColOutOfBounds.value

    def test_initiateFeatureVectorsFromCsv_withInvalidFilePath_raiseException(self):
        with pytest.raises(FileNotFoundError):
            self.featureVectorLoader.initiateFeatureVectorsFromCsv("/invalidPath", [10])

    def test_initiateFeatureVectorsAndTargetsFromCsv_withValid13ColumnCsv_loadFeatureVector(self):
        featureVectors, targets = self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath,
                                                                                                  [], 13)
        for featureVector in featureVectors:
            assert isinstance(featureVector, FeatureVector)

        assert len(featureVectors) == self.lenOfCSV
        assert len(targets) == self.lenOfCSV
        assert featureVectors[0]._sex is not None
        assert featureVectors[0]._fbs is not None

    def test_initiateFeatureVectorsTargetsFromCsv_withValid11ColumnCsv_loadFeatureVector(self):
        featureVectors, targets = self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath,
                                                                                                  [1, 5], 13)
        for featureVector in featureVectors:
            assert isinstance(featureVector, FeatureVector)

        assert len(featureVectors) == self.lenOfCSV
        assert len(targets) == self.lenOfCSV
        assert hasattr(featureVectors[0], "_sex") == False
        assert hasattr(featureVectors[0], "_fbs") == False

    def test_initiateFeatureVectorsAndTargetsFromCsv_withInvalidParameters_raiseException(self):
        for i in range(6):
            try:
                if i == 0:
                    self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(0, [], 13)
                if i == 1:
                    self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath, 13, 13)
                if i == 2:
                    self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath, [], "13")
                if i == 3:
                    self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(None, [], 13)
                if i == 4:
                    self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath, None, 13)
                else:
                    self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath, [], None)

                assert False, "Exception Expected"
            except TypeError as e:
                assert str(e) in (ErrorMsg.FeatureVectorLoaderInvalidFilePath.value,
                                  ErrorMsg.FeatureVectorLoaderInvalidDropColumnOption.value,

                                  ErrorMsg.FeatureVectorLoaderInvalidTargetColumnOption.value)

    def test_initiateFeatureVectorsAndTargetsFromCsv_ifCsvColumnNotEqualTo11or13_raiseException(self):
        dropCols: list[list] = [
            [1, 2, 5],  # CSV would be loaded with 10 columns
            [1, 3, 5, 6, 7]  # CSV would be loaded with 8 columns
        ]

        for dropCol in dropCols:
            try:
                self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath, dropCol, 13)

                assert False, "Exception Expected"
            except IndexError as e:
                assert str(e) == ErrorMsg.FeatureVectorLoaderInvalidCSVLength.value

    def test_initiateFeatureVectorsAndTargetsFromCsv_ifDropColIsOutOfBounds_raiseException(self):
        try:
            self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath, [20], 13)
            assert False, "Exception Expected"
        except IndexError as e:
            assert str(e) == ErrorMsg.FeatureVectorLoaderDropColOutOfBounds.value

    def test_initiateFeatureVectorsAndTargetsFromCsv_ifTargetColumnIsOutOfBounds_raiseException(self):
        try:
            self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv(self.filePath, [], 20)
            assert False, "Exception Expected"
        except IndexError as e:
            assert str(e) == ErrorMsg.FeatureVectorLoaderTargetColOutOfBounds.value

    def test_initiateFeatureVectorsAndTargetsFromCsv_withInvalidFilePath_raiseException(self):
        with pytest.raises(FileNotFoundError):
            self.featureVectorLoader.initiateFeatureVectorsAndTargetFromCsv("/invalidPath", [], 13)
