from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import joblib
import io
import base64
import json
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ─── Load Models ───────────────────────────────────────────────────────────────
symptom_columns = joblib.load('models/symptom_columns.pkl')
scaler = joblib.load('models/scaler.pkl')
pca = joblib.load('models/pca_model.pkl')
kmeans = joblib.load('models/kmeans_model.pkl')

main_df = pd.read_csv('data/final_healthcare_clustering_dataset.csv')

# ─── Cluster Names ─────────────────────────────────────────────────────────────
cluster_names = {
  0: "Arm & Shoulder Disorders",

    1: "Dental & Oral Disorders",

    2: "Respiratory & Pulmonary Disorders",

    3: "Urinary & Prostate Disorders",

    4: "Musculoskeletal & Joint Disorders",

    5: "Skin Mass & Tumor Disorders",

    6: "Gynecological & Pregnancy Disorders",

    7: "Vision & Retinal Disorders",

    8: "Eye Infection & Conjunctival Disorders",

    9: "Spine & Nerve Pain Disorders",

    10: "Gastrointestinal & Metabolic Disorders",

    11: "Psychiatric & Behavioral Disorders",

    12: "Skin & Dermatological Disorders"
}

cluster_icons = {
    0: "💪", 1: "🦷", 2: "🫁", 3: "🫀", 4: "🦴",
    5: "🔬", 6: "🤱", 7: "👁️", 8: "👁️", 9: "🧠",
    10: "🫃", 11: "🧘", 12: "🩹",
}

# ─── Pre-compute clustered data ────────────────────────────────────────────────
X = main_df[symptom_columns].copy()
y = main_df['diseases']
scaled_X   = scaler.transform(X)
X_pca      = pca.transform(scaled_X)
main_df['Cluster'] = kmeans.predict(X_pca)

X_clustered            = X.copy()
X_clustered['Cluster'] = main_df['Cluster']
X_clustered['diseases']= y.values


def predict_for_input(input_vector_df):
    scaled = scaler.transform(input_vector_df)
    pca_v  = pca.transform(scaled)
    cluster_num  = kmeans.predict(pca_v)[0]
    cluster_name = cluster_names[cluster_num]

    cluster_data     = X_clustered[X_clustered['Cluster'] == cluster_num]
    cluster_features = cluster_data.drop(columns=['Cluster','diseases'])
    sim_scores       = cosine_similarity(input_vector_df, cluster_features)[0]
    top_indices      = np.argsort(sim_scores)[-100:]
    similar_diseases = cluster_data.iloc[top_indices]['diseases']
    disease_counts   = similar_diseases.value_counts()
    disease_counts   = disease_counts[disease_counts >= 3]
    disease_pct      = (disease_counts / disease_counts.sum()) * 100

    return cluster_num, cluster_name, disease_pct


# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html',
        symptom_columns=symptom_columns,
        cluster_names=cluster_names,
        cluster_icons=cluster_icons)


@app.route('/api/symptoms')
def api_symptoms():
    return jsonify(symptom_columns)


@app.route('/api/symptom-check', methods=['POST'])
def api_symptom_check():
    data     = request.json
    symptoms = data.get('symptoms', [])

    input_vector = pd.DataFrame(0, index=[0], columns=symptom_columns)
    for s in symptoms:
        if s in input_vector.columns:
            input_vector.loc[0, s] = 1

    cluster_num, cluster_name, disease_pct = predict_for_input(input_vector)

    results = [
        {"disease": d, "percentage": round(float(p), 2)}
        for d, p in disease_pct.head(6).items()
    ]
    return jsonify({
        "cluster_num":  int(cluster_num),
        "cluster_name": cluster_name,
        "cluster_icon": cluster_icons.get(cluster_num, "🏥"),
        "results":      results
    })


@app.route('/api/group-explorer', methods=['POST'])
def api_group_explorer():
    data        = request.json
    cluster_num = int(data.get('cluster_num', 0))

    cluster_data = X_clustered[X_clustered['Cluster'] == cluster_num]
    symptom_means = (
        cluster_data.drop(columns=['Cluster','diseases'])
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )
    top_diseases = cluster_data['diseases'].value_counts().head(10)

    return jsonify({
        "top_symptoms": {k: round(float(v),4) for k,v in symptom_means.items()},
        "top_diseases": {k: int(v) for k,v in top_diseases.items()},
    })


@app.route('/api/csv-predict', methods=['POST'])
def api_csv_predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    f          = request.files['file']
    patient_df = pd.read_csv(f)
    symptom_cols = [c for c in patient_df.columns if c.startswith('Symptom_')]

    input_df       = pd.DataFrame(0, index=range(len(patient_df)), columns=symptom_columns)
    matched_counts = []

    for i, row in patient_df.iterrows():
        matched = 0
        for col in symptom_cols:
            sym = str(row[col]).strip().lower()
            if sym in input_df.columns:
                input_df.loc[i, sym] = 1
                matched += 1
        matched_counts.append(matched)

    scaled_input      = scaler.transform(input_df)
    pca_input         = pca.transform(scaled_input)
    predicted_clusters= kmeans.predict(pca_input)

    recommendations = []
    for i in range(len(patient_df)):
        cn           = predicted_clusters[i]
        cdata        = X_clustered[X_clustered['Cluster'] == cn]
        cfeatures    = cdata.drop(columns=['Cluster','diseases'])
        sims         = cosine_similarity([input_df.iloc[i]], cfeatures)[0]
        top_idx      = np.argsort(sims)[-100:]
        sim_dis      = cdata.iloc[top_idx]['diseases']
        dc           = sim_dis.value_counts()
        dc           = dc[dc >= 3]
        dp           = (dc / dc.sum()) * 100
        top3 = [f"{d} ({p:.1f}%)" for d,p in dp.head(3).items()]
        recommendations.append(" | ".join(top3))

    rows = []
    for i, (_, row) in enumerate(patient_df.iterrows()):
        rows.append({
            "patient":           row.get('patient', f'Patient {i+1}'),
            "matched_symptoms":  matched_counts[i],
            "disease_category":  cluster_names.get(int(predicted_clusters[i]), "Unknown"),
            "possible_diseases": recommendations[i],
        })

    total_patients    = len(patient_df)
    total_matched     = int(sum(matched_counts))
    unique_groups     = len(set(predicted_clusters))

    return jsonify({
        "stats": {
            "total_patients": total_patients,
            "total_matched":  total_matched,
            "unique_groups":  unique_groups,
        },
        "rows": rows
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
