# -*- coding: utf-8 -*-

"""
Test cropping a subset of a data array


"""

import numpy as np
from oceansdb.common import cropIndices

test_dims = {
        'time': np.array([45.625, 136.875, 228.125, 319.375]),
        'lat': np.array([-87.5, -50, -0.3, 0.1, 38, 87.5]),
        'lon': np.array([-2.5, 2.5, 7.5]),
        'depth': np.array([0, ])
        }



#cropIndices(test_dims, lat=np.array([38]), lon=np.array([0]))

