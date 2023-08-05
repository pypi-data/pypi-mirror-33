"""Module that contains ProphetWrapper class"""
import datetime
from fbprophet import Prophet
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin

class ProphetWrapper(BaseEstimator, RegressorMixin):
    """Scikit wrapper to Prophet API"""
    def __init__(self, beg_date='', predict_interval=0,\
        yearly_seasonality=False, changepoint_prior_scale=0.05):
        self.beg_date = beg_date
        self.predict_interval = predict_interval
        self.yearly_seasonality = yearly_seasonality
        self.changepoint_prior_scale = changepoint_prior_scale

    def generate_date_interval(self, beg_date, date_interval):
        """Generate an array with the specified time interval"""
        beg_datetime = datetime.datetime.strptime(beg_date, '%Y-%m-%d')
        end_datetime = beg_datetime + datetime.timedelta(days=date_interval-1)
        end_date = end_datetime.strftime('%Y-%m-%d')
        return pd.date_range(beg_date, end_date).strftime('%Y-%m-%d')

    def get_fit_dataframe(self, time_series, dates):
        """Create a dataframe used by Prophet fitting method"""
        fit_df = pd.DataFrame()
        fit_df['ds'] = dates
        fit_df['y'] = time_series
        return fit_df

    def fit(self, X, y=None):
        """Fit the internal model"""
        self.model_list_ = []
        date_interval = X.shape[1]
        dates = self.generate_date_interval(self.beg_date, date_interval)
        for i in range(0, len(X)):
            fit_df = self.get_fit_dataframe(X[i], dates)
            model = Prophet(yearly_seasonality=self.yearly_seasonality,\
              changepoint_prior_scale=self.changepoint_prior_scale)
            model.fit(fit_df)
            self.model_list_.append(model)
        return self

    def predict(self, X):
        """Predict based on the fitted model"""
        #We need to fit it again if this is used to evaluate training performance!
        self.fit(X)

        getattr(self, 'model_list_', None)
        if self.model_list_ is None:
            return np.array()

        predictions = []
        pred_df = self.model_list_[0].make_future_dataframe(
            periods=self.predict_interval, include_history=False)
        for i in range(0, len(X)):
            forecast = self.model_list_[i].predict(pred_df)
            predictions.append(forecast['yhat'].as_matrix())
        return np.array(predictions)
