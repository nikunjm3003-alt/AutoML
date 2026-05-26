import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import set_app_background

st.set_page_config(page_title="Prediction - AutoML Studio", layout="centered")
set_app_background("assets/Back2.jpg")

if 'model' not in st.session_state or st.session_state.model is None:
    st.warning("No model trained yet. Please go to the Home page, upload a dataset and train a model first.")
    st.stop()

model          = st.session_state.model
encoders       = st.session_state.encoder
target_encoder = st.session_state.target_encoder
feature_names  = st.session_state.feature_names
problem_type   = st.session_state.problem_type
best_model     = st.session_state.best_model_name
df             = st.session_state.df
target_col     = st.session_state.target_col
dropped_cols   = st.session_state.get('dropped_cols', [])

col_back, col_fwd = st.columns([1, 1])
with col_back:
    if st.button("← Home", use_container_width=True):
        st.switch_page("app.py")
with col_fwd:
    if st.button("Dashboard →", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")

st.markdown("""
    <h1 style="font-family:'Orbitron',monospace; font-size:2rem; font-weight:700;
               background: linear-gradient(90deg,#a78bfa,#60a5fa);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
         Prediction
    </h1>
""", unsafe_allow_html=True)
st.caption(f"Model: **{best_model}** | Task: **{problem_type.capitalize()}** | Target: **{target_col}**")
st.divider()

st.subheader("Enter Feature Values")
user_input = {}
original_cols = [c for c in df.columns if c != target_col and c not in dropped_cols]

binary_01_cols = {
    col for col in original_cols
    if col in df.select_dtypes(include=np.number).columns
    and df[col].dropna().nunique() == 2
    and set(df[col].dropna().unique()).issubset({0, 1})
}

cols = st.columns(2)
for i, col in enumerate(original_cols):
    with cols[i % 2]:
        if col in binary_01_cols:
            choice = st.selectbox(col, ["No", "Yes"], key=f"input_{col}")
            user_input[col] = 1 if choice == "Yes" else 0
        elif col in df.select_dtypes(include=np.number).columns:
            if df[col].nunique() <= 10:
                options = sorted(df[col].dropna().unique().tolist())
                user_input[col] = st.selectbox(col, options, key=f"input_{col}")
            else:
                min_val = float(df[col].min())
                max_val = float(df[col].max())
                mean_val = float(df[col].mean())
                user_input[col] = st.slider(col, min_value=min_val, max_value=max_val, value=mean_val, key=f"input_{col}")
        else:
            options = df[col].dropna().unique().tolist()
            user_input[col] = st.selectbox(col, options, key=f"input_{col}")

st.divider()

if st.button("Predict", use_container_width=True):
    try:
        input_df = pd.DataFrame([user_input])
        ohe_dfs = []
        cols_to_drop = []

        for col, (enc_type, enc) in encoders.items():
            if col in input_df.columns:
                if enc_type == 'label':
                    input_df[col] = enc.transform(input_df[col])
                elif enc_type == 'ohe':
                    ohe_cols = enc.get_feature_names_out([col])
                    encoded = enc.transform(input_df[[col]])
                    encoded_df = pd.DataFrame(encoded, columns=ohe_cols, index=input_df.index)
                    ohe_dfs.append(encoded_df)
                    cols_to_drop.append(col)

        if cols_to_drop:
            input_df.drop(columns=cols_to_drop, inplace=True)
        if ohe_dfs:
            input_df = pd.concat([input_df] + ohe_dfs, axis=1)

        input_df = input_df.reindex(columns=feature_names, fill_value=0)
        prediction = model.predict(input_df)[0]

        if target_encoder is not None:
            prediction = target_encoder.inverse_transform([int(prediction)])[0]

        st.subheader("Prediction Result")
        if problem_type == 'classification':
            st.success(f"Predicted Class: **{prediction}**")
            if hasattr(model, 'predict_proba'):
                probs = model.predict_proba(input_df)[0]
                classes = target_encoder.classes_ if target_encoder else [str(i) for i in range(len(probs))]
                prob_df = pd.DataFrame({'Class': classes, 'Probability': probs.round(4)})
                st.dataframe(prob_df, use_container_width=True, hide_index=True)
        else:
            st.success(f"Predicted Value: **{round(float(prediction), 4)}**")

    except Exception as e:
        st.error(f"Prediction error: {e}")