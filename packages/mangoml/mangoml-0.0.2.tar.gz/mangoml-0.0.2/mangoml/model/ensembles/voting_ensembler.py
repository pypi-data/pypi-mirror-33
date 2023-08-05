"""Module that contains VotingEnsembler class"""
from sklearn.ensemble import VotingClassifier
from mangoml.model.base_model import BaseModel
from mangoml.model.pipeline_model import PipelineModel

class VotingEnsembler(BaseModel):
    """Class that combines models using a voting method. A hard voting method is
    equivalent to a majority voting. A soft voting returns the class with the
    highest probability (calculated as the sum of the probabilities predicted by
    each model)"""
    def __init__(self, configs, score_method, predict_as_probability,
                 voting_method):
        BaseModel.__init__(self, configs, score_method, predict_as_probability)
        self.models_ = []
        self.model_weights_ = []
        self.voting_method_ = voting_method
        self.ensemble_model_ = None

    def init(self):
        """Method responsible for the ensembler initialization"""
        if not self.register_models():
            return False

        self.ensemble_model_ = VotingClassifier(estimators=self.models_,\
          voting=self.voting_method_, weights=self.model_weights_)
        return True

    def register_models(self):
        """Method used to register the prediction models"""
        models = self.configs_['pipeline_models']

        for i in range(0, len(models)):
            new_model = PipelineModel(models[i], self.score_method_,
                                      self.predict_as_probability_)

            if not new_model.init():
                print 'Error registering model', models[i]['model']['id'],\
                  'in ensemble'
                return False
            print 'Model', new_model.get_name(), 'registered in ensemble'
            self.models_.append((models[i]['model']['id'],
                                 new_model.get_sklearn_pipeline()))

            if 'weight' not in models[i]:
                self.model_weights_.append(1)
            else:
                self.model_weights_.append(models[i]['weight'])
        return True

    def get_name(self):
        """Get the label associated with a model (used for printing)"""
        if 'label' in self.configs_:
            return self.configs_['label']
        return self.configs_['id']

    def fit(self, input_data, targets):
        """Train the ensemble model"""
        self.ensemble_model_.fit(input_data, targets)

    def predict(self, input_data):
        """Predict the results of an ensemble model"""
        if not self.predict_as_probability_:
            return self.ensemble_model_.predict(input_data)
        else:
            return self.ensemble_model_.predict_proba(input_data)
