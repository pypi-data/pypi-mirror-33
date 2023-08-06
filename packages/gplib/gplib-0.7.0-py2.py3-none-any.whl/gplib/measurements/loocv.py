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


class LOOCV(Measurement):
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

        if grad_needed:
            raise NotImplementedError("LOOCV gradient")

        if test_set:
            posterior_gp = model.get_posterior(train_set)

            mean = posterior_gp.mean_function.marginalize_mean(
                test_set['X']
            )
            var = posterior_gp.covariance_function.marginalize_covariance(
                test_set['X'],
                only_diagonal=True
            )
            data_set = test_set
        else:
            covariance = model.covariance_function.marginalize_covariance(
                train_set['X']
            )
            l_matrix = model.safe_chol(covariance)

            inv_cov = scipy.linalg.cho_solve(
                (l_matrix, True),
                np.eye(l_matrix.shape[0])
            )

            diag_inv_cov = np.diagonal(inv_cov)[:, None]

            mean = train_set['Y'] - \
                   np.divide(np.dot(inv_cov, train_set['Y']), diag_inv_cov)

            var = np.divide(1.0, diag_inv_cov)
            data_set = train_set

        loocv = -np.sum(
            -0.5 * np.log(var) -
            np.power((data_set['Y'] - mean), 2) / (2.0 * var) -
            0.5 * np.log(2 * np.pi)
        )

        return loocv
