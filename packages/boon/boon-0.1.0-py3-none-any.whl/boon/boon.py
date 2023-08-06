import numpy as np

"""
This module provides functions to calculate Boo_n - the expected performance of the best-validation model chosen
from a pool of n candidate models. The measure is fully described in the paper
O. Bajgar, R. Kadlec, and J. Kleindienst. A Boo(n) for Evaluating Architecture Performance. ICML 2018.

So far, only the non-parametric estimator is implemented. Other estimators may be added later.

Git repository: https://gitlab.com/obajgar/boon/
"""


def boo(valid, test=None, n=5, best='max'):
    """
    Non-parametric empirical estimate of Boo_n based on Equation 7 in the paper and the following note on handling
    ties in validation results.
    :param valid: (array-like) Validation results.
    :param test: (array-like) Test results aligned with the validation data. Default: valid
    :param n: (int) the n parameter of Boo_n. Estimate the expected test performance of the best-validation model out of n.
    :param best: ('max' or 'min') Indicates whether 'best' corresponds to the maximum or minimum for the validation results.
    :return: (float) Boo_n
    """

    valid_array = np.array(valid)
    m = len(valid_array)

    if test is None:
        test = valid
    elif len(test) != m:
        raise ValueError("The number of validation and test results must be the same.")

    order_coeff = {'max': 1, 'min': -1}[best]

    # A bit of numpy magic to handle ties in validation results:
    # np.unique returns sorted unique validation results with their counts and an inverse array,
    # which maps the indices of original valid results to indices in this uq array and hence also in the counts array
    uq, inverse, counts = np.unique(order_coeff * valid_array, return_inverse=True, return_counts=True)
    # Ranks of unique elements starting from 1 and taking duplication into account
    uq_upper_ranks = np.cumsum(counts)
    uq_lower_ranks = uq_upper_ranks - counts

    valid_upper_ranks = uq_upper_ranks[inverse]
    valid_lower_ranks = uq_lower_ranks[inverse]
    valid_counts = counts[inverse]

    boon = np.sum((np.power(valid_upper_ranks, n) - np.power(valid_lower_ranks, n)) / valid_counts * test) / m**n

    return boon


"""
LICENSE

Copyright IBM Corporation. 2018.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
