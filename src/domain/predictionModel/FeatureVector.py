from common.AssertionConcern import AssertionConcern
from common.ErrorMsg import ErrorMsg


class FeatureVector:
    def __init__(self, age: float, sex: float, cp: float, trestbps: float, chol: float, fbs: float, restecg: float,
                 thalach: float, exang: float, oldpeak: float, slope: float, ca: float, thal: float):
        try:
            self._age: float = float(age)
            if sex is not None:
                self._sex: float = float(sex)
            self._cp: float = float(cp)
            self._trestbps: float = float(trestbps)
            self._chol: float = float(chol)
            if fbs is not None:
                self._fbs: float = float(fbs)
            self._restecg: float = float(restecg)
            self._thalach: float = float(thalach)
            self._exang: float = float(exang)
            self._oldpeak: float = float(oldpeak)
            self._slope: float = float(slope)
            self._ca: float = float(ca)
            self._thal: float = float(thal)

        except (ValueError, TypeError):
            AssertionConcern.assertTrue(False, ErrorMsg.FeatureVectorInvalidFeatures.value)

    def getOptimizedFeaturesForNaiveBayesAndDecisionTree(self) -> list[float]:
        AssertionConcern.assertTrue((hasattr(self, "_sex") and hasattr(self, "_fbs")),
                                    ErrorMsg.FeatureVectorInvalidFeatures.value)
        features: list[float] = [self._age,
                                 self._sex,
                                 self._cp,
                                 self._trestbps,
                                 self._chol,
                                 self._fbs,
                                 self._restecg,
                                 self._thalach,
                                 self._exang,
                                 self._oldpeak,
                                 self._slope,
                                 self._ca,
                                 self._thal, ]

        return features

    def getOptimizedFeaturesForSVM(self) -> list[float]:
        features: list[float] = [self._age,
                                 self._cp,
                                 self._trestbps,
                                 self._chol,
                                 self._restecg,
                                 self._thalach,
                                 self._exang,
                                 self._oldpeak,
                                 self._slope,
                                 self._ca,
                                 self._thal, ]

        return features

    def __str__(self):
        return (f"FeatureVector(age: {self._age}, sex: {getattr(self, '_sex', 'N/A')}, "
                f"cp: {self._cp}, trestbps: {self._trestbps}, chol: {self._chol}, fbs: {getattr(self, '_fbs', 'N/A')}, restecg: {self._restecg}, thalach: {self._thalach}, exang: {self._exang}, oldpeak: {self._oldpeak}, slope: {self._slope}, ca: {self._ca}, thal: {self._thal})")

    def __repr__(self):
        return self.__str__()

    def __json__(self):
        return {
            "age": self._age,
            "sex": getattr(self, "_sex", None),
            "cp": self._cp,
            "trestbps": self._trestbps,
            "chol": self._chol,
            "fbs": getattr(self, "_fbs", None),
            "restecg": self._restecg,
            "thalach": self._thalach,
            "exang": self._exang,
            "oldpeak": self._oldpeak,
            "slope": self._slope,
            "ca": self._ca,
            "thal": self._thal
        }
