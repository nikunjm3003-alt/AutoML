def detect(y):
    if y.dtype == 'object':
        return 'classification'
    elif y.dtype == 'bool':
        return 'classification'
    elif y.dtype in ['int32', 'int64'] and y.nunique() <= 10:
        return 'classification'
    elif y.dtype in ['float32', 'float64'] and y.nunique() <= 10:
        return 'classification'
    else:
        return 'regression'