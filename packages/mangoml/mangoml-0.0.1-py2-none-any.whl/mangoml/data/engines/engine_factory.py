"""Module that contains EngineFactory class"""
from mango.data.engines.pandas_engine import PandasEngine

class EngineFactory(object):
    """Class responsible for building engines"""
    def __init__(self, configs):
        self.configs_ = configs

    def build(self):
        """Build the engine"""
        if self.configs_['id'] == 'pandas':
            return PandasEngine(self.configs_)
