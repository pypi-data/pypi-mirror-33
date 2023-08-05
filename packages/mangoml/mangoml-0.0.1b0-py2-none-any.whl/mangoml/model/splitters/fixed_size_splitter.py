"""Module that contains FixedSizeSplitter class"""
from sklearn.model_selection import PredefinedSplit

class FixedSizeSplitter(object):
    """Class used to split data in train and test sets with a fixed size for test"""
    def __init__(self, configs):
        self.test_size_ = configs['test_size']

    def split(self, data):
        """Perform a data split with a fixed size for the test set"""
        data_size = 0
        if data.is_row_split_validation():
            #Time series split data by columns
            data_size = data.get_features().shape[1]
        else:
            data_size = data.get_features().shape[0]

        test_fold = [-1 for i in range(0, data_size - self.test_size_)]
        test_fold += [0 for i in range(data_size - self.test_size_, data_size)]
        splitter = PredefinedSplit(test_fold=test_fold)
        return splitter.split()
