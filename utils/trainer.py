from .detector import detect
from .train_class import train_classification
from .train_reg import train_regression

def train_model(X, y, problem_type):
    if problem_type == 'classification':
        return train_classification(X, y)
    elif problem_type == 'regression':
        return train_regression(X, y)
    else:
        raise ValueError(f"Unknown problem type: '{problem_type}'. Expected 'classification' or 'regression'.")