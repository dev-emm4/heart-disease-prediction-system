"""
main.py
───────
Project root launcher.  Place this file alongside controller/ and UI/.

    project/
    ├── main.py          ← this file
    ├── controller/
    │   └── PredictionController.py
    └── UI/
        └── ...

Run with:
    python main.py
"""

import os
import sys

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from UI.app import HeartApp

# ── Import the real controller ────────────────────────────────────────────────
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
    from controller import PredictionController
    from application import PredictionApplicationService
    from infrastructure import DatabaseConnection
    from infrastructure.persistence import SQLitePredictionResultRepository
    from domain.predictionModel import PredictionResultRepository
    from infrastructure import FeatureVectorLoader

    controller = None  # HeartApp will inject _StubController automatically

# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = HeartApp(controller=controller)
    app.run()
