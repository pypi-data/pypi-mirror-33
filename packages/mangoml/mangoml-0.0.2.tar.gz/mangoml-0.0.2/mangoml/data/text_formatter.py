"""Module that contains TextFormatter class"""
import re
import numpy as np
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import SnowballStemmer

class TextFormatter(object):
    """Class responsible for formatting text columns from data"""
    def __init__(self, configs):
        self.configs_ = configs

    def remove_html_tags(self, text):
        """Remove all HTML tags from the text"""
        return BeautifulSoup(text, "lxml").get_text()

    def change_case(self, text, case_format):
        """Change the case of a text"""
        if case_format == 'lower':
            return text.lower()
        elif case_format == 'upper':
            return text.upper()
        print 'Invalid case format '+case_format+', keeping text case'
        return text

    def remove_stop_words(self, text, stop_word_config):
        """Remove all stop words from text"""
        words = text.split()
        stop_words = set(stopwords.words(stop_word_config['language']))

        filtered_words = []
        for word in words:
            if word not in stop_words:
                filtered_words.append(word)
        return ' '.join(filtered_words)

    def lemmatize_text(self, text, lemmatizer_config):
        """Apply lemattizers to the text"""
        words = text.split()
        lemmatizer = WordNetLemmatizer()

        lemmatized_words = []
        for word in words:
            lemmatized_words.append(lemmatizer.lemmatize(word))
        return ' '.join(lemmatized_words)

    def stem_text(self, text, stemmer_config):
        """Apply configure stemmers to the text"""
        words = text.split()
        if stemmer_config['algorithm'] == 'porter':
            stemmer = PorterStemmer()
        elif stemmer_config['algorithm'] == 'lancaster':
            stemmer = LancasterStemmer()
        elif stemmer_config['algorithm'] == 'snowball':
            stemmer = SnowballStemmer(stemmer_config['language'])
        else:
            return text

        stemmed_words = []
        for word in words:
            stemmed_words.append(stemmer.stem(word))
        return ' '.join(stemmed_words)

    def remove_non_letters(self, text):
        """Filter characters different than letters"""
        return re.sub('[^a-zA-Z]', ' ', text)

    def perform_operations(self, text, configs):
        """Perform formatting for a single input text"""
        if 'change_case' in configs:
            text = self.change_case(text, configs['change_case'])
        if 'remove_stop_words' in configs:
            text = self.remove_stop_words(text, configs['remove_stop_words'])
        if 'lemmatize_text' in configs:
            text = self.lemmatize_text(text, configs['lemmatize_text'])
        if 'stem_text' in configs:
            text = self.stem_text(text, configs['stem_text'])
        if 'remove_html_tags' in configs and configs['remove_html_tags']:
            text = self.remove_html_tags(text)
        if 'use_only_letters' in configs and configs['use_only_letters']:
            text = self.remove_non_letters(text)
        return text

    def format(self, engine):
        """Format the configured text columns"""
        for column_config in self.configs_['columns']:
            column_name = column_config['name']
            operations = column_config['operations']
            column_values = engine.get_column_as_array(column_name)
            format_row = np.vectorize(lambda x: self.perform_operations(x,
                operations))
            column_values = format_row(column_values)
            engine = engine.set_column(column_name, column_values)
        return engine

    def get_processed_columns(self):
        """Return the list of processed columns"""
        return [column_config['name']
                for column_config in self.configs_['columns']]
