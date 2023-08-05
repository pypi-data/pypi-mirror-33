from sklearn.base import BaseEstimator, TransformerMixin

class Whiten(BaseEstimator, TransformerMixin):
    def __init__(self, assumed_centered=False, copy=True):
        self.assume_centered = assume_centered
        self.copy = copy

    def fit_transform(self, X):
        n_samples = X.shape[0]

        if self.copy:
            X = X - np.mean(X, axis=0)
        else:
            X -= np.mean(X, axis=0)

        Q, R = linalg.qr(X, mode='economic')

        self.R_ = np.sqrt(n_samples) * R

        return np.sqrt(n_samples) * Q

    def inverse_transform(self, X):
        return linalg.solve_triangular(self.R_, X)
