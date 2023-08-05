# mango

mango (MAchine learniNG Orchestra) is a python API for quick machine learning experimentation. The idea is to read data from a CSV file and compare different machine learning models using cross-validation.

Much of the operations used to read the data and test machine learning models are repeated for different experiments and the goal here is to avoid this repetition by implementing wrappers of object from the main python libraries used in data science (e.g. [scikit-learn](https://github.com/scikit-learn/scikit-learn), [pandas](https://github.com/pandas-dev/pandas) and [xgboost](https://github.com/dmlc/xgboost)).

Most of the configuration needed is made through a JSON file. The JSON objects are read by wrappers for objects from different APIs. The parameters configured through JSON are the same used by scikit/pandas/xgboost objects so you don't need to code everything again.

I've created this API to make it easier to participate in [Kaggle](https://www.kaggle.com/) competitions. I used the classic [Titanic Competition](https://www.kaggle.com/c/titanic) as an example of mango utilization.

Any suggestions can be send to my email: gustavohas@outlook.com
