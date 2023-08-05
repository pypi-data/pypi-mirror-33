"""Module that contains PipelineModel class"""
from sklearn.pipeline import Pipeline

from mangoml.model.base_model import BaseModel
from mangoml.model.feature_editor.feature_editor import FeatureEditor
from mangoml.model.preprocessors.preprocessor_factory import PreprocessorFactory
from mangoml.model.model_calibrators.model_calibrator_factory import ModelCalibratorFactory
from mangoml.model.models.model_factory import ModelFactory

class PipelineModel(BaseModel):
    """Class that integrates different stages of the pipeline (preprocessors,
    models, model calibrators). Heavily based on scikit Pipeline"""
    def __init__(self, configs, score_method, predict_as_probability,
                 column_names=[]):
        BaseModel.__init__(self, configs, score_method, predict_as_probability)
        self.column_names_ = column_names

        self.pipeline_steps_ = []
        self.feature_editor_ = None
        self.preprocessor_factory_ = PreprocessorFactory()
        self.model_calibrator_factory_ = ModelCalibratorFactory()
        self.model_factory_ = ModelFactory()

    def build_step(self, step_configs, step_factory, model=None):
        """Method that builds a pipeline step using the appropriate factory"""
        step_id = step_configs['id']
        if 'parameters' in step_configs:
            params = step_configs['parameters']
        else:
            params = {}

        if model is not None:
            return step_factory.build(model, step_id, params)
        return step_factory.build(step_id, params)

    def add_step(self, step_configs, step_factory):
        """Method that adds a configured step"""
        step_id = step_configs['id']
        new_step = self.build_step(step_configs, step_factory)
        if new_step is None:
            return False
        self.pipeline_steps_.append((step_id, new_step))
        return True

    def add_preprocessors(self):
        """Method that configures all preprocessors steps"""
        preprocessor_configs = {}
        if 'preprocessors' in self.configs_:
            preprocessor_configs = self.configs_['preprocessors']

        for i in range(0, len(preprocessor_configs)):
            if not self.add_step(preprocessor_configs[i],\
              self.preprocessor_factory_):
                return False
        return True

    def add_feature_editor(self):
        """Method that configures the feature edition step"""
        feature_editor_configs = {}
        if 'feature_editor' not in self.configs_:
            return

        feature_editor_configs = self.configs_['feature_editor']
        self.feature_editor_ = FeatureEditor(feature_editor_configs,
                                             self.column_names_)
        self.pipeline_steps_.append(('feature_editor', self.feature_editor_))

    def add_model_calibrators(self, raw_pipeline):
        """Method that configures all model calibrators steps"""
        model_calibrator_configs = {}
        if 'model_calibrators' in self.configs_:
            model_calibrator_configs = self.configs_['model_calibrators']

        pipeline = raw_pipeline
        for i in range(0, len(model_calibrator_configs)):
            pipeline = self.build_step(model_calibrator_configs[i],\
              self.model_calibrator_factory_, pipeline)
            if pipeline is None:
                return False

        self.pipeline_ = pipeline
        return True

    def init(self):
        """Method that initializes the pipeline with all the configured
        components"""
        raw_model = self.build_step(self.configs_['model'], self.model_factory_)
        if raw_model is None:
            print 'Error with raw model!'
            return False

        self.add_feature_editor()

        if not self.add_preprocessors():
            print 'Error with preprocessors!'
            return False

        #Building raw pipeline
        self.pipeline_steps_.append(('model', raw_model))
        raw_pipeline = Pipeline(self.pipeline_steps_)

        #Adding model calibrators for raw pipeline
        if not self.add_model_calibrators(raw_pipeline):
            print 'Error with model calibrators!'
            return False
        return True

    def get_name(self):
        """Get the label associated with a model (used for printing)"""
        if 'label' in self.configs_['model']:
            return self.configs_['model']['label']
        return self.configs_['model']['id']

    def print_feature_importance(self, input_data):
        """Method that prints the feature importance obtained by the model
        after training (when available)"""
        model = self.pipeline_.named_steps['model']
        model_id = self.configs_['model']['id']

        if self.feature_editor_ is not None:
            transformed_data = self.pipeline_.named_steps['feature_editor']\
              .transform(input_data)
            feature_names = self.feature_editor_.get_column_names(\
              transformed_data.shape[1])
        else:
            feature_names = self.column_names_

        self.model_factory_.print_feature_importance(model, model_id, feature_names)

    def fit(self, input_data, targets):
        """Method responsible for model training (including all the pipeline
        steps)"""
        self.pipeline_.fit(input_data, targets)
        print_coefs = self.configs_['model'].get('print_feature_importance', False)
        if print_coefs:
            self.print_feature_importance(input_data)

    def predict(self, input_data):
        """Method that returns all the predictions from a trained model"""
        if not self.predict_as_probability_:
            return self.pipeline_.predict(input_data)
        else:
            return self.pipeline_.predict_proba(input_data)

    def get_sklearn_pipeline(self):
        """Returns the sklearn Pipeline object"""
        return self.pipeline_
