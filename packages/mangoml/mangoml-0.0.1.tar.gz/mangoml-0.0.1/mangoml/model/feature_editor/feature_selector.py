"""Module that contains FeatureSelector class"""
from sklearn.base import TransformerMixin

class FeatureSelector(TransformerMixin):
    """Class used to select only the desired features"""
    def __init__(self, column_indexes):
        self.column_indexes_ = column_indexes

    def fit(self, X, y=None):
        """Fit feature selector"""
        return self

    def transform(self, X):
        """Apply selection to data"""
        return X[:, self.column_indexes_]
