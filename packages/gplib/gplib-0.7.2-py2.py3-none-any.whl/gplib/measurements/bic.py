# -*- coding: utf-8 -*-
#
#    Copyright 2018 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import scipy.linalg

from .measurement import Measurement


class BIC(Measurement):
    """

    """

    @staticmethod
    def measure(model, train_set, test_set=None, grad_needed=False):
        """

        :param model:
        :type model:
        :param train_set:
        :type train_set:
        :param test_set:
        :type test_set:
        :param grad_needed:
        :type grad_needed:
        :return:
        :rtype:
        """

        if test_set is not None:
            raise TypeError("Test set not needed")

        if grad_needed:
            raise NotImplementedError("BIC gradient")

        prior_lml = model.likelihood_function.get_log_likelihood(train_set)
        n = train_set['X'].shape[0]             # number of train data points
        M = model.get_optimizable_param_n()  # number of kernel parameters
        bic = -2 * prior_lml + M * np.log(n)

        return bic
