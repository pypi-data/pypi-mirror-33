# -*- coding:utf-8 -*-

"""
- 目前支持二元响应变量和多元响应变量
- 结果经过检验，和stata的logit回归结果一致
"""

from __future__ import division, absolute_import

import scipy.optimize as so
from simple_ml.base.base_model import *
from simple_ml.evaluation import *
import numpy as np
from simple_ml.base.base_enum import *
from simple_ml.base.base_error import *


__all__ = ['LogisticRegression', 'Lasso', 'Ridge']


class LogisticRegression(BaseClassifier, Multi2Binary):

    __doc__ = "Logistic Regression"

    def __init__(self, tol=0.01, alpha=0.01, threshold=0.5, has_intercept=True):
        """
        不包含惩罚项的Logistic回归
        :param tol:            误差容忍度，越大时收敛越快，但是越不精确
        :param alpha:           步长，梯度下降的参数
        :param threshold:      决策阈值，当得到的概率大于等于阈值时输出1，否则输出0
        :param has_intercept:  是否包含截距项
        """
        super(LogisticRegression, self).__init__()
        self.tol = tol
        self.alpha = alpha
        self.has_intercept = has_intercept
        self.threshold = threshold
        self.w = None

    @property
    def weight(self):
        return self.w

    @staticmethod
    def _sigmoid(x):
        return 1 / (1 + np.exp(-x))

    def _update_w(self, w_old, *args):
        sigmoid_array = self._sigmoid(np.dot(self.x, w_old.reshape(-1, 1)).reshape(1, -1)[0])
        epsilon_array = self.y - sigmoid_array
        w_new = w_old + self.alpha * np.dot(self.x.T, epsilon_array)
        return w_new

    def _loss_function_value(self, w):
        sigmoid_array = self._sigmoid(np.dot(self.x, w.reshape(-1, 1)).reshape(1, -1)[0])    # 存在重复计算的问题
        return -1 / self.variable_num * np.sum(self.y * np.log(sigmoid_array) + (1 - self.y) *
                                               np.log(1 - sigmoid_array))

    @staticmethod
    def _add_ones(x):
        return np.column_stack((np.ones(x.shape[0]), x))

    def _init(self, x, y):
        super(LogisticRegression, self)._init(x, y)
        if self.has_intercept and not (self.x[:, 0] == 1).all() and x.shape[1] > 1:
            self.x = self._add_ones(self.x)
            self.variable_num += 1

    def fit(self, x, y):
        super(LogisticRegression, self).fit(x, y)
        if self.label_type == LabelType.multi_class:
            self._multi_fit(self)
        elif self.label_type == LabelType.binary:
            self.w, _ = self._fit()
            if len(self.w) != self.variable_num:
                raise FeatureNumberMismatchError
        else:
            raise LabelTypeError("Logistic回归不支持连续标签")

    def _fit(self):
        """
        梯度下降进行求解
        ref: http://m.blog.csdn.net/zjuPeco/article/details/77165974
        """
        w_old = np.zeros(self.variable_num)
        loss_init = self._loss_function_value(w_old)
        t = np.Inf
        loss_new = loss_init
        while t > self.tol:
            w_old = self._update_w(w_old)
            loss_new = self._loss_function_value(w_old)
            t = abs(loss_new - loss_init)
            loss_init = loss_new
        return w_old, loss_new

    def _predict(self, x):
        y = np.dot(x, self.w)
        return self._sigmoid(y)

    def predict(self, x):
        if self.w is None and self.new_models is None:
            raise ModelNotFittedError
        if self.has_intercept and not (x[:, 0] == 1).all() and x.shape[1] > 1:
            x = self._add_ones(x)
        super(LogisticRegression, self).predict(x)

        if self.label_type == LabelType.binary:
            return np.array([1 if i >= self.threshold else 0 for i in self._predict(x)])
        else:
            return self._multi_predict(x)

    def predict_prob(self, x):
        if self.has_intercept and not (x[:, 0] == 1).all() and x.shape[1] > 1:
            x = self._add_ones(x)
        return self._predict(x)

    def score(self, x, y):
        if self.has_intercept and not (x[:, 0] == 1).all() and x.shape[1] > 1:
            x = self._add_ones(x)
        super(LogisticRegression, self).score(x, y)
        predict_y = self.predict(x)
        if self.label_type == LabelType.binary:
            return classify_f1(predict_y, y)
        elif self.label_type == LabelType.multi_class:
            return classify_f1_macro(predict_y, y)
        else:
            raise LabelTypeError

    def auc_plot(self, x, y):
        predict_y = self.predict_prob(x)
        classify_roc_plot(predict_y, y)

    def classify_plot(self, x, y, title=""):
        if self.has_intercept:
            x = self._add_ones(x)
        classify_plot(self.new(), self.x, self.y, x, y, title=self.__doc__ + title)

    def new(self):
        return LogisticRegression(self.tol, self.alpha, self.threshold, self.has_intercept)


