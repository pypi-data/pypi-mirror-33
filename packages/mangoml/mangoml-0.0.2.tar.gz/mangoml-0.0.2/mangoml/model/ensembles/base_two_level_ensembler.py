"""Module that contains BaseTwoLevelEnsembler abstract class"""
from abc import ABCMeta, abstractmethod
import numpy as np
from mangoml.model.base_model import BaseModel
from mangoml.model.pipeline_model import PipelineModel

class BaseTwoLevelEnsembler(BaseModel):
    """Abstract class that defines common methods for two level ensemblers"""
    __metaclass__ = ABCMeta
    def __init__(self, configs, score_method, predict_as_probability,
                 column_names):
        BaseModel.__init__(self, configs, score_method, predict_as_probability)
        self.combiner_model_ = None
        self.first_level_models_ = []
        self.column_names_ = column_names

    @abstractmethod
    def build_splitter(self):
        """Abstract method. Should build the splitter used by the ensembler"""
        pass

    @abstractmethod
    def fit(self, input_data, targets):
        """Abstract method. Should use the input_data to find the parameters
        of both the combiner model and the first level models"""
        pass

    def init(self):
        """Register all the configured models"""
        if not self.register_first_level_models():
            return False
        return self.register_combiner_model()

    def register_combiner_model(self):
        """Register the model used only to give weights to other models
        predictions (combiner model)"""
        combiner_model_config = self.configs_['combiner_model']
        combiner_model = PipelineModel(combiner_model_config, self.score_method_,
                                       self.predict_as_probability_,
                                       self.column_names_)
        if not combiner_model.init():
            return False
        self.combiner_model_ = combiner_model
        return True

    def register_first_level_models(self):
        """Register the models that will be ensembled (first level models)"""
        model_configs = self.configs_['first_level_models']

        for i in range(0, len(model_configs)):
            new_model = PipelineModel(model_configs[i], self.score_method_,
                                      self.predict_as_probability_,
                                      self.column_names_)

            if not new_model.init():
                print 'Error registering model', model_configs[i]['model']['id'],\
                  'in ensemble'
                return False
            print 'Model', new_model.get_name(), 'registered in ensemble'
            self.first_level_models_.append(new_model)

        return True

    def get_name(self):
        """Get the label associated with a model (used for printing)"""
        if 'label' in self.configs_:
            return self.configs_['label']
        return self.configs_['id']

    def fit_first_level_models(self, input_data, targets):
        """Train the models that will be ensembled"""
        for i in range(0, len(self.first_level_models_)):
            self.first_level_models_[i].fit(input_data, targets)

    def fit_combiner_model(self, input_data, targets):
        """Train the combiner model"""
        self.combiner_model_.fit(input_data, targets)

    def format_probability_prediction(self, first_level_prediction):
        """Method used to deal with the different shapes of probability
        predictions"""
        #If only 2 classes are used the features are redundant (P[0], 1-P[0])
        if self.predict_as_probability_ and len(first_level_prediction[0]) == 2:
            first_level_prediction = np.array([first_level_prediction[i][1]\
              for i in range(0, len(first_level_prediction))])
            first_level_prediction = first_level_prediction.reshape(-1, 1)
        else:
            first_level_prediction = first_level_prediction.reshape(-1,\
              len(first_level_prediction[0]))
        return first_level_prediction

    def predict_first_level_models(self, input_data):
        """Method that returns the predictions of the ensembled models"""
        predictions = []
        for i in range(0, len(self.first_level_models_)):
            first_level_prediction = self.first_level_models_[i].predict(input_data)

            if self.predict_as_probability_:
                first_level_prediction =\
                  self.format_probability_prediction(first_level_prediction)
            else:
                first_level_prediction = np.array(first_level_prediction).reshape(-1, 1)
            predictions.append(first_level_prediction)

        return np.concatenate(predictions, axis=1)

    def predict_combiner_model(self, input_data):
        """Method that returns the predicted weights of each ensembled model
        given by the combiner model"""
        return self.combiner_model_.predict(input_data)

    def predict(self, input_data):
        """Method that gives the full ensemble model prediction"""
        formatted_combiner_input = self.predict_first_level_models(input_data)
        return self.predict_combiner_model(formatted_combiner_input)
