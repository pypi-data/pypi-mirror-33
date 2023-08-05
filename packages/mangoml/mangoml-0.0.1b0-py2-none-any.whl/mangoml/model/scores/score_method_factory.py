"""Module that contains ScoreMethodFactory class"""
from mangoml.model.scores.scorer import Scorer

class ScoreMethodFactory(object):
    """Class responsible for returning the specified scoring function"""
    def build(self, configs):
        """Method that returns the scoring method"""
        if configs["scorer"]["id"] == "log_loss":
            return Scorer.log_loss
        elif configs["scorer"]["id"] == "roc_auc":
            return Scorer.roc_auc
        elif configs["scorer"]["id"] == "accuracy":
            return Scorer.accuracy
        elif configs["scorer"]["id"] == "mean_f1_score":
            return Scorer.mean_f1_score
        elif configs["scorer"]["id"] == "rmsle":
            return Scorer.rmsle
        elif configs["scorer"]["id"] == "rmse":
            return Scorer.rmse
        elif configs["scorer"]["id"] == "mse":
            return Scorer.mse
        elif configs["scorer"]["id"] == "smape":
            return Scorer.smape
        elif configs["scorer"]["id"] == "precision_score":
            return Scorer.precision_score
        elif configs["scorer"]["id"] == "recall_score":
            return Scorer.recall_score
        elif configs["scorer"]["id"] == "normalized_gini":
            return Scorer.normalized_gini
        return None
