"""Module that contains WordCountTransformer class"""
from sklearn.base import TransformerMixin

class WordCountTransformer(TransformerMixin):
    """Class used to transform a text feature into the number of words"""
    def fit(self, X, y=None):
        """Empty method necessary for a transformer"""
        return self

    def transform(self, X):
        """Method that transform the text into the number of words"""
        return [[len(x.split())] for x in X]
