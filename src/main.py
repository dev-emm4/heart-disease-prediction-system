import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import HeartApp

try:
    from controller import PredictionController
    from application import PredictionApplicationService
    from infrastructure import DatabaseConnection
    from infrastructure.persistence import SQLitePredictionResultRepository
    from domain.predictionModel import PredictionResultRepository
    from infrastructure import FeatureVectorLoader

    databaseConnection: DatabaseConnection = DatabaseConnection()
    repo: PredictionResultRepository = SQLitePredictionResultRepository(databaseConnection)
    applicationService: PredictionApplicationService = PredictionApplicationService(repo)
    controller = PredictionController(applicationService, FeatureVectorLoader())

except ImportError as e:
    controller = None  # HeartApp will inject _StubController automatically


if __name__ == "__main__":
    app = HeartApp(controller=controller)
    app.run()
