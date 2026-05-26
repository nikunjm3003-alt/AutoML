import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

def load_and_preprocess(df_input, target_col):
    df = df_input.copy()
    
    # dropping columns with null value greater than 50%
    threshold = len(df) * 0.5
    df = df.dropna(thresh=threshold, axis=1)

    # identify column types 
    numerical_cols = [c for c in df.select_dtypes(include=np.number).columns if c != target_col]
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    # impute nulls
    for col in numerical_cols:
        if df[col].isna().sum() > 0:
            df[col] = df[col].fillna(df[col].mean())

    for col in categorical_cols:
        if df[col].isna().sum() > 0:
            df[col] = df[col].fillna(df[col].mode()[0])

    # dropping numeric columns that look like IDs 
    numeric_id_cols = [
        col for col in numerical_cols
        if df[col].nunique() == len(df)
    ]
    if numeric_id_cols:
        df.drop(columns=numeric_id_cols, inplace=True)
    numerical_cols = [col for col in numerical_cols if col not in numeric_id_cols]

    # dropping high cardinality categorical columns
    high_cardinality = [
        col for col in categorical_cols
        if df[col].nunique() > 50
    ]
    if high_cardinality:
        df.drop(columns=high_cardinality, inplace=True)
    categorical_cols = [col for col in categorical_cols if col not in high_cardinality]

    dropped_cols = numeric_id_cols + high_cardinality
    cols_to_encode = [col for col in categorical_cols if col != target_col]

    encoders = {}
    processed_dfs = []

    # Process scalar/numerical features first
    base_df = df.drop(columns=cols_to_encode)
    
    for col in cols_to_encode:
        if df[col].nunique() == 2:
            le = LabelEncoder()
            base_df[col] = le.fit_transform(df[col])
            encoders[col] = ('label', le)
        else:
            ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            encoded = ohe.fit_transform(df[[col]])
            encoded_cols = ohe.get_feature_names_out([col])
            encoded_df = pd.DataFrame(encoded, columns=encoded_cols, index=df.index)
            processed_dfs.append(encoded_df)
            encoders[col] = ('ohe', ohe)

    if processed_dfs:
        final_df = pd.concat([base_df] + processed_dfs, axis=1)
    else:
        final_df = base_df

    # encode target if categorical
    target_encoder = None
    if target_col in categorical_cols:
        le = LabelEncoder()
        final_df[target_col] = le.fit_transform(final_df[target_col])
        target_encoder = le

    X = final_df.drop(target_col, axis=1)
    y = final_df[target_col].copy()

    return X, y, encoders, target_encoder, dropped_cols