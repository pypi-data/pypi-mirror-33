"""Module that contains PandasEngine class"""
import pandas as pd
import numpy as np

class PandasEngine(object):
    """The engine of Pandas. This class is "stateless" so all methods that
    modify the engine content return a new engine object"""
    def __init__(self, configs, dataframe=None):
        self.configs_ = configs
        if dataframe is None:
            if configs['mode'] == 'read':
                self.dataframe_ = pd.read_csv(**configs['parameters'])
            else:
                self.dataframe_ = pd.DataFrame()
        else:
            self.dataframe_ = dataframe

    def get_column_as_array(self, column_name):
        """Get a CSV column as a numpy array"""
        return self.dataframe_[column_name].as_matrix()

    def get_column_names(self):
        """Return a list with the names of all columns"""
        return self.dataframe_.columns.values.tolist()

    def get_string_column_names(self):
        """Return a list with the names of all string columns"""
        #Filtering all numeric columns
        str_dataframe = self.dataframe_.select_dtypes(include=['object'])
        return str_dataframe.columns.values.tolist()

    def get_numeric_column_names(self):
        """Return a list with the names of all numeric columns"""
        #Filtering only numeric columns
        num_dataframe = self.dataframe_.select_dtypes(include=[np.number])
        return num_dataframe.columns.values.tolist()

    def get_column_missing_fraction(self, column_name):
        """Return the fraction of missing data for a specific column"""
        num_missing_rows = sum(self.dataframe_[column_name].
                               isnull().values.ravel())
        return float(num_missing_rows) / self.dataframe_.shape[0]

    def get_column_mean(self, column_name):
        """Return the column mean"""
        return self.dataframe_[column_name].mean()

    def get_column_max(self, column_name):
        """Return the column maximum value"""
        return self.dataframe_[column_name].max()

    def get_column_min(self, column_name):
        """Return the column minimum value"""
        return self.dataframe_[column_name].min()

    def get_column_median(self, column_name):
        """Return the column median"""
        return self.dataframe_[column_name].median()

    def get_table_as_matrix(self):
        """Return the full table"""
        return self.dataframe_.as_matrix()

    def erase_columns(self, column_list):
        """Erase a list of columns and return a new PandasEngine"""
        new_dataframe = self.dataframe_.copy()
        new_dataframe = new_dataframe.drop(column_list, 1)
        return PandasEngine(self.configs_, new_dataframe)

    def set_column(self, column_name, column_values):
        """Set a column value and return a new PandasEngine"""
        new_dataframe = self.dataframe_.copy()
        new_dataframe[column_name] = column_values
        return PandasEngine(self.configs_, new_dataframe)

    def add_column(self, column_name, column_values):
        """Add a new column and return a new PandasEngine"""
        return self.set_column(column_name, column_values)

    def set_table_from_dict(self, data_dict):
        """Set the data table from a dictionary"""
        new_dataframe = pd.Dataframe.from_dict(data_dict)
        return PandasEngine(self.configs_, new_dataframe)

    def rename_columns(self, rename_dict):
        """Rename a list of columns"""
        new_dataframe = self.dataframe_.copy()
        new_dataframe = new_dataframe.rename(columns=rename_dict)
        return PandasEngine(self.configs_, new_dataframe)

    def concatenate_columns(self, column_input_1, column_input_2,
                            column_output):
        """Concatenate columns and save it in column_output"""
        new_dataframe = self.dataframe_.copy()
        new_dataframe[column_output] = new_dataframe[column_input_1].\
            astype(str) + new_dataframe[column_input_2].astype(str)
        return PandasEngine(self.configs_, new_dataframe)

    def concatenate_column_and_string(self, column_input, str_value,
                                      column_output):
        """Concatenate column with a string and save it in column_output"""
        new_dataframe = self.dataframe_.copy()
        new_dataframe[column_output] = new_dataframe[column_input]\
            .astype(str) + str_value
        return PandasEngine(self.configs_, new_dataframe)

    def fill_column_missing_values(self, column_name, fill_value):
        """Fill all missing values with fill_value"""
        new_dataframe = self.dataframe_.copy()
        new_dataframe[column_name] = new_dataframe[column_name].fillna(
            fill_value)
        return PandasEngine(self.configs_, new_dataframe)

    def sort_by_column(self, column_name):
        """Sort the table using the specified column"""
        new_dataframe = self.dataframe_.copy()
        new_dataframe = new_dataframe.sort_values(column_name)
        return PandasEngine(self.configs_, new_dataframe)

    def build_file(self, configs):
        """Create an output file with the data table"""
        self.dataframe_.to_csv(**configs['parameters'])
