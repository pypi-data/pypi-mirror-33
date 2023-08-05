"""Module that contains SplitterWrapper class"""

class SplitterWrapper(object):
    """Class used to wrap splitting methods from other libraries"""
    def __init__(self, splitter, group_column=''):
        self.splitter_ = splitter
        self.group_column_ = group_column

    def split_arrays(self, features, targets):
        """Split features and targets as arrays using the configured splitter"""
        return self.splitter_.split(features, targets)

    def split(self, data):
        """Split data using the configured splitter"""
        if len(self.group_column_) > 0:
            groups = data.get_engine().get_column_as_array(self.group_column_)
            return self.splitter_.split(data.get_features(), data.get_targets(),
                                        groups)
        return self.splitter_.split(data.get_features(), data.get_targets())