class Lasso(LogisticRegression, BaseFeatureSelect):

    __doc__ = "Lasso Regression"

    def __init__(self, tol=0.01, lamb=0.1, alpha=0.01, threshold=0.5, has_intercept=True):
        """
        包含L1惩罚项的Logistic回归
        :param tol:            误差容忍度，越大时收敛越快，但是越不精确
        :param lamb            lambda，即惩罚项前面的参数，越大越不容易过拟合，但是偏差也越大
        :param alpha:           步长，梯度下降的参数
        :param threshold:      决策阈值，当得到的概率大于等于阈值时输出1，否则输出0
        :param has_intercept:  是否包含截距项
        """
        super(Lasso, self).__init__(tol, alpha, threshold, has_intercept)
        self.lamb = lamb

    def _loss_function_value(self, w):
        """
        直接采用平方损失，当然用logistic损失也行
        :param w: 参数向量
        :return: 损失函数值
        """
        return np.mean(np.square(self.y - self._sigmoid(np.dot(self.x, w)))) + self.lamb * np.sum(np.abs(w))

    def _loss_change_one_value(self, value, *args):
        w = args[0].copy()
        w[args[1]] = value
        return self._loss_function_value(w)

    def _update_w(self, w_old, *args):
        """
        坐标下降法进行求解，每一次固定除w_i以外所有w，用爬山法求最优
        :param w_old: 参数向量
        :param i: 第i个参数不固定，其他的都固定
        :return: void
        """
        i = args[0]
        if i >= len(w_old):
            raise MisMatchError
        w_old[i] = so.fmin(self._loss_change_one_value, w_old[i], (w_old, i), disp=False)[0]
        # func = lambda x: self._loss_change_one_value(x[0], w_old, i)
        # from simple_ml.optimal import SimulatedAnneal
        # sa = SimulatedAnneal(func, np.array([w_old[i]]), iter_times=20)
        # w_old[i] = sa.run()

    def _fit(self):
        _min = np.inf
        w_0 = np.zeros(self.variable_num)
        loss = self._loss_function_value(w_0)
        while abs(loss - _min) > self.tol:
            if loss < _min:
                _min = loss
            for i in range(self.variable_num):
                self._update_w(w_0, i)
            loss = self._loss_function_value(w_0)
        return w_0, _min

    def feature_select(self, top_n):
        if top_n > self.variable_num:
            raise TopNTooLargeError
        if self.w is None:
            raise ModelNotFittedError
        if self.has_intercept:
            w = self.w[1:]
        else:
            w = self.w
        if len(w[w != 0]) <= top_n:
            return np.arange(w.shape[0])[w != 0]
        else:
            return w.argsort()[-top_n:][::-1]

    def new(self):
        return Lasso(self.tol, self.lamb, self.alpha, self.threshold, self.has_intercept)


class Ridge(Lasso):

    __doc__ = "Ridge Regression"

    def __init__(self, tol=0.01, lamb=0.1, alpha=0.01, threshold=0.5, has_intercept=True):
        """
        包含L2惩罚项的Logistic回归
        :param tol:            误差容忍度，越大时收敛越快，但是越不精确
        :param lamb            lambda，即惩罚项前面的参数，越大越不容易过拟合，但是偏差也越大
        :param alpha:           步长，梯度下降的参数
        :param threshold:      决策阈值，当得到的概率大于等于阈值时输出1，否则输出0
        :param has_intercept:  是否包含截距项
        """
        super(Ridge, self).__init__(tol, lamb, alpha, threshold, has_intercept)

    def _loss_function_value(self, w):
        """
        直接采用平方损失，当然用logistic损失也行
        :param w: 参数向量
        :return: 损失函数值
        """
        return np.mean(np.square(self.y - self._sigmoid(np.dot(self.x, w)))) + self.lamb * np.sum(np.square(w))

    def new(self):
        return Ridge(self.tol, self.lamb, self.alpha, self.threshold, self.has_intercept)
