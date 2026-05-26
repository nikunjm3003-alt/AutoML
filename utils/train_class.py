from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, auc, roc_curve, roc_auc_score
import numpy as np
import pandas as pd


def train_classification(X, y):
    models = ["LogisticRegression", "DecisionTreeClassifier", "RandomForestClassifier", "XGBClassifier"]
    result = []
    pipelines = {}
    is_binary = len(y.unique()) == 2

    for model_name in models:
        if model_name == "LogisticRegression":
            pipe = Pipeline([('smote', SMOTE(random_state=42)),
                             ('scaling', StandardScaler()),
                             ('model', LogisticRegression(random_state=42, max_iter=1000))])

        elif model_name == "DecisionTreeClassifier":
            pipe = Pipeline([('smote', SMOTE(random_state=42)),
                             ('model', DecisionTreeClassifier(max_depth=5, random_state=42))])

        elif model_name == "RandomForestClassifier":
            pipe = Pipeline([('smote', SMOTE(random_state=42)),
                             ('model', RandomForestClassifier(n_jobs=-1, random_state=42, n_estimators=50))])

        elif model_name == "XGBClassifier":
            pipe = Pipeline([('smote', SMOTE(random_state=42)),
                             ('model', XGBClassifier(
                                 n_estimators=50, max_depth=5, learning_rate=0.1,
                                 random_state=42, n_jobs=-1, eval_metric='logloss'
                             ))])

        pipelines[model_name] = pipe

        # train/test split evaluation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        pipe.fit(X_train, y_train)
        y_pred_tts = pipe.predict(X_test)
        tts_acc = accuracy_score(y_test, y_pred_tts)
        tts_f1 = classification_report(y_test, y_pred_tts, output_dict=True)['macro avg']['f1-score']

        if is_binary:
            probs_tts = pipe.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, probs_tts)
            tts_auc = auc(fpr, tpr)
        else:
            probs_tts = pipe.predict_proba(X_test)
            tts_auc = roc_auc_score(y_test, probs_tts, multi_class='ovr', average='macro')

        # k-fold cross-validation
        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        probs_kf = cross_val_predict(pipe, X, y, cv=kf, method='predict_proba')

        if is_binary:
            y_pred_kf = (probs_kf[:, 1] >= 0.5).astype(int)
            fpr, tpr, _ = roc_curve(y, probs_kf[:, 1])
            kf_auc = auc(fpr, tpr)
        else:
            y_pred_kf = np.argmax(probs_kf, axis=1)
            kf_auc = roc_auc_score(y, probs_kf, multi_class='ovr', average='macro')

        kf_acc = accuracy_score(y, y_pred_kf)
        kf_f1 = classification_report(y, y_pred_kf, output_dict=True)['macro avg']['f1-score']

        result.append({
            'Model'    : model_name,
            'TTS Acc'  : round(tts_acc, 4),
            'TTS F1'   : round(tts_f1, 4),
            'TTS AUC'  : round(tts_auc, 4),
            'KFold Acc': round(kf_acc, 4),
            'KFold F1' : round(kf_f1, 4),
            'KFold AUC': round(kf_auc, 4),
        })

    results_df = pd.DataFrame(result).set_index('Model')

    best_metric = 'KFold AUC' if is_binary else 'KFold F1'
    best_model_name = results_df[best_metric].idxmax()

    best_pipe = pipelines[best_model_name]
    best_pipe.fit(X, y)

    return best_pipe, best_model_name, results_df