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


class FittingMethod(object):
    """

    """

    def fit(self, model, train_set, test_set=None):
        """
        Optimize Hyperparameters

        :param model:
        :type model:
        :param train_set:
        :type train_set:
        :param test_set:
        :type test_set:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
