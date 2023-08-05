"""Module that contains SplitterFactory class"""
from sklearn import model_selection
from mangoml.model.splitters.splitter_wrapper import SplitterWrapper
from mangoml.model.splitters.fixed_size_splitter import FixedSizeSplitter
from mangoml.model.splitters.datetime_splitter import FixedTimeWindowSplitter,\
    MovingTimeWindowSplitter

class SplitterFactory(object):
    """Class responsible for building data splitters (used for model
    evaluation)"""

    def build_sklearn(self, splitter_id, splitter_params):
        """Build splitters wrapping sklearn"""
        if splitter_id == 'mangoml_sklearn_KFold':
            return SplitterWrapper(model_selection.KFold(**splitter_params))
        elif splitter_id == 'mangoml_sklearn_StratifiedKFold':
            return SplitterWrapper(model_selection.StratifiedKFold(**splitter_params))
        elif splitter_id == 'mangoml_sklearn_ShuffleSplit':
            return SplitterWrapper(model_selection.ShuffleSplit(**splitter_params))
        elif splitter_id == 'mangoml_sklearn_StratifiedShuffleSplit':
            return SplitterWrapper(model_selection.StratifiedShuffleSplit(**splitter_params))
        elif splitter_id == 'mangoml_sklearn_GroupKFold':
            group_column = splitter_params.pop('group_column')
            return SplitterWrapper(model_selection.GroupKFold(**splitter_params),
                                   group_column)
        return None

    def build_mangoml(self, splitter_id, splitter_params):
        """Build mangoml splitters"""
        if splitter_id == 'mangoml_FixedSizeSplitter':
            return FixedSizeSplitter(splitter_params)
        elif splitter_id == 'mangoml_FixedTimeWindowSplitter':
            return FixedTimeWindowSplitter(splitter_params)
        elif splitter_id == 'mangoml_MovingTimeWindowSplitter':
            return MovingTimeWindowSplitter(splitter_params)
        return None

    def build(self, splitter_id, splitter_params):
        """Build a data splitter using the specified id"""
        if 'sklearn' in splitter_id:
            return self.build_sklearn(splitter_id, splitter_params)
        elif 'mangoml' in splitter_id:
            return self.build_mangoml(splitter_id, splitter_params)
        return None
