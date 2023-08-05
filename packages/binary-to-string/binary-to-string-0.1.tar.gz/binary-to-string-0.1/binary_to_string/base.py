from sklearn.base import TransformerMixin, BaseEstimator
import numpy as np


class BinaryToString(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_decoded = list(map(lambda text: text.decode('utf-8') if type(text) == bytes else text, X))
        return np.array(X_decoded)
