from sklearn.model_selection import train_test_split, KFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
import pandas as pd


def train_regression(X, y):
    models = ["LinearRegression", "DecisionTreeRegressor", "RandomForestRegressor", "XGBRegressor"]

    results = []
    pipeline = {}

    for model_name in models:

        if model_name == "LinearRegression":
            pipe = Pipeline([
                ('scaler', StandardScaler()),
                ('model', LinearRegression())
            ])

        elif model_name == "DecisionTreeRegressor":
            pipe = Pipeline([
                ('model', DecisionTreeRegressor(max_depth=5, random_state=42))
            ])

        elif model_name == "RandomForestRegressor":
            pipe = Pipeline([
                ('model', RandomForestRegressor(
                    n_jobs=-1,
                    random_state=42,
                    n_estimators=50
                ))
            ])

        elif model_name == "XGBRegressor":
            pipe = Pipeline([
                ('model', XGBRegressor(
                    n_estimators=50, max_depth=5, learning_rate=0.1,
                    random_state=42, n_jobs=-1
                ))
            ])

        pipeline[model_name] = pipe

        # train/test split evaluation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        pipe.fit(X_train, y_train)
        y_pred_tts = pipe.predict(X_test)

        tts_r2   = r2_score(y_test, y_pred_tts)
        tts_mae  = mean_absolute_error(y_test, y_pred_tts)
        tts_rmse = root_mean_squared_error(y_test, y_pred_tts)

        # k-fold cross-validation
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        y_pred_kf = cross_val_predict(pipe, X, y, cv=kf)

        kf_r2   = r2_score(y, y_pred_kf)
        kf_mae  = mean_absolute_error(y, y_pred_kf)
        kf_rmse = root_mean_squared_error(y, y_pred_kf)

        results.append({
            'model'   : model_name,
            'TTS R2'  : round(tts_r2, 4),
            'TTS MAE' : round(tts_mae, 4),
            'TTS RMSE': round(tts_rmse, 4),
            'KF R2'   : round(kf_r2, 4),
            'KF MAE'  : round(kf_mae, 4),
            'KF RMSE' : round(kf_rmse, 4)
        })

    results_df = pd.DataFrame(results).set_index('model')
    best_model_name = results_df['KF R2'].idxmax()

    best_pipe = pipeline[best_model_name]
    best_pipe.fit(X, y)
    return best_pipe, best_model_name, results_df