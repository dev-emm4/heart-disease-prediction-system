from enum import Enum


class ErrorMsg(Enum):
    InvalidFeatureVector = "Invalid feature vector provided"
    InvalidPredictionModel = "Invalid prediction model provided"
    InvalidPredictionResult = "Invalid prediction result provided"
    InvalidPerformanceResult = "Invalid performance result provided"
    ModelPerformanceCalculatorInvalidPredictionModel = "Invalid prediction model provided at ModelPerformanceCalculator"
    ModelPerformanceCalculatorFeatureVectors = "Invalid FeatureVector provided at ModelPerformanceCalculator"
    ModelPerformanceCalculatorTarget = "Invalid Target provided at ModelPerformanceCalculator"
    PerformanceResultInvalidModelName = "Invalid model name provided at Performance Result"
    PerformanceResultInvalidRecall = "Invalid recall provided at Performance Result"
    PerformanceResultInvalidAccuracy = "Invalid Accuracy provided at Performance Result"
    PerformanceResultInvalidPrecision = "Invalid Precision provided at Performance Result"
    PredictionModelInvalidFeatureVector = "Invalid FeatureVector Provided at PredictionModel"
    FeatureVectorInvalidFeatures = "Invalid Features at FeatureVector"
    PredictionResultInvalidId = "Invalid ID provided at PredictionResult"
    PredictionResultInvalidModelName = "Invalid modelName provided at PredictionResult"
    PredictionResultInvalidFeatureVector = "Invalid featureVector provided at PredictionResult"
    PredictionResultInvalidDiag = "Invalid diagnosis provided at PredictionResult"
    PredictionResultInvalidTimeStamp = "Invalid timestamp provided at PredictionResult"
    PredictionResultRepoInvalidPredictionResult = "Invalid Prediction Result at PredictionResultRepo"
    PredictionResultRepoInvalidPredictionId = "Invalid Prediction Result ID at PredictionResultRepo"
    PredictionResultRepoInvalidPredictionModelName = "Invalid Prediction Result modelName at PredictionResultRepo"
    PredictionResultRepoInvalidPageSize = "Invalid page size at PredictionResultRepo"
    PredictionResultRepoInvalidPage = "Invalid page at PredictionResultRepo"
    FeatureVectorLoaderInvalidFilePath = "Invalid file path at FeatureVectorLoader"
    FeatureVectorLoaderInvalidDropColumnOption = "Invalid drop column option at FeatureVectorLoader"
    FeatureVectorLoaderInvalidCSVLength = "Invalid CSV length at FeatureVectorLoader"
    FeatureVectorLoaderDropColOutOfBounds = "drop column is out of bound at FeatureVectorLoader"
    FeatureVectorLoaderTargetColOutOfBounds = "Target column is out of bound at FeatureVectorLoader"
    FeatureVectorLoaderInvalidTargetColumnOption = "Invalid Target column option at FeatureVectorLoader"
    PredictionServiceInvalidModelName = "Invalid modelName provided at PredictionService"
    PredictionServiceInvalidFeatureVector = "Invalid FeatureVector provided at PredictionService"
    PredictionServiceInvalidTarget = "Invalid target provided at PredictionService"
    PredictionServiceInvalidPredictionId = "Invalid prediction ID provided at PredictionService"
    PredictionServiceInvalidPage = "Invalid page provided at PredictionService"
    PredictionServiceInvalidPageSize = "Invalid page size provided at PredictionService"
    PredictionControllerInvalidModelName = "Invalid modelName provided at PredictionController"
    PredictionControllerInvalidFeatureJson = "Invalid Feature JSON provided at PredictionController"
    PredictionControllerInvalidFilePath = "Invalid file path provided at PredictionController"
    PredictionControllerInvalidDropColOption = "Invalid drop column option provided at PredictionController"
    PredictionControllerInvalidTargetColOption = "Invalid Target column option provided at PredictionController"
    PredictionControllerInvalidPredictionId = "Invalid Prediction ID provided at PredictionController"
    PredictionControllerInvalidPage = "Invalid page provided at PredictionController"
    PredictionControllerInvalidPageSize = "Invalid page size provided at PredictionController"

    @staticmethod
    def predictionControllerSpecificErrorMsg() -> list:
        return [
            ErrorMsg.PredictionControllerInvalidModelName.value,
            ErrorMsg.PredictionControllerInvalidFeatureJson.value,
            ErrorMsg.PredictionControllerInvalidFilePath.value,
            ErrorMsg.PredictionControllerInvalidDropColOption.value,
            ErrorMsg.PredictionControllerInvalidTargetColOption.value,
            ErrorMsg.PredictionControllerInvalidPredictionId.value,
            ErrorMsg.PredictionControllerInvalidPage.value,
            ErrorMsg.PredictionControllerInvalidPageSize.value,
        ]
