"""Module that contains Data class"""
import numpy as np
from mangoml.data.engines.engine_factory import EngineFactory

class Data(object):
    """Class used to manipulate data"""
    def __init__(self, configs, data_formatter):
        self.configs_ = configs
        self.data_formatter_ = data_formatter
        self.engine_ = self.build_engine()
        self.targets_ = self.init_target()
        self.features_names_, self.features_ = self.init_features()
        self.row_split_validation_ = self.configs_.get('row_split_validation', False)

    def build_engine(self):
        """Build the configured engine"""
        engine_factory = EngineFactory(self.configs_['engine'])
        return engine_factory.build()

    def init_target(self):
        """Initialize the target array"""
        if 'target_column' in self.configs_:
            target_column = self.configs_['target_column']
            targets = self.engine_.get_column_as_array(target_column)
            self.engine_ = self.engine_.erase_columns([target_column])
            return self.data_formatter_.get_formatted_target(targets)
        return None

    def init_features(self):
        """Initialize the features matrix"""
        return self.data_formatter_.get_formatted_features(self.engine_)

    def split_array_by_column(self, input_data, indexes):
        """Split an array by column using a sequential index array"""
        if indexes is None:
            return input_data
        beg = indexes[0]
        end = indexes[-1] + 1
        return np.array([data[beg:end] for data in input_data])

    def get_targets(self, indexes=None):
        """Return the target array"""
        if self.row_split_validation_:
            return self.split_array_by_column(self.features_, indexes)

        if indexes is not None:
            return self.targets_[indexes]
        return self.targets_

    def get_features(self, indexes=None):
        """Return the features matrix"""
        if self.row_split_validation_:
            return self.split_array_by_column(self.features_, indexes)

        feature_array = self.features_
        if 'text_feature' in self.configs_ and self.configs_['text_feature']:
            feature_array = np.array([text_feature[0] \
                for text_feature in self.features_])
        if indexes is not None:
            return feature_array[indexes]
        return feature_array

    def is_log_target(self):
        """Returns true when the target is in log scale"""
        return self.data_formatter_.is_log_target()

    def is_row_split_validation(self):
        """Return true when data is a time series"""
        return self.row_split_validation_

    def get_engine(self):
        """Return the internal engine"""
        return self.engine_

    def get_feature_names(self):
        """Return a list with all feature names obtained from data"""
        return self.features_names_
