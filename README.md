# 🩺 AI-Based Healthcare Symptom Clustering and Disease Recommendation System

## 📌 Overview

This project is an AI-powered healthcare analytics system that groups diseases based on symptom patterns and recommends possible diseases for new patients using unsupervised machine learning.

The system analyzes symptom data, discovers hidden disease groups using clustering, and predicts the most likely medical conditions based on symptom similarity.

---

## 🚀 Features

* Disease grouping using K-Means Clustering
* Dimensionality reduction using PCA
* Disease recommendation using Cosine Similarity
* Interactive Symptom Checker
* Medical Condition Group Prediction
* Disease Match Percentage Calculation
* CSV Upload Support for Batch Predictions
* Cluster Visualization using PCA
* Modern Healthcare Dashboard UI

---

## 🏗️ Machine Learning Pipeline

### 1. Data Preprocessing

* Cleaned healthcare symptom dataset
* Binary symptom encoding (0 = absent, 1 = present)
* Feature scaling using StandardScaler

### 2. Dimensionality Reduction

* Principal Component Analysis (PCA)
* Reduced high-dimensional symptom space
* Improved clustering performance and visualization

### 3. Clustering

* K-Means Clustering
* 26 Medical Condition Groups discovered
* Similar diseases automatically grouped together

### 4. Disease Recommendation

* Cosine Similarity
* Finds diseases with symptom patterns closest to the patient
* Returns disease match percentages

---

## 📊 Technologies Used

| Technology          | Purpose                  |
| ------------------- | ------------------------ |
| Python              | Core Development         |
| Pandas              | Data Processing          |
| NumPy               | Numerical Computation    |
| Scikit-Learn        | Machine Learning         |
| PCA                 | Dimensionality Reduction |
| K-Means             | Disease Clustering       |
| Cosine Similarity   | Disease Recommendation   |
| Matplotlib          | Visualization            |
| Flask               | Backend                  |
| HTML/CSS/JavaScript | Frontend                 |

---

## 📂 Project Structure

```text
Disease-Symptom-Pattern/
│
├── models/
│   ├── kmeans_model.pkl
│   ├── pca_model.pkl
│   ├── scaler.pkl
│   └── symptom_columns.pkl
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── Disease-Symptom-Pattern-Discovery.ipynb
├── app.py
├── requirements.txt
├── README.md
│
└── .gitignore
```

---

## 📈 Medical Condition Groups

The model automatically discovers 26 medical condition groups including:

* Respiratory & Lung Disorders
* Heart & Cardiac Disorders
* Neurological Disorders
* Eye & Vision Disorders
* Skin & Dermatological Disorders
* Urinary Disorders
* Dental & Oral Disorders
* Gastrointestinal Disorders
* Pregnancy & Reproductive Disorders
* Psychiatric & Behavioral Disorders
* Musculoskeletal Disorders
* Ear & Hearing Disorders

---

## 🔍 Example Workflow

Patient Symptoms:

* Fever
* Cough
* Wheezing
* Shortness of Breath

↓

Predicted Medical Group:

Respiratory & Lung Disorders

↓

Possible Diseases:

* Pneumonia
* Bronchitis
* Asthma

↓

Disease Match Percentage:

* Pneumonia (48%)
* Bronchitis (32%)
* Asthma (20%)

---

## 📸 Visualization

The project includes:

* PCA Cluster Visualization
* Disease Cluster Analysis
* Symptom Distribution Charts
* Medical Condition Group Explorer

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/SATYA012904/Disease-Symptom-Pattern-Discovery/edit/main/README.md

```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 🎯 Applications

* Healthcare Analytics
* Disease Pattern Discovery
* Clinical Decision Support
* Symptom-Based Disease Recommendation
* Medical Research
* Educational Demonstrations

---

## 🔮 Future Improvements

* Deep Learning-based Disease Prediction
* Explainable AI (XAI)
* Real-time Patient Monitoring
* Medical Report Generation
* Voice-Based Symptom Input
* Chatbot Integration
* Cloud Deployment

---

## 👨‍💻 Author

Satyabrata Sahu

B.Tech Computer Science Engineering

Machine Learning | Data Science | Artificial Intelligence

---

## 📜 License

This project is developed for educational and research purposes.
