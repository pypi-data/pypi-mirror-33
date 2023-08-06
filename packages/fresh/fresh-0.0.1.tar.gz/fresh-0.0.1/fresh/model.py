# -*- coding: utf-8 -*-

import logging
from sklearn.base import BaseEstimator
from fresh.pipeline import PipeBuilder


class Model(BaseEstimator):
    """
    Basically a wrapper around .pipeline which handles the actual transformation and training of the model.
    This serves as a transparent wrapper to the raw data and following construction and training of multiple models
    and variations to find the best one.
    """

    target = None
    pipeline = None
    logger = logging.getLogger(__name__)

    def fit(self, X, y):
        if y.name in X.columns:
            self.logger.warning('Found target columns "{}" in X, deleting it!'.format(y.name))
            del X[y.name]
        self.pipeline = PipeBuilder.from_data(X, y)
        self.pipeline.fit(X, y)
        return self

    def predict(self, X):
        return self.pipeline.predict(X)

    def score(self, X, y, *args, **kwargs):
        return self.pipeline.score(X, y, *args, **kwargs)
