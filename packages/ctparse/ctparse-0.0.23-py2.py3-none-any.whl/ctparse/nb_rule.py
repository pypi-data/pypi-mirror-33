import logging
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

logger = logging.getLogger(__name__)


def _id(x):
    # can not pickle models if using a lambda below
    parts = x.split(' ')
    return [' '.join(parts[:3]), ' '.join(parts[-3:]), parts[2], parts[4]]


class NBRule:
    def __init__(self):
        self._model = None

    def fit(self, X, y):
        self._model = make_pipeline(
            CountVectorizer(ngram_range=(1, 1), lowercase=False,
                            tokenizer=_id),
            MultinomialNB(alpha=1.0))
        self._model.fit(X, y)
        # Make sure that class order is 0, 1
        assert self._model.classes_[0] == 0
        return self

    def predict(self, X):
        """wrapper to predict - if no model is fitted, return 0.0 for all samples"""
        if self._model is None:
            return [0.0 for x in X]
        pred = self._model.predict_proba(X)
        return pred[:, 1]

    def map_prod(self, prod, y=None):
        """given one production, transform it into all sub-sequences of len 1 - len(prod)"""
        Xs = []
        ys = []
        for i in range(1, len(prod)):
            Xs.append([str(w) for w in prod[:i]])
            ys.append(1 if y else -1)
        if not Xs:
            return [[]], [-1]
        return Xs, ys

    def apply(self, x):
        """apply model to a single data point"""
        return self.predict([x])[0]
