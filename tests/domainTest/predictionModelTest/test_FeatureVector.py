import os
import sys

from src.domain import ErrorMsg
from src.domain.predictionModel import FeatureVector

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class TestFeatureVector:

    def test_constructor_withValidNumericalValue_create(self):
        fv_int = FeatureVector(
            age=45,
            sex=1,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=0,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )
        assert isinstance(fv_int, FeatureVector)

        fv_float = FeatureVector(
            age=45.5,
            sex=1.0,
            cp=3.2,
            trestbps=130.5,
            chol=250.1,
            fbs=0.0,
            restecg=1.5,
            thalach=150.3,
            exang=1.0,
            oldpeak=2.5,
            slope=2.0,
            ca=0.5,
            thal=3.1
        )
        assert isinstance(fv_float, FeatureVector)

        fv_str = FeatureVector(
            age="45",
            sex="1",
            cp="3",
            trestbps="130",
            chol="250",
            fbs="0",
            restecg="1",
            thalach="150",
            exang="1",
            oldpeak="2",
            slope="2",
            ca="0",
            thal="3"
        )
        assert isinstance(fv_str, FeatureVector)

    def test_constructor_ifSexAndFbsAreNone_create(self):
        fv = FeatureVector(
            age=45,
            sex=None,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=None,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )

        assert isinstance(fv, FeatureVector)

    def test_constructor_withInvalidNumericalValue_throwError(self):
        for i in range(13):
            try:
                FeatureVector(
                    "abc" if i == 0 else 45,
                    "abc" if i == 1 else 1,
                    "abc" if i == 2 else 3,
                    "abc" if i == 3 else 130,
                    "abc" if i == 4 else 250,
                    "abc" if i == 5 else 0,
                    "abc" if i == 6 else 1,
                    "abc" if i == 7 else 150,
                    "abc" if i == 8 else 1,
                    "abc" if i == 9 else 2,
                    "abc" if i == 10 else 2,
                    "abc" if i == 11 else 0,
                    "abc" if i == 12 else 3
                )

                assert False, "Exception Expected"
            except TypeError as e:
                assert str(e) == ErrorMsg.FeatureVectorInvalidFeatures.value

    def test_constructor_withNoneValue_throwError(self):
        for i in range(13):
            try:
                FeatureVector(
                    None if i == 0 else 45,
                    None if i == 1 else 1,
                    None if i == 2 else 3,
                    None if i == 3 else 130,
                    None if i == 4 else 250,
                    None if i == 5 else 0,
                    None if i == 6 else 1,
                    None if i == 7 else 150,
                    None if i == 8 else 1,
                    None if i == 9 else 2,
                    None if i == 10 else 2,
                    None if i == 11 else 0,
                    None if i == 12 else 3
                )

                if i != 1 and i != 5:  # index 1 and 5 represents the index of sex and fbs all which accept None value
                    assert False, "Exception Expected"
            except TypeError as e:
                assert str(e) == ErrorMsg.FeatureVectorInvalidFeatures.value

    def test_getOptimizedFeaturesForNaiveBayesAndDecisionTree_whileFbsAndSexIsNotNone_returnListOfFeatures(self):
        fv = FeatureVector(
            age=45,
            sex=1,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=0,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )
        features = fv.getOptimizedFeaturesForNaiveBayesAndDecisionTree()
        expected_features = [45, 1, 3, 130, 250, 0, 1, 150, 1, 2, 2, 0, 3]
        assert features == expected_features

    def test_getOptimizedFeaturesForNaiveBayesAndDecisionTree_whileFbsAndSexIsNone_throwError(self):
        try:
            fv = FeatureVector(
                age=45,
                sex=None,
                cp=3,
                trestbps=130,
                chol=250,
                fbs=None,
                restecg=1,
                thalach=150,
                exang=1,
                oldpeak=2,
                slope=2,
                ca=0,
                thal=3
            )
            fv.getOptimizedFeaturesForNaiveBayesAndDecisionTree()

            assert False, "Exception Expected"
        except TypeError as e:
            assert str(e) == ErrorMsg.FeatureVectorInvalidFeatures.value

    def test_getOptimizedFeaturesForSVM_whileFbsAndSexIsNotNull_returnListOfFeatures(self):
        fv = FeatureVector(
            age=45,
            sex=1,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=0,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )
        features = fv.getOptimizedFeaturesForSVM()
        expected_features = [45, 3, 130, 250, 1, 150, 1, 2, 2, 0, 3]
        assert features == expected_features

    def test_getOptimizedFeaturesForSVM_whileFbsAndSexIsNone_returnListOfFeatures(self):
        fv = FeatureVector(
            age=45,
            sex=None,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=None,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )
        features = fv.getOptimizedFeaturesForSVM()
        expected_features = [45, 3, 130, 250, 1.0, 150, 1, 2, 2, 0, 3]
        assert features == expected_features

    def test_strAndRepr_withFbsAndSexPresent_returnStringRepresentation(self):
        fv = FeatureVector(
            age=45,
            sex=1,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=0,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )

        expected_str = "FeatureVector(age: 45.0, sex: 1.0, cp: 3.0, trestbps: 130.0, chol: 250.0, fbs: 0.0, restecg: 1.0, thalach: 150.0, exang: 1.0, oldpeak: 2.0, slope: 2.0, ca: 0.0, thal: 3.0)"
        assert str(fv) == expected_str
        assert repr(fv) == expected_str

    def test_strAndRepr_withFbsAndSexAbsent_returnStringRepresentation(self):
        fv = FeatureVector(
            age=45,
            sex=None,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=None,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )

        expected_str = "FeatureVector(age: 45.0, sex: N/A, cp: 3.0, trestbps: 130.0, chol: 250.0, fbs: N/A, restecg: 1.0, thalach: 150.0, exang: 1.0, oldpeak: 2.0, slope: 2.0, ca: 0.0, thal: 3.0)"
        assert str(fv) == expected_str
        assert repr(fv) == expected_str

    def test_json_withFbsAndSexPresent_returnJsonRepresentation(self):
        fv = FeatureVector(
            age=45,
            sex=1,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=0,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )

        expected_json = {
            "age": 45.0,
            "sex": 1.0,
            "cp": 3.0,
            "trestbps": 130.0,
            "chol": 250.0,
            "fbs": 0.0,
            "restecg": 1.0,
            "thalach": 150.0,
            "exang": 1.0,
            "oldpeak": 2.0,
            "slope": 2.0,
            "ca": 0.0,
            "thal": 3.0
        }
        assert fv.__json__() == expected_json

    def test_json_withFbsAndSexAbsent_returnJsonRepresentation(self):
        fv = FeatureVector(
            age=45,
            sex=None,
            cp=3,
            trestbps=130,
            chol=250,
            fbs=None,
            restecg=1,
            thalach=150,
            exang=1,
            oldpeak=2,
            slope=2,
            ca=0,
            thal=3
        )

        expected_json = {
            "age": 45.0,
            "sex": None,
            "cp": 3.0,
            "trestbps": 130.0,
            "chol": 250.0,
            "fbs": None,
            "restecg": 1.0,
            "thalach": 150.0,
            "exang": 1.0,
            "oldpeak": 2.0,
            "slope": 2.0,
            "ca": 0.0,
            "thal": 3.0
        }
        assert fv.__json__() == expected_json
