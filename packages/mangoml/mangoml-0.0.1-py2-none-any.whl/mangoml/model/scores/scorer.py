"""Module that contains a Scorer class with all implemented scoring methods"""
import numpy as np
import sklearn.metrics as skmetrics

class Scorer(object):
    """Class that contains all scoring methods used during model comparison"""
    @staticmethod
    def log_loss(predicted, target):
        """Calculates the log loss"""
        return skmetrics.log_loss(target, predicted)

    @staticmethod
    def roc_auc(predicted, target):
        """Calculates the area under the ROC curve"""
        return skmetrics.roc_auc_score(target, predicted)

    @staticmethod
    def accuracy(predicted, target):
        """Calculates the fraction of correct classification predictions"""
        return skmetrics.accuracy_score(target, predicted)

    @staticmethod
    def mean_f1_score(predicted, target):
        """Calculates the mean F1 score"""
        return skmetrics.f1_score(target, predicted, average='weighted')

    @staticmethod
    def precision_score(predicted, target):
        """Calculates the precision"""
        return skmetrics.precision_score(target, predicted)

    @staticmethod
    def recall_score(predicted, target):
        """Calculates the recall"""
        return skmetrics.recall_score(target, predicted)

    @staticmethod
    def rmsle(predicted, target):
        """Calculates the root mean squared logarithimic error"""
        #Obtained from kaggle
        total = 0.0
        for i in range(len(predicted)):
            p = np.log(predicted[i] + 1)
            r = np.log(target[i] + 1)
            total = total + (p - r)**2
        return (total/len(predicted))**0.5

    @staticmethod
    def rmse(predicted, target):
        """Calculates the root mean squared error"""
        return skmetrics.mean_squared_error(target, predicted)**0.5

    @staticmethod
    def mse(predicted, target):
        """Calculates the mean squared error"""
        return skmetrics.mean_squared_error(target, predicted)

    @staticmethod
    def smape(predicted, target):
        """Calculates the symmetric mean absolute percentage error"""
        #Obtained from kaggle
        valid_datapoints = ~np.isnan(target)
        target, predicted = target[valid_datapoints], predicted[valid_datapoints]
        raw_smape = np.abs(target - predicted) / (np.abs(target) + np.abs(predicted))
        kaggle_smape = np.nan_to_num(raw_smape)
        return np.mean(kaggle_smape) * 200

    @staticmethod
    def gini(target, predicted):
        """Calculates the gini coefficient"""
        return 2 * skmetrics.roc_auc_score(target, predicted) - 1

    @staticmethod
    def normalized_gini(predicted, target):
        """Calculates the normalized gini coefficient"""
        if predicted.shape[1] == 2:
            predicted = np.array([elem[1] for elem in predicted])
            return float(Scorer.gini(target, predicted)) / Scorer.gini(target, target)
        return float(Scorer.gini(target, predicted)) / Scorer.gini(target, target)
