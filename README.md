# 🩺 MedAI — Disease Symptom Pattern Discovery

An AI-powered healthcare analytics web app that groups diseases by symptom patterns and recommends possible conditions using unsupervised machine learning — deployed live on Render.

🔗 **Live Demo:** [disease-symptom-pattern-discovery.onrender.com](https://disease-symptom-pattern-discovery.onrender.com)

> ⚠️ Hosted on Render's free tier — first load may take 30–60 seconds to wake up.

---

## 📌 Overview

MedAI analyzes patient symptom data, discovers hidden disease clusters using K-Means + PCA, and predicts the most likely medical conditions based on cosine similarity. The system was trained on a dataset of **246,945 patient records** across **329 symptoms** and **13 disease groups**.

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Symptom Checker** | Select symptoms and get AI-predicted disease group + match percentages |
| **CSV Batch Prediction** | Upload a patient CSV for bulk disease prediction |
| **Group Explorer** | Browse all 13 disease groups, their top symptoms and conditions |
| **Sample Datasets** | Built-in 10/15/20 patient demo datasets to test instantly |
| **Clinical Brutalism UI** | Premium dark UI with deep navy, acid-mint, electric-cyan palette |

---

## 🏗️ Machine Learning Pipeline

```
Raw Symptom Data (329 binary features)
        ↓
StandardScaler (feature normalization)
        ↓
PCA (dimensionality reduction)
        ↓
K-Means Clustering (13 disease groups)
        ↓
Cosine Similarity (disease recommendation)
        ↓
Disease Match % (top predictions)
```

### Key Design Decisions
- **Binary encoding** — symptoms are 0/1 (absent/present), stored as `uint8` to minimize memory
- **Stratified cluster cache** — instead of loading the full 78MB DataFrame at runtime, a 0.3MB pre-computed cache of 2,000 stratified samples per cluster is used
- **dtype-aware CSV loading** — `pd.read_csv(..., dtype=dtype_map)` avoids a 616MB float64 intermediate spike during startup

---

## 🩺 Disease Groups (13 Clusters)

| # | Group | Icon |
|---|---|---|
| 0 | Arm & Shoulder Disorders | 💪 |
| 1 | Dental & Oral Disorders | 🦷 |
| 2 | Respiratory & Pulmonary Disorders | 🫁 |
| 3 | Urinary & Prostate Disorders | 💧 |
| 4 | Musculoskeletal & Joint Disorders | 🦴 |
| 5 | Skin Mass & Tumor Disorders | 🔬 |
| 6 | Gynecological & Pregnancy Disorders | 🤱 |
| 7 | Vision & Retinal Disorders | 👁️ |
| 8 | Eye Infection & Conjunctival Disorders | 👁️‍🗨️ |
| 9 | Spine & Nerve Pain Disorders | 🧠 |
| 10 | Gastrointestinal & Metabolic Disorders | 🫃 |
| 11 | Psychiatric & Behavioral Disorders | 🧘 |
| 12 | Skin & Dermatological Disorders | 🩹 |

---

## 🔍 Example Workflow

```
Patient Symptoms: fever, cough, wheezing, shortness of breath
         ↓
Predicted Group: 🫁 Respiratory & Pulmonary Disorders
         ↓
Possible Diseases:
  • Pneumonia       (48%)
  • Bronchitis      (32%)
  • Asthma          (20%)
```

---

## 📂 Project Structure

```
Disease-Symptom-Pattern-Discovery/
│
├── models/
│   ├── kmeans_model.pkl        # Trained K-Means model
│   ├── pca_model.pkl           # Trained PCA model
│   ├── scaler.pkl              # Fitted StandardScaler
│   ├── symptom_columns.pkl     # List of 329 symptom feature names
│   └── cluster_cache.pkl       # Pre-computed 0.3MB cluster cache (replaces 78MB DataFrame)
│
├── data/
│   └── preclustered_dataset.zip  # Compressed dataset (2.5MB zip → 160MB CSV)
│
├── static/
│   ├── css/style.css           # Clinical Brutalism design system
│   ├── js/app.js               # Frontend logic
│   └── sample_csvs/            # Built-in demo patient datasets (10/15/20 patients)
│
├── templates/
│   └── index.html              # Jinja2 template
│
├── app.py                      # Flask backend
├── requirements.txt            # Pinned dependencies
├── .python-version             # Forces Python 3.11.9 on Render
├── runtime.txt                 # Render Python version fallback
└── .gitignore
```

---

## ⚙️ Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/SATYA012904/Disease-Symptom-Pattern-Discovery.git
cd Disease-Symptom-Pattern-Discovery

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
http://127.0.0.1:5000
```

---

## 📊 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 2.3 |
| ML | scikit-learn 1.6.1 (KMeans, PCA, StandardScaler, Cosine Similarity) |
| Data | Pandas 2.1.4, NumPy 1.26.4 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Fonts | Syne + DM Sans (Google Fonts) |
| Deployment | Render (free tier) |
| Python | 3.11.9 |

---

## 🧠 Memory Optimization (Render Free Tier — 512MB limit)

The biggest engineering challenge was fitting the app within Render's 512MB RAM limit:

| Problem | Solution |
|---|---|
| `read_csv` spikes to 616MB (float64 intermediate) | Pass `dtype=uint8` map directly into `read_csv` |
| 78MB DataFrame kept in memory at runtime | Pre-computed 0.3MB `cluster_cache.pkl` with stratified 2k samples/cluster |
| Cosine similarity on 82k rows (Cluster 2) → OOM | Capped at 2,000 stratified rows per cluster |
| Python 3.14 default on Render breaks pandas | `.python-version` file pins Python 3.11.9 |

Final startup memory: **~120MB** (well within 512MB limit).

---

## 🎯 Use Cases

- Healthcare analytics & disease pattern discovery
- Clinical decision support prototype
- Medical symptom triage assistance
- Educational ML demonstration
- Research on unsupervised learning in healthcare

---

## 🔮 Future Improvements

- [ ] Deep learning disease prediction (LSTM / Transformer)
- [ ] Explainable AI (SHAP / LIME for symptom importance)
- [ ] Real-time patient monitoring dashboard
- [ ] Voice-based symptom input
- [ ] Medical report PDF generation
- [ ] Multilingual support

---

## 👨‍💻 Author

**Satyabrata Sahu**
B.Tech Computer Science Engineering
*Machine Learning · Data Science · Artificial Intelligence*

---

## 📜 License

This project is developed for educational and research purposes.
