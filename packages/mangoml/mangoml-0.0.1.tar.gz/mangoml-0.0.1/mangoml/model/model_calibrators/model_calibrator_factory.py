"""Module that contains ModelCalibratorFactory class"""
from sklearn import calibration
from sklearn import model_selection
from sklearn import multiclass

class ModelCalibratorFactory(object):
    """Class responsible for building model calibrators. These objects are
    used after training to calibrate the performance of the final model"""

    def build(self, input_model, model_calibrator_id, model_calibrator_params):
        """Build a model calibrator using the specified id"""
        if model_calibrator_id == 'sklearn_CalibratedClassifierCV':
            params = model_calibrator_params
            params['base_estimator'] = input_model
            return calibration.CalibratedClassifierCV(**params)
        elif model_calibrator_id == 'sklearn_GridSearchCV':
            params = model_calibrator_params
            params['estimator'] = input_model
            return model_selection.GridSearchCV(**params)
        elif model_calibrator_id == 'sklearn_OneVsRestClassifier':
            params = model_calibrator_params
            params['estimator'] = input_model
            return multiclass.OneVsRestClassifier(**params)
        elif model_calibrator_id == 'sklearn_OneVsOneClassifier':
            params = model_calibrator_params
            params['estimator'] = input_model
            return multiclass.OneVsOneClassifier(**params)
        return None
