import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import set_app_background

st.set_page_config(page_title="DashBoard-AutoML Studio", layout='wide')
set_app_background("assets/Back2.jpg")

if 'model' not in st.session_state or st.session_state.model is None:
    st.warning("No Model Trained Yet. Please go to the Home page, upload a dataset and train a model first")
    st.stop()

df = st.session_state.df
target_col = st.session_state.target_col
problem_type = st.session_state.problem_type
best_model = st.session_state.best_model_name
results_df = st.session_state.results_df
dropped_cols = st.session_state.get('dropped_cols', [])

# show original columns only — exclude columns dropped during preprocessing
# (OHE-expanded columns like Gender_Male live in feature_names, not in df)
display_cols = [c for c in df.columns if c not in dropped_cols]
clean_df = df[display_cols]

numerical_cols = clean_df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = clean_df.select_dtypes(include='object').columns.tolist()

num_features = [c for c in numerical_cols if c != target_col]
cat_features = [c for c in categorical_cols if c != target_col]

col_back, col_fwd = st.columns([1, 1])
with col_back:
    if st.button("← Home", use_container_width=True):
        st.switch_page("app.py")
with col_fwd:
    if st.button(" Predictions →", use_container_width=True):
        st.switch_page("pages/2_predictions.py")

st.markdown("""
    <h1 style="font-family:'Orbitron',monospace; font-size:2rem; font-weight:700;
               background: linear-gradient(90deg,#a78bfa,#60a5fa);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        📊 Dashboard
    </h1>
""", unsafe_allow_html=True)
st.caption(f"Dataset overview and model results for **{target_col}** prediction")

# KPIs
st.subheader("Dataset Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{df.shape[0]:,}")
c2.metric("Columns", f"{df.shape[1]}")
c3.metric("Null Values", f"{df.isna().sum().sum():,}")
c4.metric("Problem Type", problem_type.capitalize())

st.divider()

st.subheader("Model Comparison")
st.success(f"Best Model : **{best_model}**")

def highlight_best(row):
    return ['background-color: #1a4a2e; color: white' if row.name == best_model else '' for _ in row]

st.dataframe(results_df.style.apply(highlight_best, axis=1), use_container_width=True)

st.divider()

# target distribution
st.subheader("TARGET DISTRIBUTION")

if problem_type == 'classification':
    vc = df[target_col].value_counts().reset_index()
    vc.columns = [target_col, 'count']
    fig = px.bar(vc, x=target_col, y='count', color=target_col,
                 title=f"Class Distribution — {target_col}",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    fig = px.histogram(df, x=target_col, nbins=40,
                       title=f"Target Distribution — {target_col}",
                       color_discrete_sequence=['#2ecc71'])
    st.plotly_chart(fig, use_container_width=True)

st.divider()

if num_features:
    st.subheader("Numerical Features")
    cols = st.columns(2)
    for i, col in enumerate(num_features):
        with cols[i % 2]:
            fig = px.histogram(df, x=col, nbins=30, title=col,
                               color_discrete_sequence=['#3498db'])
            fig.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

if cat_features:
    st.subheader("Categorical Features")
    cols = st.columns(2)
    for i, col in enumerate(cat_features):
        with cols[i % 2]:
            vc = df[col].value_counts().reset_index()
            vc.columns = [col, 'count']
            fig = px.bar(vc, x=col, y='count', title=col,
                         color_discrete_sequence=['#9b59b6'])
            fig.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

if len(numerical_cols) >= 2:
    st.subheader("Correlation Heatmap")
    corr = df[numerical_cols].corr().round(2)
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale='RdBu',
        zmid=0,
        text=corr.values,
        texttemplate="%{text}",
        showscale=True
    ))
    fig.update_layout(title="Correlation Matrix — Numerical Columns",
                      height=500)
    st.plotly_chart(fig, use_container_width=True)