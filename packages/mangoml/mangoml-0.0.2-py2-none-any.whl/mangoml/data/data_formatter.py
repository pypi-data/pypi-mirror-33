"""Module that contains DataFormatter class"""
import math
import numpy as np
from sklearn.preprocessing import LabelEncoder
from mangoml.data.engines.engine_factory import EngineFactory
from mangoml.data.text_formatter import TextFormatter

class DataFormatter(object):
    """Class responsible for data formatting"""
    def __init__(self, configs):
        self.configs_ = configs
        self.engine_ = self.build_engine()

        self.log_target_ = self.configs_['data_formatter'].get('log_target',
                                                               False)
        self.numeric_categorical_columns_ =\
          self.configs_['data_formatter'].get('numeric_categorical_columns', [])

        self.columns_to_remove_ = self.set_columns_to_remove()
        self.text_formatter_ = self.build_text_formatter()
        self.encoders_ = self.fit_categorical_encoders()

    def build_engine(self):
        """Build the configured engine"""
        engine_parameters = self.configs_['inputs']['train']['engine']
        engine_factory = EngineFactory(engine_parameters)
        return engine_factory.build()

    def build_text_formatter(self):
        """Build TextFormatter object"""
        if 'text_formatter' in self.configs_['data_formatter']:
            return TextFormatter(self.configs_['data_formatter']
                                 ['text_formatter'])
        return None

    def should_column_be_removed(self, column_name):
        """Verify if a column should be removed using some criteria"""
        if 'missing_fraction_threshold' not in self.configs_['data_formatter']:
            return False

        missing_threshold = \
            self.configs_['data_formatter']['missing_fraction_threshold']
        missing_fraction = self.engine_.get_column_missing_fraction(column_name)
        if missing_fraction > missing_threshold:
            return True
        return False

    def set_columns_to_remove(self):
        """Choose all columns that should be removed based on parameters"""
        if 'columns_to_remove' in self.configs_['data_formatter']:
            columns_to_remove = self.configs_['data_formatter']['columns_to_remove']
        else:
            columns_to_use = self.configs_['data_formatter']['columns_to_use']
            columns_to_remove = [column for column in self.engine_.get_column_names() if column not in columns_to_use]
        automatic_removes = []
        for column_name in self.engine_.get_column_names():
            #Column is scheduled to be removed in config file
            if column_name in columns_to_remove:
                continue
            if self.should_column_be_removed(column_name):
                automatic_removes.append(column_name)

        if len(automatic_removes) > 0:
            print 'Columns automatically removed based on configurations:', \
              automatic_removes
        return columns_to_remove + automatic_removes

    def replace_nan(self, value):
        """Function used to replace nan with None"""
        if type(value) is float and math.isnan(value):
            return None
        return value

    def get_encoder(self):
        """Returns the object responsible for encoding categorical variables"""
        encoder_type = self.configs_['data_formatter'].get(\
          'categorical_encoder', '')
        if encoder_type == 'sklearn_LabelEncoder':
            return LabelEncoder()
        return None

    def fit_categorical_encoders(self):
        """Fit encoders for categorical fields. All the string columns are
        assumed as categorical."""
        encoders = {}
        categorical_columns = self.engine_.get_string_column_names()
        categorical_columns += self.numeric_categorical_columns_

        #If an encoder is not configured, do nothing
        if self.get_encoder() is None:
            return encoders

        for column_name in set(categorical_columns):
            if self.text_formatter_ is not None and\
              column_name in self.text_formatter_.get_processed_columns():
                #Ignore text columns processed by TextFormatter
                continue
            if column_name in self.columns_to_remove_:
                #Ignore columns that will be removed
                continue

            column_encoder = self.get_encoder()
            column_values = self.engine_.get_column_as_array(column_name)
            column_values = [str(elem) for elem in column_values]
            #Append None as a label and replace nan to deal with missing data
            column_values = np.append(column_values, [None])
            nan_replacer = np.vectorize(self.replace_nan)
            column_values = nan_replacer(column_values)

            encoders[column_name] = column_encoder.fit(column_values)
        if len(encoders) > 0:
            print 'Categorical columns that will be encoded:', encoders.keys()
        return encoders

    def format_categorical_columns(self, engine):
        """Format all the categorical columns from data for model building"""

        #If an encoder is not configured, do nothing
        if self.get_encoder() is None:
            return engine

        categorical_columns = engine.get_string_column_names()
        categorical_columns += self.numeric_categorical_columns_
        for column_name in set(categorical_columns):
            if self.text_formatter_ is not None and\
              column_name in self.text_formatter_.get_processed_columns():
                #Ignore text columns processed by TextFormatter
                continue
            column_values = engine.get_column_as_array(column_name)
            column_values = [str(elem) for elem in column_values]
            #Replace nan to deal with missing data
            nan_replacer = np.vectorize(self.replace_nan)
            column_values = nan_replacer(column_values)

            formatted_column = self.encoders_[column_name].transform(
                column_values)
            engine = engine.set_column(column_name, formatted_column)
        return engine

    def get_numeric_filling_value(self, engine, column_name):
        """Method that returns how the missing numeric fields should be
        filled"""
        if 'numeric_fill_value' not in self.configs_['data_formatter']:
            print '\nMissing numeric data will not be filled (option '\
              'numeric_fill_value not configured)\n'
            return None

        numeric_fill_value = self.configs_['data_formatter']['numeric_fill_value']
        if numeric_fill_value == 'column_mean':
            return engine.get_column_mean(column_name)
        elif numeric_fill_value == 'column_median':
            return engine.get_column_median(column_name)
        elif type(numeric_fill_value) is float:
            return float(numeric_fill_value)
        elif type(numeric_fill_value) is int:
            return int(numeric_fill_value)

        print 'Invalid numeric filling value:', numeric_fill_value
        return None

    def format_numeric_columns(self, engine):
        """Format all the numeric columns from data for model building"""
        for column_name in engine.get_numeric_column_names():
            filling_value = self.get_numeric_filling_value(engine, column_name)
            if filling_value is None:
                break
            engine = engine.fill_column_missing_values(column_name,
                                                       filling_value)
        return engine

    def get_formatted_features(self, engine):
        """Format the feature matrix"""
        print '\n'
        engine = engine.erase_columns(self.columns_to_remove_)
        engine = self.format_numeric_columns(engine)
        if self.text_formatter_ is not None:
            engine = self.text_formatter_.format(engine)
        engine = self.format_categorical_columns(engine)
        print 'Formatted columns used:', engine.get_column_names(), '\n'
        return engine.get_column_names(), engine.get_table_as_matrix()

    def get_formatted_target(self, targets):
        """Format the target array"""
        if self.log_target_:
            return np.log(targets)
        return targets

    def is_log_target(self):
        """Returns true when the target is in log scale"""
        return self.log_target_
