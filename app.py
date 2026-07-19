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

# Load pre-computed cluster cache (1MB) instead of full dataset (78MB+)
cluster_cache = joblib.load('models/cluster_cache.pkl')


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
    0: "💪", 1: "🦷", 2: "🫁", 3: "💧", 4: "🦴",
    5: "🔬", 6: "🤱", 7: "👁️", 8: "👁️‍🗨️", 9: "🧠",
    10: "🫃", 11: "🧘", 12: "🩹",
}

# ─── Pre-compute clustered data ────────────────────────────────────────────────
# X = main_df[symptom_columns]
# y = main_df['diseases']




def predict_for_input(input_vector_df):
    scaled       = scaler.transform(input_vector_df)
    pca_v        = pca.transform(scaled)
    cluster_num  = int(kmeans.predict(pca_v)[0])
    cluster_name = cluster_names[cluster_num]

    cache        = cluster_cache[cluster_num]
    features     = cache['features']
    diseases     = cache['diseases']

    sim_scores   = cosine_similarity(input_vector_df, features)[0]
    top_indices  = np.argsort(sim_scores)[-100:]
    sim_diseases = diseases[top_indices]

    unique, counts = np.unique(sim_diseases, return_counts=True)
    mask         = counts >= 3
    unique, counts = unique[mask], counts[mask]
    total        = counts.sum()
    pct          = (counts / total) * 100
    order        = np.argsort(pct)[::-1]

    disease_pct  = {unique[i]: pct[i] for i in order}
    return cluster_num, cluster_name, disease_pct


# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html',
        symptom_columns=symptom_columns,
        cluster_names=cluster_names,
        cluster_icons=cluster_icons)

@app.route('/api/sample-preview/<int:size>')
def sample_preview(size):

    mapping = {
        10: 'static/sample_csvs/corrected_mixed_patients_10.csv',
        15: 'static/sample_csvs/corrected_mixed_patients_15.csv',
        20: 'static/sample_csvs/corrected_mixed_patients_20.csv'
    }

    if size not in mapping:
        return jsonify({"error": "Invalid sample size"}), 404

    df = pd.read_csv(mapping[size])

    return jsonify({
        "columns": list(df.columns),
        "rows": df.fillna("").to_dict(orient='records'),
        "total_rows": len(df)
    })

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
    for d, p in list(disease_pct.items())[:6]
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
    cache       = cluster_cache[cluster_num]
    return jsonify({
        "top_symptoms": cache['top_symptoms'],
        "top_diseases": cache['top_diseases'],
    })


@app.route('/api/csv-predict', methods=['POST'])
def api_csv_predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    f            = request.files['file']
    patient_df   = pd.read_csv(f)
    symptom_cols = [c for c in patient_df.columns if c.startswith('Symptom_')]
    sym_set      = set(symptom_columns)

    input_df       = pd.DataFrame(0, index=range(len(patient_df)), columns=symptom_columns, dtype='uint8')
    matched_counts = []

    for i, row in patient_df.iterrows():
        matched = 0
        for col in symptom_cols:
            sym = str(row[col]).strip().lower()
            if sym in sym_set:
                input_df.at[i, sym] = 1
                matched += 1
        matched_counts.append(matched)

    scaled_input       = scaler.transform(input_df)
    pca_input          = pca.transform(scaled_input)
    predicted_clusters = kmeans.predict(pca_input)
    del scaled_input, pca_input

    recommendations = []
    for i in range(len(patient_df)):
        cn       = int(predicted_clusters[i])
        cache    = cluster_cache[cn]
        features = cache['features']
        diseases = cache['diseases']

        sims    = cosine_similarity([input_df.iloc[i].values], features)[0]
        top_idx = np.argsort(sims)[-100:]
        sim_dis = diseases[top_idx]

        unique, counts = np.unique(sim_dis, return_counts=True)
        mask           = counts >= 3
        unique, counts = unique[mask], counts[mask]
        if len(unique) == 0:
            recommendations.append("No strong match found")
            continue
        total = counts.sum()
        pct   = (counts / total) * 100
        order = np.argsort(pct)[::-1]
        top3  = [f"{unique[j]} ({pct[j]:.1f}%)" for j in order[:3]]
        recommendations.append(" | ".join(top3))

    rows = []
    for i, (_, row) in enumerate(patient_df.iterrows()):
        rows.append({
            "patient":           row.get('patient', f'Patient {i+1}'),
            "matched_symptoms":  matched_counts[i],
            "disease_category":  cluster_names.get(int(predicted_clusters[i]), "Unknown"),
            "possible_diseases": recommendations[i],
        })

    return jsonify({
        "stats": {
            "total_patients": len(patient_df),
            "total_matched":  int(sum(matched_counts)),
            "unique_groups":  len(set(int(x) for x in predicted_clusters)),
        },
        "rows": rows
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)