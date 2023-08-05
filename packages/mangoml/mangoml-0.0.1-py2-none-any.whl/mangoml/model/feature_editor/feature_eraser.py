"""Module that contains FeatureEraser class"""
import numpy as np
from sklearn.base import TransformerMixin

class FeatureEraser(TransformerMixin):
    """Class used to delete features before passing it to models"""
    def __init__(self, column_indexes):
        self.column_indexes_ = column_indexes

    def fit(self, X, y=None):
        """Fit feature eraser"""
        return self

    def transform(self, X):
        """Apply pipeline transformations to delete the configured features"""
        if len(self.column_indexes_) > 0:
            if X.ndim == 1 or X.shape[1] == len(self.column_indexes_):
                return None
            transformed_input = np.delete(X, self.column_indexes_, 1)
            return transformed_input
        return X
