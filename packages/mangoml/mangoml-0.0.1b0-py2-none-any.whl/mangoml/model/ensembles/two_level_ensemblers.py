"""Module that contains the two level ensemblers: StackingEnsembler and
BlendingEnsembler classes"""
import numpy as np
from mangoml.model.ensembles.base_two_level_ensembler import BaseTwoLevelEnsembler
from mangoml.model.splitters.splitter_factory import SplitterFactory

class StackingEnsembler(BaseTwoLevelEnsembler):
    """Class that combines models using the stacking method"""
    def __init__(self, configs, score_method, predict_as_probability,
                 column_names):
        BaseTwoLevelEnsembler.__init__(self, configs, score_method,
                                       predict_as_probability, column_names)
        self.splitter_ = self.build_splitter()

    def is_valid_splitter(self):
        """Check if the configured splitter is available for the ensembler"""
        splitter_id = self.configs_['splitter']['id']
        if splitter_id == 'mangoml_sklearn_KFold':
            return True
        elif splitter_id == 'mangoml_sklearn_StratifiedKFold':
            return True
        return False

    def build_splitter(self):
        """Build the configured splitter used for data splitting"""
        if not self.is_valid_splitter():
            print self.configs_['splitter']['id'], 'cannot be used for stacking!'
            return None

        factory = SplitterFactory()
        return factory.build(self.configs_['splitter']['id'],
                             self.configs_['splitter']['parameters'])

    def fit(self, input_data, targets):
        """Train the full ensembler"""
        combiner_target = np.zeros((len(input_data),))
        formatted_combiner_input = np.zeros((len(input_data),\
          len(self.first_level_models_)))

        for train_index, test_index in self.splitter_.split_arrays(input_data, targets):
            first_level_input = input_data[train_index]
            first_level_target = targets[train_index]
            combiner_input = input_data[test_index]

            self.fit_first_level_models(first_level_input, first_level_target)
            formatted_combiner_input[test_index] =\
              self.predict_first_level_models(combiner_input)
            combiner_target[test_index] = targets[test_index]

        self.fit_combiner_model(formatted_combiner_input, combiner_target)
        self.fit_first_level_models(input_data, combiner_target)

class BlendingEnsembler(BaseTwoLevelEnsembler):
    """Class that combines models using the blending method"""
    def __init__(self, configs, score_method, predict_as_probability,
                 column_names):
        BaseTwoLevelEnsembler.__init__(self, configs, score_method,
                                       predict_as_probability, column_names)
        self.splitter_ = self.build_splitter()

    def is_valid_splitter(self):
        """Check if the configured splitter is available for the ensembler"""
        splitter_id = self.configs_['splitter']['id']
        if splitter_id == 'mangoml_sklearn_ShuffleSplit':
            return True
        elif splitter_id == 'mangoml_sklearn_StratifiedShuffleSplit':
            return True
        return False

    def build_splitter(self):
        """Build the configured splitter used for data splitting"""
        if not self.is_valid_splitter():
            print self.configs_['splitter']['id'], 'cannot be used for blending!'
            return None

        factory = SplitterFactory()
        return factory.build(self.configs_['splitter']['id'],
                             self.configs_['splitter']['parameters'])

    def fit(self, input_data, targets):
        """Train the full ensembler"""
        train_index, test_index = next(self.splitter_.split_arrays(input_data,
                                                                   targets))

        first_level_input = input_data[train_index]
        first_level_target = targets[train_index]
        combiner_input = input_data[test_index]
        combiner_target = targets[test_index]

        self.fit_first_level_models(first_level_input, first_level_target)
        formatted_combiner_input = self.predict_first_level_models(combiner_input)
        self.fit_combiner_model(formatted_combiner_input, combiner_target)
        self.fit_first_level_models(input_data, targets)
