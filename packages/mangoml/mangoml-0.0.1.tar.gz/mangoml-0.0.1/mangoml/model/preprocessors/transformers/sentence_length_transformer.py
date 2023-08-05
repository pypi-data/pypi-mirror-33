"""Module that contains SentenceLengthTransformer class"""
from sklearn.base import TransformerMixin

class SentenceLengthTransformer(TransformerMixin):
    """Class used to transform a text feature into the size of the text"""
    def fit(self, X, y=None):
        """Empty method necessary for a transformer"""
        return self

    def transform(self, X):
        """Method that transform the text into the size of the text"""
        return [[len(x)] for x in X]
