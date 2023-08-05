"""Module that contains PreprocessorFactory class"""
from sklearn import ensemble
from sklearn import preprocessing
from sklearn.feature_extraction import text
from sklearn.preprocessing import PolynomialFeatures
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectFromModel
from mangoml.model.preprocessors.transformers.mean_word_length_transformer\
 import MeanWordLengthTransformer
from mangoml.model.preprocessors.transformers.sentence_length_transformer\
 import SentenceLengthTransformer
from mangoml.model.preprocessors.transformers.word_count_transformer\
 import WordCountTransformer
from mangoml.model.preprocessors.transformers.stopword_count_transformer\
 import StopwordCountTransformer
from mangoml.model.preprocessors.transformers.model_wrapper_transformer\
 import ModelWrapperTransformer

class PreprocessorFactory(object):
    """Class used to build preprocessors"""
    def build_mangoml(self, preprocessor_id, preprocessor_params):
        """Method that builds preprocessors/wrappers implemented by mango"""
        if preprocessor_id == 'mangoml_WordCountTransformer':
            return WordCountTransformer(**preprocessor_params)
        elif preprocessor_id == 'mangoml_StopwordCountTransformer':
            return StopwordCountTransformer(**preprocessor_params)
        elif preprocessor_id == 'mangoml_MeanWordLengthTransformer':
            return MeanWordLengthTransformer(**preprocessor_params)
        elif preprocessor_id == 'mangoml_SentenceLengthTransformer':
            return SentenceLengthTransformer(**preprocessor_params)
        elif preprocessor_id == 'mangoml_sklearn_KMeans':
            return ModelWrapperTransformer(KMeans(**preprocessor_params))
        elif preprocessor_id == 'mangoml_sklearn_MiniBatchKMeans':
            return ModelWrapperTransformer(MiniBatchKMeans(**preprocessor_params))
        return None

    def build_sklearn(self, preprocessor_id, preprocessor_params):
        """Method that builds preprocessors implemented in sklearn"""
        if preprocessor_id == 'sklearn_StandardScaler':
            return preprocessing.StandardScaler(**preprocessor_params)
        elif preprocessor_id == 'sklearn_ExtraTreesClassifier':
            return SelectFromModel(ensemble.ExtraTreesClassifier(\
              **preprocessor_params))
        elif preprocessor_id == 'sklearn_TfidfVectorizer':
            return text.TfidfVectorizer(**preprocessor_params)
        elif preprocessor_id == 'sklearn_CountVectorizer':
            return text.CountVectorizer(**preprocessor_params)
        elif preprocessor_id == 'sklearn_PCA':
            return PCA(**preprocessor_params)
        elif preprocessor_id == 'sklearn_PolynomialFeatures':
            return PolynomialFeatures(**preprocessor_params)
        return None

    def build(self, preprocessor_id, preprocessor_params):
        """Method that builds preprocessors using the specified id"""
        if 'mangoml' in preprocessor_id:
            return self.build_mangoml(preprocessor_id, preprocessor_params)
        elif 'sklearn' in preprocessor_id:
            return self.build_sklearn(preprocessor_id, preprocessor_params)
        return None
