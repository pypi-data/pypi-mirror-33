"""Module that contains ModelPool class"""
import numpy as np
from mangoml.model.pipeline_model import PipelineModel
from mangoml.model.ensembles.ensembler_factory import EnsemblerFactory
from mangoml.model.scores.score_method_factory import ScoreMethodFactory
from mangoml.model.splitters.splitter_factory import SplitterFactory

class ModelPool(object):
    """Class responsible for model selection based on cross validation results"""
    def __init__(self, configs, is_score_ascending=True, column_names=[]):
        self.configs_ = configs
        self.models_ = []
        self.best_model_ = None
        self.best_performance_ = 0
        self.is_score_ascending_ = is_score_ascending
        self.column_names_ = column_names
        self.is_time_series_data_ = configs.get('is_time_series_data', False)
        self.time_window_ = configs.get('time_window', 1)

        self.splitter_ = self.build_splitter()
        self.register_models()
        if 'ensemble_models' in configs['pool']:
            self.register_ensemble_models()

    def register_ensemble_models(self):
        """Method used to register ensemble models that will be compared during
        model selection"""
        ensemble_models = self.configs_['pool']['ensemble_models']

        score_method_factory = ScoreMethodFactory()
        score_method = score_method_factory.build(self.configs_)
        ensembler_factory = EnsemblerFactory()

        for i in range(0, len(ensemble_models)):
            new_model = ensembler_factory.build(ensemble_models[i]['id'],
                                                ensemble_models[i], score_method,
                                                self.configs_['predict_as_probability'],
                                                self.column_names_)
            if not new_model.init():
                print 'Error in model', ensemble_models[i]['id']
            else:
                print 'Model', new_model.get_name(), 'registered\n'
                self.models_.append(new_model)
        print '\n'

    def build_splitter(self):
        """Builds the configured splitter used for data splitting"""
        factory = SplitterFactory()
        return factory.build(self.configs_['splitter']['id'],
                             self.configs_['splitter']['parameters'])

    def register_models(self):
        """Method used to register models that will be compared during model
        selection"""
        model_configs = self.configs_['pool']['pipeline_models']

        score_method_factory = ScoreMethodFactory()
        score_method = score_method_factory.build(self.configs_)

        for i in range(0, len(model_configs)):
            new_model = PipelineModel(model_configs[i], score_method,
                                      self.configs_['predict_as_probability'],
                                      self.column_names_)
            if not new_model.init():
                print 'Error in model', model_configs[i]['model']['id']
            else:
                print 'Model', new_model.get_name(), 'registered'
                self.models_.append(new_model)
        print '\n'

    def is_best_model(self, performance):
        """Check if the performance of a model is the best until now"""
        if self.best_model_ is None:
            return True
        elif self.is_score_ascending_ and performance > self.best_performance_:
            return True
        elif not self.is_score_ascending_ and performance < self.best_performance_:
            return True
        return False

    def estimate_model_performance(self, model, data, split_indexes):
        """Method used to estimate a model performance"""
        if not self.is_time_series_data_:
            return model.estimate_performance(data, split_indexes)
        return model.estimate_timeseries_performance(data, split_indexes,
                                                     self.time_window_)

    def pick_best_model(self, data):
        """Method used to select the best model based on the configured scoring
        method"""
        self.best_model_ = None
        self.best_performance_ = 0

        split_indexes = list(self.splitter_.split(data))
        for i in range(0, len(self.models_)):
            print 'Fitting model', self.models_[i].get_name(), '...'
            performance = self.estimate_model_performance(self.models_[i], data,
                                                          split_indexes)
            if self.is_best_model(performance):
                self.best_model_ = self.models_[i]
                self.best_performance_ = performance

        print 'Best model:', self.best_model_.get_name(),\
          'with performance equals', self.best_performance_
        return self.best_model_

    def fit_best_model(self, data):
        """Method used to train the model with the best scoring performance"""
        fit_input = data.get_features()
        target_input = data.get_targets()
        self.best_model_.fit(fit_input, target_input)

    def get_best_model_predictions(self, data):
        """Method that returns the predictions of the best model"""
        prediction_input = data.get_features()
        if data.is_log_target():
            return np.exp(self.best_model_.predict(prediction_input))
        return self.best_model_.predict(prediction_input)

    def get_best_model_cv_predictions(self, data):
        """Method that returns the predictions from data with a target using
        cross validation (only the bin not used to fit will be predicted as
        in stacking)"""
        return self.best_model_.cv_predict(data, self.splitter_)
