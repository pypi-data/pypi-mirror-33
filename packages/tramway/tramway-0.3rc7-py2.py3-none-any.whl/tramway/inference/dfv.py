# -*- coding: utf-8 -*-

# Copyright © 2017, Institut Pasteur
#   Contributor: François Laurent

# This file is part of the TRamWAy software available at
# "https://github.com/DecBayComp/TRamWAy" and is distributed under
# the terms of the CeCILL license as circulated at the following URL
# "http://www.cecill.info/licenses.en.html".

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


from .df import infer_DF
from .dv import DV, dv_neg_posterior
from .base import smooth_infer_init
from warnings import warn
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from collections import OrderedDict
import time


setup = {'name': 'dfv',
        'infer': 'infer_DF_to_DV',
        'arguments': OrderedDict((
                ('localization_error',  ('-e', dict(type=float, default=0.03, help='localization error'))),
                ('diffusivity_prior',   ('-d', dict(type=float, default=1., help='prior on the diffusivity'))),
                ('potential_prior',     ('-v', dict(type=float, default=1., help='prior on the potential'))),
                ('jeffreys_prior',      ('-j', dict(action='store_true', help="Jeffreys' prior"))),
                ('min_diffusivity',     dict(type=float, help='minimum diffusivity value allowed')),
                ('max_iter',            dict(type=int, help='maximum number of iterations')),
                ('debug',       dict(action='store_true')))),
        'provides': 'dv',
        'cell_sampling': 'group'}




def infer_DF_to_DV(cells, localization_error=0.03, diffusivity_prior=1., potential_prior=1., \
        jeffreys_prior=False, min_diffusivity=None, max_iter=None, debug=False, **kwargs):
        # initial values
        index, reverse_index, n, dt_mean, D_initial, min_diffusivity, D_bounds, border = \
                smooth_infer_init(cells, min_diffusivity=min_diffusivity, jeffreys_prior=jeffreys_prior)
        # addition in the original inferDV code >>>
        DF = infer_DF(cells, localization_error, jeffreys_prior, min_diffusivity, debug, **kwargs)
        assert np.all(DF.index == index)
        D_initial = DF['diffusivity'].values
        F_initial = DF[[ 'force '+col for col in cells.space_cols ]].values
        V_initial = -np.log(n / np.max(n))
        def f(V):
                t = time.time()
                e = 0.
                for i in index:
                        gradV = cells.grad(i, V, reverse_index)
                        if gradV is not None:
                                dF = F_initial + gradV
                                e += np.sum(dF * dF)
                print('err: {}\ttime: {}ms'.format(e, int(round((time.time() - t) * 1e3))))
                return e
        result = minimize(f, V_initial, options=dict(maxiter=100))
        V_initial = result.x
        # <<< addition in the original inferDV code
        V_bounds = [(None, None)] * V_initial.size
        dv = DV(D_initial, V_initial, diffusivity_prior, potential_prior, min_diffusivity, ~border)
        # parametrize the optimization algorithm
        if min_diffusivity is not None:
                kwargs['bounds'] = D_bounds + V_bounds
        options = kwargs.get('options', dict(eps=1e-8, gtol=1e-10))
        if max_iter:
                if min_diffusivity is not None:
                        options['maxfun'] = max_iter # L-BFGS-B ignores maxiter and admits maxfun instead
                else:
                        options['maxiter'] = max_iter
        kwargs['options'] = options
        # run the optimization routine
        squared_localization_error = localization_error * localization_error
        result = minimize(dv_neg_posterior, dv.combined, \
                args=(dv, cells, squared_localization_error, jeffreys_prior, dt_mean, index, reverse_index), \
                **kwargs)
        # collect the result
        if not result.success and debug:
                warn(result.message, RuntimeWarning)
                #print(dv_neg_posterior(result.x, dv, cells, squared_localization_error, jeffreys_prior, dt_mean, index, reverse_index))
        dv.update(result.x)
        D, V = dv.D, dv.V
        DVF = pd.DataFrame(np.stack((D, V), axis=1), index=index, \
                columns=[ 'diffusivity', 'potential'])
        # derivate the forces
        index_, F = [], []
        for i in index:
                gradV = cells.grad(i, V, reverse_index)
                if gradV is not None:
                        index_.append(i)
                        F.append(-gradV)
        if F:
                F = pd.DataFrame(np.stack(F, axis=0), index=index_, \
                        columns=[ 'force ' + col for col in cells.space_cols ])
                DVF = DVF.join(F)
        else:
                warn('not any cell is suitable for evaluating the local force', RuntimeWarning)
        if debug:
                xy = np.vstack([ cells[i].center for i in index ])
                DVF = DVF.join(pd.DataFrame(xy, index=index, \
                        columns=cells.space_cols))
                #DVF.to_csv('results.csv', sep='\t')
        return DVF

