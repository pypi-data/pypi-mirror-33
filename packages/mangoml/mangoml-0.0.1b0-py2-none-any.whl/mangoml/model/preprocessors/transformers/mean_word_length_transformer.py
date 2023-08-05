"""Module that contains MeanWordLengthTransformer class"""
import numpy as np
from sklearn.base import TransformerMixin

class MeanWordLengthTransformer(TransformerMixin):
    """Class used to transform a text feature into the mean word length"""
    def fit(self, X, y=None):
        """Empty method necessary for a transformer"""
        return self

    def meanWordLength(self, sentence):
        """Method that calculates the mean word length of a sentence"""
        words = sentence.split()
        word_lengths = [len(word) for word in words]
        if len(word_lengths) == 0:
            return 0
        return np.average(word_lengths)

    def transform(self, X):
        """Method that transform the text into the mean word length"""
        return [[self.meanWordLength(x)] for x in X]
