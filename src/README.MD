# 🫀 CardioAI — Heart Disease Prediction System

**Undergraduate Research Project — Kwara State University, August 2023**  
*Analysis of Optimal Features for Heart Disease Prediction Using Machine Learning*

---

## Overview

CardioAI is the software deliverable of a final-year undergraduate research project that investigated whether **filter-based feature selection** improves the predictive performance of supervised machine learning classifiers on clinical heart disease data.

The central research question was: *does reducing a dataset to its most statistically informative features lead to better model performance, and does that hold consistently across different classifier types?*

The short answer — it depends on the model. Identifying exactly *when* and *why* was the point of the research.

---

## Research Summary

The project trained three supervised classifiers on the [UCI Heart Disease Dataset](https://archive.ics.uci.edu/ml/datasets/heart+disease) (303 patient records, Cleveland Clinic Foundation) and applied chi-square (χ²) filter-based feature selection to determine the optimal feature subset for each model.

### How the Feature Selection Worked

For each of the 13 clinical features in the dataset, a chi-square statistic was computed against the target variable (presence or absence of heart disease). The χ² score measures how strongly a feature's distribution is associated with the target class — a higher score indicates a stronger dependency, meaning the feature is more likely to carry genuine predictive signal. Features with low scores are approximately independent of the outcome and may introduce noise.

Features were ranked by their χ² scores and removed iteratively from the weakest upward. Each model was retrained and evaluated after every removal, and the subset that yielded peak performance was retained as that model's optimal feature set.

### Results

| Model | Optimal Feature Set | Finding |
|---|---|---|
| **Naïve Bayes** | All 13 features | Accuracy declined with any feature removed |
| **SVM** | 11 features (`sex` and `fbs` excluded) | Removing the two weakest features improved classification |
| **Decision Tree** | All 13 features | Accuracy declined with any feature removed |

The SVM result was the most notable finding. `fbs` (fasting blood sugar > 120 mg/dL) and `sex` had the weakest chi-square associations with the target in this dataset. SVM, which is sensitive to noisy decision boundaries, improved measurably once those features were removed. Naïve Bayes and Decision Tree, on the other hand, benefited from the full feature set — feature reduction was a net negative for both.

---

## Dataset

The UCI Heart Disease dataset contains 13 clinical attributes:

| Feature | Description |
|---|---|
| `age` | Patient age in years |
| `sex` | Biological sex (1 = Male, 0 = Female) |
| `cp` | Chest pain type (1 = Typical angina, 2 = Atypical angina, 3 = Non-anginal pain, 4 = Asymptomatic) |
| `trestbps` | Resting blood pressure (mm Hg) |
| `chol` | Serum cholesterol (mg/dL) |
| `fbs` | Fasting blood sugar > 120 mg/dL (1 = Yes, 0 = No) |
| `restecg` | Resting ECG results (0 = Normal, 1 = ST-T wave abnormality, 2 = Left ventricular hypertrophy) |
| `thalach` | Maximum heart rate achieved (bpm) |
| `exang` | Exercise-induced angina (1 = Yes, 0 = No) |
| `oldpeak` | ST depression induced by exercise relative to rest |
| `slope` | Slope of peak exercise ST segment (1 = Upsloping, 2 = Flat, 3 = Downsloping) |
| `ca` | Number of major vessels coloured by fluoroscopy (0–3) |
| `thal` | Thalassemia type (3 = Normal, 6 = Fixed defect, 7 = Reversable defect) |

---

## The Application

CardioAI wraps the trained models in a desktop interface built with Python and Tkinter. All three models are exposed through the same UI, each configured to use its optimal feature set automatically.

### Features

**Single Prediction** — Enter a patient's clinical measurements to receive an immediate heart disease prediction, along with the full feature vector and a unique record ID. When SVM is selected, the `sex` and `fbs` fields are automatically disabled since the model was not trained on those features.

**Bulk Prediction** — Upload a CSV file of patient records to run predictions across all rows at once. Results are displayed in a resizable paginated table; clicking any row reveals the full feature vector used for that prediction.

**Model Evaluation** — Supply a labelled CSV (features + ground-truth target column) to calculate accuracy, precision, and recall for any of the three models against that test set.

**Prediction History** — A paginated, filterable log of all stored predictions. Records can be individually inspected, deleted, or cleared in bulk.

**Statistics** — A usage dashboard showing the total prediction count and a proportional breakdown by model.

---

## Project Structure

```
project/
├── main.py                        # Application entry point
├── controller/
│   └── PredictionController.py    # ML inference and business logic
└── UI/
    ├── app.py                     # Root window, navigation, global styling
    ├── theme.py                   # Centralised design tokens (colours, fonts, dimensions)
    ├── components/                # Reusable UI widgets
    │   ├── nav_sidebar.py
    │   ├── feature_form.py
    │   ├── data_table.py
    │   ├── card.py
    │   └── status_bar.py
    ├── views/                     # One file per screen
    │   ├── single_prediction_view.py
    │   ├── bulk_prediction_view.py
    │   ├── performance_view.py
    │   ├── history_view.py
    │   └── statistics_view.py
    └── utils/
        ├── validators.py
        └── formatters.py
```

---

## Getting Started

**Prerequisites:** Python 3.10 or later. Tkinter is included with Python on Windows and macOS. On Linux:

```bash
sudo apt install python3-tk
```

**Installation:**

```bash
git clone https://github.com/your-username/cardioai.git
cd cardioai
pip install -r requirements.txt
python main.py
```

If `PredictionController` is not found, the application will start in demo mode using a built-in stub controller — useful for exploring the interface without the ML backend.

### CSV Format

For bulk prediction and model evaluation, the CSV should have columns in this order:

```
age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal[, target]
```

The optional `target` column (0 = no disease, 1 = disease present) is required for evaluation. For bulk prediction, exclude it using the *Drop Columns* field (typically column index `13`).

---

## Tech Stack

- **Python 3.10+**
- **Tkinter** — UI framework
- **scikit-learn** — Machine learning models
- **UCI Heart Disease Dataset** — Cleveland Clinic Foundation

---

## License

This project is licensed under the MIT License — see [LICENSE](./LICENSE) for details.

---

*Kwara State University · Department of Computer Science · 2023*