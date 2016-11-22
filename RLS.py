import numpy as np
import sklearn.preprocessing as prep
import statsmodels.api as sm
import matplotlib.pyplot as plt

class RLS(object):
    
    def __init__(self, lambd=0.98):
        
        self.__lambd = lambd
    
    @property
    def lambd(self):
        
        return self.__lambd
    
    @property
    def weight(self):
        
        return self.__weight
    
    @property
    def proj(self):
        
        return self.__proj
    
    def fit(self, X, y):
        
        self.__scaler = prep.StandardScaler(with_mean=False)
        
        X_std = self.__scaler.fit_transform(X)
        
        self.__weight = np.zeros(X_std.shape[1])
        self.__proj   = np.eye(X_std.shape[1])
        
        for xi, yi in zip(X_std, y):
            alpha = yi - np.dot(xi, self.__weight)
            g = 1. / (self.__lambd + np.dot(xi, np.dot(self.__proj, xi))) *  np.dot(self.__proj, xi)
            self.__proj = 1. / self.__lambd * (self.__proj - np.outer(g, np.dot(xi, self.__proj)))
            self.__weight += alpha * g
        
        return self
    
    def predict(self, X):
        
        X_std = self.__scaler.transform(X)
        
        return np.dot(X_std, self.__weight)

if __name__ == "__main__":
    
    #nSize = 100
    #np.random.seed(0)
    #X = np.array([np.random.rand(nSize)-0.5], dtype=float).reshape((nSize,1))
    #y = 0.3 + np.ravel(0.5*X) + np.random.normal(scale=0.1, size=nSize)
    
    X = np.array([[1, 9], [2, 8], [3, 7], [4, 6], [5, 5], [6, 4]], dtype=float)
    y = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    
    rls = RLS(lambd=1.).fit(X,y)
    y_pred = rls.predict(X)
    
    model = sm.OLS(y, X)
    result = model.fit()
    print(result.summary())
    
    plt.figure()
    plt.scatter(y_pred, y)
    plt.show()
    
    print(rls.weight)
