"""Module that contains BaseModel abstract class"""
from abc import ABCMeta, abstractmethod
import numpy as np

class BaseModel(object):
    """Abstract class that defines common methods for all models"""
    __metaclass__ = ABCMeta
    def __init__(self, configs, score_method, predict_as_probability):
        self.configs_ = configs
        self.score_method_ = score_method
        self.predict_as_probability_ = predict_as_probability

    @abstractmethod
    def init(self):
        """Abstract method. Should initialize all components from a model"""
        pass

    @abstractmethod
    def fit(self, input_data, targets):
        """Abstract method. Should find the parameters of the model from the
        input_data"""
        pass

    @abstractmethod
    def predict(self, input_data):
        """Abstract method. Should make predictions for the input_data from the
        trained model"""
        pass

    @abstractmethod
    def get_name(self):
        """Abstract method. Should return the label associated with a model
        (used for printing)"""
        pass

    def evaluate_predictions(self, input_data, targets, is_log_target):
        """Evaluate the performance of a model based on predictions"""
        predictions = self.predict(input_data)
        if is_log_target:
            score_targets = np.exp(targets)
            score_predictions = np.exp(predictions)
        else:
            score_targets = targets
            score_predictions = predictions
        return self.score_method_(score_predictions, score_targets)

    def evaluate_time_window_predictions(self, input_data, time_window,
                                         is_log_target):
        """Evaluate the performance of a model based on predictions using a time window"""
        pred_data = np.array([time_series[:-time_window] for time_series in input_data])
        targets = np.array([time_series[-time_window:] for time_series in input_data])
        predictions = self.predict(pred_data)
        if is_log_target:
            score_targets = np.exp(targets)
            score_predictions = np.exp(predictions)
        else:
            score_targets = targets
            score_predictions = predictions
        return self.score_method_(score_predictions, score_targets)

    def estimate_performance(self, data, split_indexes):
        """Method used to estimate the performance of the model"""
        scores = []
        is_log_target = data.is_log_target()

        for train_index, test_index in split_indexes:
            fit_inputs = data.get_features(train_index)
            fit_targets = data.get_targets(train_index)
            score_inputs = data.get_features(test_index)
            score_targets = data.get_targets(test_index)
            self.fit(fit_inputs, fit_targets)

            train_score = self.evaluate_predictions(fit_inputs, fit_targets,
                                                    is_log_target)
            print self.get_name(), 'Training score:', train_score

            val_score = self.evaluate_predictions(score_inputs, score_targets,
                                                  is_log_target)
            scores.append(val_score)
            print self.get_name(), 'Last validation score:', scores[-1]

        print self.get_name(), 'scores:', scores
        print self.get_name(), 'final performance:', np.mean(scores), '\n'
        return np.mean(scores)

    def cv_predict(self, data, splitter):
        """Method used to estimate the performance of a model using cross
        validation (as used in stacking). A bin used for predictions will not
        be used to train the model"""
        predictions = np.empty([data.get_features().shape[0],])
        for train_index, test_index in splitter.split(data):
            fit_inputs = data.get_features(train_index)
            fit_targets = data.get_targets(train_index)
            self.fit(fit_inputs, fit_targets)

            score_inputs = data.get_features(test_index)
            if not data.is_log_target():
                predictions[test_index] = self.predict(score_inputs)
            else:
                predictions[test_index] = np.exp(self.predict(score_inputs))
        return predictions

    def estimate_timeseries_performance(self, data, split_indexes, time_window):
        """Method used to estimate the performance of a time series model"""
        scores = []
        is_log_target = data.is_log_target()

        for train_index, test_index in split_indexes:
            fit_inputs = data.get_features(train_index)
            score_targets = data.get_features(test_index)
            self.fit(fit_inputs, None)

            train_score = self.evaluate_time_window_predictions(fit_inputs, time_window,
                                                                is_log_target)
            print self.get_name(), 'Training score:', train_score

            val_score = self.evaluate_predictions(fit_inputs, score_targets,
                                                  is_log_target)
            scores.append(val_score)
            print self.get_name(), 'Last validation score:', scores[-1]

        print self.get_name(), 'scores:', scores
        print self.get_name(), 'final performance:', np.mean(scores), '\n'
        return np.mean(scores)
