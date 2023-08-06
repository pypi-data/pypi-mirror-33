# -*- coding: utf-8 -*-

from .base import *
from .smooth_d import smooth_d_neg_posterior
import numpy as np
import pandas as pd
from collections import OrderedDict


setup = {'arguments': OrderedDict(),
        'cell_sampling': 'group'}


def infer(cells, volume=True, **kwargs):
        index, reverse_index, n, dt_mean, D_initial, _, _, _ = \
                smooth_infer_init(cells)
        index = np.asarray(index)
        V = []
        for i in index:
                cell = cells[i]
                V.append(cell.volume)
        # format the output
        result = pd.DataFrame(V, columns='volume')
        return result

