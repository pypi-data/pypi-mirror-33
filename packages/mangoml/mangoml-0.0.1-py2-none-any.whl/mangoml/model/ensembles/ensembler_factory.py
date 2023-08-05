"""Module that contains EnsemblerFactory class"""
from mango.model.ensembles.voting_ensembler import VotingEnsembler
from mango.model.ensembles.two_level_ensemblers import BlendingEnsembler
from mango.model.ensembles.two_level_ensemblers import StackingEnsembler

class EnsemblerFactory(object):
    """Class responsible for building ensemblers"""
    def build(self, ensemble_id, configs, score_method, predict_as_probability,
              column_names):
        """Method that returns the configured ensembler object"""
        if ensemble_id == "mango_sklearn_MajorityVotingEnsembler":
            return VotingEnsembler(configs, score_method,
                                   predict_as_probability, 'hard')
        elif ensemble_id == "mango_sklearn_ProbabilityVotingEnsembler":
            return VotingEnsembler(configs, score_method,
                                   predict_as_probability, 'soft')
        elif ensemble_id == "mango_BlendingEnsembler":
            return BlendingEnsembler(configs, score_method,
                                     predict_as_probability, column_names)
        elif ensemble_id == "mango_StackingEnsembler":
            return StackingEnsembler(configs, score_method,
                                     predict_as_probability, column_names)
        return None
