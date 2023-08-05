"""Module that contains ModelWrapperTransformer class"""
from sklearn.base import TransformerMixin
import numpy as np

class ModelWrapperTransformer(TransformerMixin):
    """Class used as a wrapper when the transformation should be obtained
    from a model prediction"""
    def __init__(self, model):
        self.model_ = model

    def fit(self, X, y=None):
        """Fit the internal model"""
        self.model_.fit(X, y)
        return self

    def transform(self, X):
        """Use internal model prediction as data transformation"""
        transformed_data = np.array([[elem] for elem in self.model_.predict(X)])
        return transformed_data
