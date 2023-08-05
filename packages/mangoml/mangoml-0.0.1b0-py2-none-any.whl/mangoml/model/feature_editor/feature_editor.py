"""Module that contains FeatureEditor class"""
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin
from sklearn.pipeline import FeatureUnion

from mangoml.model.preprocessors.preprocessor_factory import PreprocessorFactory
from mangoml.model.feature_editor.feature_selector import FeatureSelector
from mangoml.model.feature_editor.feature_eraser import FeatureEraser

class FeatureEditor(TransformerMixin):
    """Class used to add or delete features before passing it to models"""
    def __init__(self, configs, column_names):
        self.configs_ = configs
        self.pipeline_ = None
        self.column_names_ = column_names

        self.build_operations()

    def build_add_step(self, configs):
        """Create a pipeline for a specific add operation"""
        preprocessor_factory = PreprocessorFactory()
        pipeline_steps = []

        if 'input' in configs:
            filtered_indexes = [self.column_names_.index(column)\
                for column in configs['input']]
            selector = FeatureSelector(filtered_indexes)
            pipeline_steps.append(('selector', selector))

        operation = preprocessor_factory.build(
            configs['operation']['id'], configs['operation']['parameters'])
        pipeline_steps.append(('operation', operation))

        return Pipeline(pipeline_steps)

    def build_delete_step(self, deletion_list):
        """Create a transformer for a delete operation"""
        filtered_indexes = [self.column_names_.index(column)\
                for column in deletion_list]
        return FeatureEraser(filtered_indexes)

    def build_operations(self):
        """Build the pipeline that will apply all the configured operations"""
        pipeline_steps = []

        del_operation = self.build_delete_step(self.configs_.get('delete', []))
        pipeline_steps.append(('delete', del_operation))

        add_configs = self.configs_.get('add', [])
        for i in range(0, len(add_configs)):
            add_operation = self.build_add_step(add_configs[i])
            pipeline_steps.append(('add_'+str(i), add_operation))

        self.pipeline_ = FeatureUnion(pipeline_steps)

    def fit(self, X, y=None):
        """Fit feature editor pipeline"""
        return self.pipeline_.fit(X, y)

    def get_column_names(self, input_dim):
        """Return a list with the resulting column names after transformation"""
        deletion_list = self.configs_.get('delete', [])
        ret = list(self.column_names_)
        for elem in deletion_list:
            ret.remove(elem)
        ret += ['extra_feature_' + str(i) for i in range(input_dim - len(ret))]
        return ret

    def transform(self, X):
        """Apply pipeline transformations to data"""
        return self.pipeline_.transform(X)
