"""Module that contains splitters based on datetime"""
from abc import ABCMeta, abstractmethod
import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset
from dateutil.relativedelta import relativedelta

class BaseDatetimeSplitter(object):
    """Abstract class that defines commom methods for splitters based on time"""
    __metaclass__ = ABCMeta
    def __init__(self, configs):
        self.date_column_ = configs.get('date_column', None)
        self.timescale_ = configs.get('timescale', 'days')
        self.configs_ = configs
        self.period_start_ = None
        self.period_end_ = None
        self.sliding_window_size_ = None

    def subtract_interval(self, datetime, interval):
        """Subtract an interval from a datetime using the configured timescale"""
        if self.timescale_ == 'years':
            return datetime - DateOffset(years=interval)
        elif self.timescale_ == 'months':
            return datetime - DateOffset(months=interval)
        elif self.timescale_ == 'days':
            return datetime - DateOffset(days=interval)
        elif self.timescale_ == 'hours':
            return datetime - DateOffset(hours=interval)
        elif self.timescale_ == 'minutes':
            return datetime - DateOffset(minutes=interval)
        elif self.timescale_ == 'seconds':
            return datetime - DateOffset(seconds=interval)
        return None

    def add_interval(self, datetime, interval):
        """Add an interval to a datetime using the configured timescale"""
        if self.timescale_ == 'years':
            return datetime + DateOffset(years=interval)
        elif self.timescale_ == 'months':
            return datetime + DateOffset(months=interval)
        elif self.timescale_ == 'days':
            return datetime + DateOffset(days=interval)
        elif self.timescale_ == 'hours':
            return datetime + DateOffset(hours=interval)
        elif self.timescale_ == 'minutes':
            return datetime + DateOffset(minutes=interval)
        elif self.timescale_ == 'seconds':
            return datetime + DateOffset(seconds=interval)
        return None

    def subtract_datetimes(self, last_datetime, first_datetime):
        """Subtract two datetimes using the configured timescale"""
        if self.timescale_ == 'years':
            return relativedelta(last_datetime, first_datetime).years
        elif self.timescale_ == 'days':
            return (last_datetime.date() - first_datetime.date()).days
        elif self.timescale_ == 'hours':
            return int((last_datetime - first_datetime).total_seconds() // 3600)
        elif self.timescale_ == 'minutes':
            return int((last_datetime - first_datetime).total_seconds() // 60)
        elif self.timescale_ == 'seconds':
            return int((last_datetime - first_datetime).total_seconds())
        return None

    def get_last_date(self, data):
        """Return the latest date from the considered dates"""
        if data.is_row_split_validation():
            dates = data.get_feature_names()
            max_date = None
            for date in dates:
                cur_date = pd.to_datetime(date)
                if max_date is None or max_date < cur_date:
                    max_date = cur_date
        else:
            max_date = data.get_engine().get_column_max(self.date_column_)
        return max_date

    def get_first_date(self, data):
        """Return the earliest date from the considered dates"""
        if data.is_row_split_validation():
            dates = data.get_feature_names()
            min_date = None
            for date in dates:
                cur_date = pd.to_datetime(date)
                if min_date is None or min_date > cur_date:
                    min_date = cur_date
        else:
            min_date = data.get_engine().get_column_min(self.date_column_)
        return min_date

    def get_timediff_map(self, data):
        """Return a map with the time difference to period_end as key and the
        array index as value"""
        self.set_time_window_parameters(data, self.configs_)
        if data.is_row_split_validation():
            #Time series split data by columns
            dates = data.get_feature_names()
        else:
            dates = data.get_engine().get_column_as_array(self.date_column_)

        timediff_map = {}
        date_index = 0
        for date in dates:
            cur_date = pd.to_datetime(date)
            if self.subtract_datetimes(self.period_end_, cur_date) < 0:
                #Date after the configured period ending. Ignore it
                date_index += 1
                continue
            elif self.subtract_datetimes(self.period_start_, cur_date) > 0:
                #Date before the configured period starting point.
                #Always use it as training data (-1)
                if -1 not in timediff_map:
                    timediff_map[-1] = []
                timediff_map[-1].append(date_index)
            else:
                #The map key is the time passed since the start date
                timediff = self.subtract_datetimes(cur_date, self.period_start_)
                if timediff not in timediff_map:
                    timediff_map[timediff] = []
                timediff_map[timediff].append(date_index)
            date_index += 1
        return timediff_map

    @abstractmethod
    def set_time_window_parameters(self, data, configs):
        """Abstract method. Should set the time window parameters"""
        pass

    @abstractmethod
    def split(self, data):
        """Abstract method. Should split the data using datetime."""
        pass

class FixedTimeWindowSplitter(BaseDatetimeSplitter):
    """Class used to split data in train and test sets using a fixed datetime as
    the split point"""
    def __init__(self, configs):
        BaseDatetimeSplitter.__init__(self, configs)

    def set_time_window_parameters(self, data, configs):
        """Set the fixed time window parameters"""
        if 'validation_period_end' in configs:
            self.period_end_ = pd.to_datetime(configs['validation_period_end'])
        else:
            if 'fixed_time_window_size' in configs and\
                'validation_period_start' in configs:
                self.period_start_ = pd.to_datetime(configs['validation_period_start'])
                period_interval = int(configs['fixed_time_window_size']) - 1
                self.period_end_ = self.add_interval(self.period_start_,
                                                     period_interval)
            else:
                last_date = self.get_last_date(data)
                self.period_end_ = pd.to_datetime(last_date)

        if 'validation_period_start' in configs:
            self.period_start_ = pd.to_datetime(configs['validation_period_start'])
        else:
            #Interval period configured contains the last date
            period_interval = int(configs['fixed_time_window_size']) - 1
            self.period_start_ = self.subtract_interval(self.period_end_,
                                                        period_interval)

    def split(self, data):
        """Perform a train/test split using datetime as the split point"""
        timediff_map = self.get_timediff_map(data)
        train_fold = timediff_map[-1]
        test_fold = []
        for timediff in sorted(timediff_map.keys()):
            if timediff == -1:
                continue
            test_fold += timediff_map[timediff]
        data_split = [(np.array(train_fold), np.array(test_fold))]
        return data_split

class MovingTimeWindowSplitter(BaseDatetimeSplitter):
    """Class used to split data in multiple folds using a moving time
    window for the test fold (similar to TimeSeriesSplit from sklearn)"""
    def __init__(self, configs):
        BaseDatetimeSplitter.__init__(self, configs)

    def set_time_window_parameters(self, data, configs):
        """Set the moving time window parameters"""
        if 'validation_period_end' in configs:
            self.period_end_ = pd.to_datetime(configs['validation_period_end'])
        else:
            last_date = self.get_last_date(data)
            self.period_end_ = pd.to_datetime(last_date)

        if 'validation_period_start' in configs:
            self.period_start_ = pd.to_datetime(configs['validation_period_start'])
        else:
            first_date = self.get_first_date(data)
            self.period_start_ = pd.to_datetime(first_date)
        self.sliding_window_size_ = configs.get('sliding_time_window_size', 1)

    def get_training_window(self, timediff_map, test_timediff):
        """Returns a training window with all samples from a previous datetime"""
        cv_train_fold = []
        previous_datetimes = [elem for elem in timediff_map.keys() if elem < test_timediff]
        for previous_timediff in sorted(previous_datetimes):
            cv_train_fold += timediff_map[previous_timediff]
        return cv_train_fold

    def change_time_window_size(self, previous_timediff_map):
        """Create a new timediff map using the configured sliding window"""
        new_timediff_map = {}
        for timediff in sorted(previous_timediff_map.keys()):
            if timediff == -1:
                new_timediff_map[timediff] = previous_timediff_map[timediff]
            else:
                timediff_window = timediff // self.sliding_window_size_
                if timediff_window not in new_timediff_map:
                    new_timediff_map[timediff_window] = []
                new_timediff_map[timediff_window] += previous_timediff_map[timediff]
        return new_timediff_map

    def split(self, data):
        """Perform a moving time window split"""
        timediff_map = self.get_timediff_map(data)
        if self.sliding_window_size_ != 1:
            timediff_map = self.change_time_window_size(timediff_map)

        data_split = []
        min_timediff = min(timediff_map.keys())
        for timediff in sorted(timediff_map.keys()):
            if timediff == min_timediff:
                #Used only for training
                continue
            cv_test_fold = timediff_map[timediff]
            cv_train_fold = self.get_training_window(timediff_map, timediff)
            data_split.append((np.array(cv_train_fold), np.array(cv_test_fold)))
        return data_split
