"""Module that contains StopwordCountTransformer class"""
from sklearn.base import TransformerMixin
from nltk.corpus import stopwords

class StopwordCountTransformer(TransformerMixin):
    """Class used to transform a text feature into the count of stopwords
    present in the text"""
    def __init__(self, **kwargs):
        self.language = kwargs['language']

    def fit(self, X, y=None):
        """Method used to store the set of stopwords accordingly with the
        text language"""
        self.stop_words_ = set(stopwords.words(self.language))
        return self

    def count_stop_words(self, sentence):
        """Method that counts the number of stopwords in a text"""
        words = sentence.split()
        filtered_words = []
        for word in words:
            if word not in self.stop_words_:
                filtered_words.append(word)
        return len(filtered_words)

    def transform(self, X):
        """Method that transform the text into the number of stopwords"""
        return [[self.count_stop_words(x)] for x in X]
