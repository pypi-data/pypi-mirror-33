"""Module that contains Result class"""

class Result(object):
    """Class that generates result file"""
    def __init__(self, configs, engine):
        self.configs_ = configs
        self.engine_ = engine
        self.rename_features()
        self.erase_features()

    def add_feature(self, feature_name, feature_value):
        """Add features to result"""
        self.engine_ = self.engine_.add_column(feature_name, feature_value)

    def add_prediction(self, prediction_label, prediction_results):
        """Add the prediction column to result"""
        self.engine_ = self.engine_.add_column(prediction_label,
                                               prediction_results)

    def erase_features(self):
        """Erase features from result"""
        if 'columns_to_remove' in self.configs_:
            self.engine_ = self.engine_.erase_columns(
                self.configs_['columns_to_remove'])

    def rename_features(self):
        """Rename a list of features"""
        if 'columns_to_rename' in self.configs_:
            self.engine_ = self.engine_.rename_columns(
                self.configs_['columns_to_rename'])

    def sort(self, feature_name):
        """Sort the results using a feature name"""
        self.engine_ = self.engine_.sort_by_column(feature_name)

    def build_file(self):
        """Create a output file with results"""
        self.engine_.build_file(self.configs_['engine'])

    def set_custom_engine(self, engine):
        """Set a customized engine for Result. Used for customized output"""
        self.engine_ = engine

    def get_engine(self):
        """Return the internal engine"""
        return self.engine_
