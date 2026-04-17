# Heart Disease Prediction System - API Specification

## Table of Contents
1. [Overview](#overview)
2. [Response Format](#response-format)
3. [Status Codes](#status-codes)
4. [Models & Features](#models--features)
5. [Endpoints](#endpoints)
6. [Error Handling](#error-handling)
7. [Examples](#examples)

---

## Overview

This document specifies the API for the **Heart Disease Prediction System**, provided through the `PredictionController` class. The controller manages all interactions between the UI and the prediction engine, supporting single and bulk predictions, model performance evaluation, and prediction history management.

### Key Features
- **Single Predictions**: Predict heart disease for individual patients
- **Bulk Predictions**: Process multiple predictions from CSV files
- **Performance Evaluation**: Calculate model accuracy, precision, and recall on datasets
- **Prediction History**: Store and retrieve prediction results
- **Statistics**: View model usage statistics

### Supported ML Models
- `NaiveBayes`
- `SVM`
- `DecisionTree`

---

## Response Format

All API responses follow a standardized JSON structure:

```json
{
  "status": "success|value error|internal error",
  "message": "<result_data_or_error_message>"
}
```

### Response Structure Details

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | HTTP-like status indicating success or type of error |
| `message` | varies | Result data (object/array) on success, error message (string) on failure |

---

## Status Codes

| Status | Value | Description |
|--------|-------|-------------|
| **success** | `"success"` | Request completed successfully |
| **value error** | `"value error"` | Input validation failed |
| **internal error** | `"internal error"` | Unexpected server error |
| **not found** | `"not found"` | Resource not found (reserved for future use) |

### Error Messages

When an error occurs, the `message` field will contain one of the following:

| Error Message | Cause |
|---------------|-------|
| `"Input provided is invalid"` | Invalid input parameters (wrong type, format, or missing required fields) |
| `"CSV or CSV location is invalid"` | CSV file path invalid, file doesn't exist, or CSV format is incorrect |
| `"Unexpected error encountered"` | Internal server error |

---

## Models & Features

### Supported Models

#### 1. **NaiveBayes**
- Naive Bayes probabilistic classifier
- Requires **all 13 features** to be present in input
- Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal

#### 2. **SVM (Support Vector Machine)**
- Support Vector Machine classifier
- Requires **11 features** (does NOT use: sex, fbs)
- Features: age, cp, trestbps, chol, restecg, thalach, exang, oldpeak, slope, ca, thal
- When sex/fbs are missing, they will be set to `null`

#### 3. **DecisionTree**
- Decision Tree classifier
- Requires **all 13 features** to be present in input
- Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal

### Feature Definitions

All features should be provided as numeric values (float or int). Here's the complete feature list:

| Feature | Type | Abbreviation | Description |
|---------|------|--------------|-------------|
| age | float/int | age | Patient age in years |
| sex | float/int | sex | Patient sex (1 = Male, 0 = Female) |
| cp | float/int | cp | Chest pain type (0-3 indicating different types) |
| trestbps | float/int | trestbps | Resting blood pressure (in mm Hg) |
| chol | float/int | chol | Serum cholesterol level (in mg/dl) |
| fbs | float/int | fbs | Fasting blood sugar > 120 mg/dl (1 = yes, 0 = no) |
| restecg | float/int | restecg | Resting electrocardiographic results (0-2) |
| thalach | float/int | thalach | Maximum heart rate achieved |
| exang | float/int | exang | Exercise-induced angina (1 = yes, 0 = no) |
| oldpeak | float/int | oldpeak | ST depression induced by exercise relative to rest |
| slope | float/int | slope | Slope of the ST segment (0-2) |
| ca | float/int | ca | Number of major vessels colored by fluoroscopy (0-3) |
| thal | float/int | thal | Thalassemia type (0, 1, 2, 3) |

---

## Endpoints

### 1. Make Single Prediction

**Purpose**: Predict heart disease for a single patient based on their features.

**Method**: `makePrediction(modelName: str, featureJson: dict) -> dict`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `modelName` | string | Yes | Name of the model: `"NaiveBayes"`, `"SVM"`, or `"DecisionTree"` |
| `featureJson` | object | Yes | JSON object containing patient features (see Feature Definitions table) |

#### Request Example

```json
{
  "modelName": "NaiveBayes",
  "featureJson": {
    "age": 50.0,
    "sex": 0.0,
    "cp": 2.0,
    "trestbps": 120.0,
    "chol": 200.0,
    "fbs": 0.0,
    "restecg": 1.0,
    "thalach": 130.0,
    "exang": 0.0,
    "oldpeak": 1.0,
    "slope": 1.0,
    "ca": 0.0,
    "thal": 2.0
  }
}
```

#### Response Format

**Success (status: "success")**
```json
{
  "status": "success",
  "message": {
    "Id": "550e8400-e29b-41d4-a716-446655440000",
    "modelName": "NaiveBayes",
    "featureVector": {
      "age": 50.0,
      "sex": 0.0,
      "cp": 2.0,
      "trestbps": 120.0,
      "chol": 200.0,
      "fbs": 0.0,
      "restecg": 1.0,
      "thalach": 130.0,
      "exang": 0.0,
      "oldpeak": 1.0,
      "slope": 1.0,
      "ca": 0.0,
      "thal": 2.0
    },
    "isMalignant": true,
    "timeStamp": "2026-04-17T10:30:00.000000"
  }
}
```

**Error Response (status: "value error")**
```json
{
  "status": "value error",
  "message": "Input provided is invalid"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `Id` | string (UUID) | Unique identifier for the prediction result |
| `modelName` | string | The model used for prediction |
| `featureVector` | object | The input features used for prediction |
| `isMalignant` | boolean | Prediction result (true = disease present, false = disease absent) |
| `timeStamp` | string (ISO 8601) | Timestamp of when the prediction was made |

#### Validation Rules

- `modelName` must be exactly: `"NaiveBayes"`, `"SVM"`, or `"DecisionTree"`
- `featureJson` must be a valid JSON object
- For **NaiveBayes** and **DecisionTree**: all 13 features must be present
- For **SVM**: features should be present except sex and fbs (which will be set to null)
- All feature values must be numeric (int or float)
- Missing or null feature values will cause a `"value error"` response

#### Possible Errors

| Error Type | Cause |
|------------|-------|
| `"value error"` | Invalid model name, non-dict featureJson, missing features, or non-numeric feature values |
| `"internal error"` | Unexpected server error during prediction |

---

### 2. Make Bulk Predictions

**Purpose**: Perform predictions on multiple patients from a CSV file.

**Method**: `makeBulkPredictions(modelName: str, filePath: str, dropColumn: list[int | float]) -> dict`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `modelName` | string | Yes | Model name: `"NaiveBayes"`, `"SVM"`, or `"DecisionTree"` |
| `filePath` | string | Yes | Absolute path to the CSV file |
| `dropColumn` | array of numbers | Yes | List of column indices (0-based) to exclude from processing (e.g., [13] to exclude last column) |

#### CSV File Format Requirements

- **Format**: Standard CSV file with headers
- **Column Order**: Must match FeatureVectorAttributes in order (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, ...)
- **Data Type**: All values must be numeric
- **Rows**: Must have at least 1 data row (excluding header)

#### Example CSV Structure
```
age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target
50,0,2,120,200,0,1,130,0,1,1,0,2,0
63,1,1,145,233,1,2,150,0,2.3,0,0,1,1
```

#### Request Example

```json
{
  "modelName": "NaiveBayes",
  "filePath": "/path/to/data.csv",
  "dropColumn": [13]
}
```

#### Response Format

**Success (status: "success")**
```json
{
  "status": "success",
  "message": [
    {
      "Id": "550e8400-e29b-41d4-a716-446655440000",
      "modelName": "NaiveBayes",
      "featureVector": {
        "age": 50.0,
        "sex": 0.0,
        "cp": 2.0,
        "trestbps": 120.0,
        "chol": 200.0,
        "fbs": 0.0,
        "restecg": 1.0,
        "thalach": 130.0,
        "exang": 0.0,
        "oldpeak": 1.0,
        "slope": 1.0,
        "ca": 0.0,
        "thal": 2.0
      },
      "isMalignant": false,
      "timeStamp": "2026-04-17T10:30:00.000000"
    },
    {
      "Id": "650e8400-e29b-41d4-a716-446655440001",
      "modelName": "NaiveBayes",
      "featureVector": {...},
      "isMalignant": true,
      "timeStamp": "2026-04-17T10:30:01.000000"
    }
  ]
}
```

**Error Response (status: "value error")**
```json
{
  "status": "value error",
  "message": "Input provided is invalid"
}
```

**CSV Error Response**
```json
{
  "status": "value error",
  "message": "CSV or CSV location is invalid"
}
```

#### Response Fields

- Returns an array of prediction results (same structure as single prediction)
- Each row in the CSV produces one prediction result

#### Validation Rules

- `modelName` must be valid
- `filePath` must be a valid, accessible file path
- CSV file must be readable and properly formatted
- `dropColumn` must be an array of numeric values
- After dropping specified columns, remaining columns must match model requirements:
  - **NaiveBayes**: exactly 13 features
  - **DecisionTree**: exactly 13 features
  - **SVM**: exactly 11 features

#### Possible Errors

| Error Type | Cause |
|------------|-------|
| `"value error"` | Invalid model name, invalid file path, invalid dropColumn type, or wrong feature count |
| `"value error"` (CSV message) | File not found, CSV parsing error, or invalid CSV format |
| `"internal error"` | Unexpected server error |

---

### 3. Calculate Model Performance

**Purpose**: Evaluate model performance (accuracy, precision, recall) on a test dataset.

**Method**: `calculatePerformance(modelName: str, filePath: str, dropColumn: list[int | float], targetColumn: int | float) -> dict`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `modelName` | string | Yes | Model name: `"NaiveBayes"`, `"SVM"`, or `"DecisionTree"` |
| `filePath` | string | Yes | Absolute path to the CSV file with target labels |
| `dropColumn` | array of numbers | Yes | List of column indices to exclude from features (typically includes target column) |
| `targetColumn` | number | Yes | Column index (0-based) containing the target labels (disease presence: 1 or 0) |

#### CSV File Format Requirements

- Must include all feature columns plus a target column
- Target column should contain binary values (0 = no disease, 1 = disease present)
- Example: columns 0-12 are features, column 13 is target

#### Request Example

```json
{
  "modelName": "DecisionTree",
  "filePath": "/path/to/test_data.csv",
  "dropColumn": [13],
  "targetColumn": 13
}
```

#### Response Format

**Success (status: "success")**
```json
{
  "status": "success",
  "message": {
    "modelName": "DecisionTree",
    "recall": 0.8523,
    "accuracy": 0.8745,
    "precision": 0.8612
  }
}
```

**Error Response (status: "value error")**
```json
{
  "status": "value error",
  "message": "Input provided is invalid"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `modelName` | string | The model evaluated |
| `recall` | float | Recall score (0.0-1.0) - True Positive Rate |
| `accuracy` | float | Accuracy score (0.0-1.0) - Overall correctness |
| `precision` | float | Precision score (0.0-1.0) - Positive prediction accuracy |

#### Metric Definitions

- **Accuracy**: (TP + TN) / (TP + TN + FP + FN) - Overall correctness
- **Precision**: TP / (TP + FP) - How many positive predictions are actually correct
- **Recall**: TP / (TP + FN) - How many actual positives were identified

#### Validation Rules

- `modelName` must be valid
- `filePath` must be valid and accessible
- `dropColumn` must be array of numeric values
- `targetColumn` must be numeric and valid
- Feature columns must match model requirements after dropping specified columns
- Target column must contain only 0 or 1 values

#### Possible Errors

| Error Type | Cause |
|------------|-------|
| `"value error"` | Invalid parameters or wrong feature count |
| `"value error"` (CSV message) | File not found, CSV parsing error, or invalid format |
| `"internal error"` | Unexpected server error |

---

### 4. Get All Predictions

**Purpose**: Retrieve all stored prediction results from the database.

**Method**: `getAllPredictions() -> dict`

#### Request Parameters

None

#### Response Format

**Success (status: "success")**
```json
{
  "status": "success",
  "message": [
    {
      "Id": "550e8400-e29b-41d4-a716-446655440000",
      "modelName": "NaiveBayes",
      "featureVector": {...},
      "isMalignant": true,
      "timeStamp": "2026-04-17T10:30:00.000000"
    },
    {
      "Id": "650e8400-e29b-41d4-a716-446655440001",
      "modelName": "SVM",
      "featureVector": {...},
      "isMalignant": false,
      "timeStamp": "2026-04-17T10:31:00.000000"
    }
  ]
}
```

**Empty Result (status: "success")**
```json
{
  "status": "success",
  "message": []
}
```

#### Response Fields

- Returns an array of all prediction results stored in the database
- Empty array if no predictions have been made yet
- Each item has the same structure as single prediction response

#### Possible Errors

| Error Type | Cause |
|------------|-------|
| `"internal error"` | Database connection error |

---

### 5. Get Predictions by Model

**Purpose**: Retrieve all predictions made with a specific model.

**Method**: `getPredictionsByModel(modelName: str) -> dict`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `modelName` | string | Yes | Model name: `"NaiveBayes"`, `"SVM"`, or `"DecisionTree"` |

#### Request Example

```json
{
  "modelName": "SVM"
}
```

#### Response Format

**Success (status: "success")**
```json
{
  "status": "success",
  "message": [
    {
      "Id": "550e8400-e29b-41d4-a716-446655440000",
      "modelName": "SVM",
      "featureVector": {...},
      "isMalignant": true,
      "timeStamp": "2026-04-17T10:30:00.000000"
    },
    {
      "Id": "650e8400-e29b-41d4-a716-446655440001",
      "modelName": "SVM",
      "featureVector": {...},
      "isMalignant": false,
      "timeStamp": "2026-04-17T10:31:00.000000"
    }
  ]
}
```

**Empty Result (status: "success")**
```json
{
  "status": "success",
  "message": []
}
```

#### Validation Rules

- `modelName` must be exactly: `"NaiveBayes"`, `"SVM"`, or `"DecisionTree"`

#### Possible Errors

| Error Type | Cause |
|------------|-------|
| `"value error"` | Invalid model name |
| `"internal error"` | Database error |

---

### 6. Delete Prediction

**Purpose**: Delete a specific prediction result from the database.

**Method**: `deletePrediction(predictionId: str) -> dict`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `predictionId` | string | Yes | UUID of the prediction to delete (must be valid UUID format) |

#### Request Example

```json
{
  "predictionId": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Response Format

**Success - Prediction Deleted (status: "success")**
```json
{
  "status": "success",
  "message": true
}
```

**Success - Prediction Not Found (status: "success")**
```json
{
  "status": "success",
  "message": false
}
```

**Error - Invalid UUID (status: "value error")**
```json
{
  "status": "value error",
  "message": "Input provided is invalid"
}
```

#### Response Fields

| Value | Meaning |
|-------|---------|
| `true` | Prediction was found and successfully deleted |
| `false` | Prediction with given ID was not found (no error, nothing to delete) |

#### Validation Rules

- `predictionId` must be a valid UUID string format
- Valid UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

#### Possible Errors

| Error Type | Cause |
|------------|-------|
| `"value error"` | Invalid UUID format or null value |
| `"internal error"` | Database error |

---

### 7. Get Statistics

**Purpose**: Retrieve usage statistics for all models.

**Method**: `getStatistics() -> dict`

#### Request Parameters

None

#### Response Format

**Success (status: "success")**
```json
{
  "status": "success",
  "message": {
    "stat": {
      "NaiveBayes": 25,
      "SVM": 18,
      "DecisionTree": 32
    },
    "totalCount": 75
  }
}
```

**Empty Statistics (status: "success")**
```json
{
  "status": "success",
  "message": {
    "stat": {},
    "totalCount": 0
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `stat` | object | Object where keys are model names and values are prediction counts |
| `totalCount` | integer | Total number of predictions made with all models |

#### Details

- `stat` is an object containing a count for each model that has been used
- If a model hasn't been used yet, it won't appear in the `stat` object
- `totalCount` is the sum of all predictions across all models

#### Possible Errors

| Error Type | Cause |
|------------|-------|
| `"internal error"` | Database error |

---

## Error Handling

### Error Response Structure

All error responses follow this format:

```json
{
  "status": "<error_type>",
  "message": "<error_message>"
}
```

### Error Classification

#### Validation Errors (status: "value error")
- **Message**: `"Input provided is invalid"`
- **When**: Parameter validation fails (wrong type, format, missing required fields)
- **Action**: Check request parameters against API specification

#### CSV/File Errors (status: "value error")
- **Message**: `"CSV or CSV location is invalid"`
- **When**: File not found, can't be read, or CSV format is invalid
- **Action**: Verify file path and CSV format

#### Internal Errors (status: "internal error")
- **Message**: `"Unexpected error encountered"`
- **When**: Unexpected server-side error occurs
- **Action**: Check server logs and retry request

### Common Causes and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Input provided is invalid" | Wrong model name | Use exactly: "NaiveBayes", "SVM", or "DecisionTree" |
| "Input provided is invalid" | Missing features | Ensure all required features are present in featureJson |
| "Input provided is invalid" | Wrong data type | Ensure all feature values are numbers (int/float) |
| "CSV or CSV location is invalid" | File doesn't exist | Verify file path is correct and file exists |
| "CSV or CSV location is invalid" | Wrong column count | Check dropColumn values don't exclude required features |
| "CSV or CSV location is invalid" | CSV parsing error | Ensure CSV is properly formatted with headers |

---

## Examples

### Complete Workflow Example

#### Step 1: Make a Single Prediction

```python
# Request
request = {
    "modelName": "NaiveBayes",
    "featureJson": {
        "age": 50.0,
        "sex": 0.0,
        "cp": 2.0,
        "trestbps": 120.0,
        "chol": 200.0,
        "fbs": 0.0,
        "restecg": 1.0,
        "thalach": 130.0,
        "exang": 0.0,
        "oldpeak": 1.0,
        "slope": 1.0,
        "ca": 0.0,
        "thal": 2.0
    }
}

# Response (Success)
response = {
    "status": "success",
    "message": {
        "Id": "550e8400-e29b-41d4-a716-446655440000",
        "modelName": "NaiveBayes",
        "featureVector": {...},
        "isMalignant": false,
        "timeStamp": "2026-04-17T10:30:00.000000"
    }
}
```

#### Step 2: Make Bulk Predictions from CSV

```python
# Request
request = {
    "modelName": "NaiveBayes",
    "filePath": "/home/user/data/patients.csv",
    "dropColumn": [13]  # Drop target column
}

# Response (Success)
response = {
    "status": "success",
    "message": [
        {"Id": "...", "modelName": "NaiveBayes", ...},
        {"Id": "...", "modelName": "NaiveBayes", ...},
        # ... more predictions
    ]
}
```

#### Step 3: Evaluate Model Performance

```python
# Request
request = {
    "modelName": "NaiveBayes",
    "filePath": "/home/user/data/test_patients.csv",
    "dropColumn": [13],
    "targetColumn": 13
}

# Response (Success)
response = {
    "status": "success",
    "message": {
        "modelName": "NaiveBayes",
        "recall": 0.8523,
        "accuracy": 0.8745,
        "precision": 0.8612
    }
}
```

#### Step 4: Get Statistics

```python
# Request (no parameters)

# Response
response = {
    "status": "success",
    "message": {
        "stat": {
            "NaiveBayes": 1025,
            "SVM": 500,
            "DecisionTree": 750
        },
        "totalCount": 2275
    }
}
```

#### Step 5: Retrieve All Predictions

```python
# Request (no parameters)

# Response
response = {
    "status": "success",
    "message": [
        {"Id": "...", "modelName": "NaiveBayes", ...},
        {"Id": "...", "modelName": "SVM", ...},
        # ... all predictions
    ]
}
```

### Error Handling Example

```python
# Request with invalid model name
request = {
    "modelName": "LinearRegression",  # Invalid model
    "featureJson": {...}
}

# Response (Error)
response = {
    "status": "value error",
    "message": "Input provided is invalid"
}
```

---

## Implementation Notes for UI Developers

### 1. Response Handling
- Always check the `status` field first to determine success or error
- On success, parse `message` according to the endpoint
- On error, display the `message` to the user

### 2. Data Validation
- Validate all inputs before sending requests (model name, feature types, ranges)
- Ensure CSV files are properly formatted before upload
- Validate UUID format before deletion requests

### 3. Feature Input
- Support both integer and float input for all features
- Provide UI validation for numeric values
- Consider providing input masks or dropdowns for categorical features (sex, cp, etc.)

### 4. Bulk Operations
- For large CSV files, consider showing progress indication
- Validate CSV format before processing
- Consider pagination for large result sets

### 5. Model Selection
- Clearly differentiate models in UI (NaiveBayes, SVM, DecisionTree)
- For SVM, note that sex and fbs are not used (optional inputs)
- Show performance metrics when available

### 6. Persistence
- All predictions are automatically stored in the database
- Use `getAllPredictions()` or `getPredictionsByModel()` to retrieve history
- Use `deletePrediction()` to remove unwanted results

---

## Appendix: Quick Reference

### Models
```
NaiveBayes    → 13 features required
SVM           → 11 features (sex, fbs optional/null)
DecisionTree  → 13 features required
```

### Endpoints Summary
```
makePrediction(modelName, featureJson)
makeBulkPredictions(modelName, filePath, dropColumn)
calculatePerformance(modelName, filePath, dropColumn, targetColumn)
getAllPredictions()
getPredictionsByModel(modelName)
deletePrediction(predictionId)
getStatistics()
```

### Status Values
```
success       → Operation successful
value error   → Input validation failed
internal error → Server error
```

---

**Document Version**: 1.0  
**Last Updated**: April 17, 2026  
**System**: Heart Disease Prediction System

