# -*- coding: utf-8 -*-

# Copyright © 2017, Institut Pasteur
#   Contributor: François Laurent

# This file is part of the TRamWAy software available at
# "https://github.com/DecBayComp/TRamWAy" and is distributed under
# the terms of the CeCILL license as circulated at the following URL
# "http://www.cecill.info/licenses.en.html".

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


from .base import *
from .optim import *
from .stochastic_dv import *
from warnings import warn
from math import pi, log
import numpy as np
import pandas as pd
from collections import OrderedDict
import time


setup = {'name': 'non.stochastic.dv',
        'provides': 'dv',
        'infer': 'infer_non_stochastic_DV',
        'arguments': OrderedDict((
                ('localization_error',  ('-e', dict(type=float, default=0.03, help='localization error'))),
                ('diffusivity_prior',   ('-d', dict(type=float, help='prior on the diffusivity'))),
                ('potential_prior',     ('-v', dict(type=float, help='prior on the potential'))),
                ('jeffreys_prior',      ('-j', dict(action='store_true', help="Jeffreys' prior"))),
                ('min_diffusivity',     dict(type=float, help='minimum diffusivity value allowed')),
                ('max_iter',            dict(type=int, help='maximum number of iterations (~100)')),
                ('compatibility',       ('-c', '--inferencemap', '--compatible',
                                        dict(action='store_true', help='InferenceMAP compatible'))),
                ('epsilon',             dict(args=('--eps',), kwargs=dict(type=float, help='if defined, every gradient component can recruit all of the neighbours, minus those at a projected distance less than this value'), translate=True)),
                ('grad',                dict(help="gradient; any of 'grad1', 'gradn'")),
                ('export_centers',      dict(action='store_true')),
                ('verbose',             ()),
                ('region_size',                 ('-s', dict(type=int, help='radius of the regions, in number of adjacency steps'))))),
        'cell_sampling': 'group'}


def global_dv_neg_posterior(x, *args):
        s = 0.
        for j in range(int(x.size/2)):
                try:
                        s += local_dv_neg_posterior(j, x, *args)
                except ValueError:
                        pass
        return s


def infer_non_stochastic_DV(cells, localization_error=0.03, diffusivity_prior=None, potential_prior=None, \
        jeffreys_prior=False, min_diffusivity=None, max_iter=None, epsilon=None, \
        export_centers=False, verbose=True, compatibility=False, **kwargs):

        # initial values
        index, reverse_index, n, dt_mean, D_initial, min_diffusivity, D_bounds, border = \
                smooth_infer_init(cells, min_diffusivity=min_diffusivity, jeffreys_prior=jeffreys_prior)
        min_diffusivity = None
        try:
                if compatibility:
                        raise Exception # skip to the except block
                volume = [ cells[i].volume for i in index ]
        except:
                V_initial = -np.log(n / np.max(n))
        else:
                density = n / np.array([ np.inf if v is None else v for v in volume ])
                density[density == 0] = np.min(density[0 < density])
                V_initial = np.log(np.max(density)) - np.log(density)
        dv = LocalDV(D_initial, V_initial, diffusivity_prior, potential_prior, min_diffusivity, ~border)

        # gradient options
        grad_kwargs = {}
        if epsilon is not None:
                if compatibility:
                        warn('epsilon should be None for backward compatibility with InferenceMAP', RuntimeWarning)
                grad_kwargs['eps'] = epsilon

        # parametrize the optimization algorithm
        #default_BFGS_options = dict(maxcor=dv.combined.size, ftol=1e-8, maxiter=1e3,
        #        disp=verbose)
        #options = kwargs.pop('options', default_BFGS_options)
        #if max_iter:
        #        options['maxiter'] = max_iter
        #V_bounds = [(None, None)] * V_initial.size
        #if min_diffusivity is None: # currently, cannot be None
        #        bounds = None
        #else:
        #        bounds = D_bounds + V_bounds
        #        options['maxfun'] = 1e10
        #        # in L-BFGS-B the number of iterations is usually very low (~10-100) while the number of
        #        # function evaluations is much higher (~1e4-1e5);
        #        # with maxfun defined, an iteration can stop anytime and the optimization may terminate
        #        # with an error message
        #options.update(kwargs)

        # posterior function input arguments
        squared_localization_error = localization_error * localization_error
        args = (dv, cells, squared_localization_error, jeffreys_prior, dt_mean,
                        index, reverse_index, grad_kwargs)

        # get the initial posterior value so that it is subtracted from the further evaluations
        m = len(index)
        x0 = np.sum( local_dv_neg_posterior(j, dv.combined, *(args + (0., False))) for j in range(m) )
        if verbose:
                print('At X0\tactual posterior= {}\n'.format(x0))
        args = args + (x0 / float(m), 1 < int(verbose))

        def sample(_k, _x, _f):
                return 0, np.arange(m), np.arange(2*m)
        def sample(_k, _x):
                return np.arange(m)

        # run the optimization routine
        #result = sdfpmin(local_dv_neg_posterior, dv.combined, args, sample, m, verbose=verbose)
        #result = dfpmin(global_dv_neg_posterior, dv.combined, args, verbose=verbose)
        obfgs_kwargs = {}
        if verbose:
                obfgs_kwargs['verbose'] = verbose
        if max_iter:
                obfgs_kwargs['maxiter'] = max_iter
        result = minimize_obfgs(sample, local_dv_neg_posterior, dv.combined, args, **obfgs_kwargs)
        #if not (result.success or verbose):
        #        warn('{}'.format(result.message), OptimizationWarning)

        # collect the result
        dv.update(result[0])#.x)
        D, V = dv.D, dv.V
        if np.any(V < 0):
                V -= np.min(V)
        DVF = pd.DataFrame(np.stack((D, V), axis=1), index=index, \
                columns=[ 'diffusivity', 'potential'])

        # derivate the forces
        index_, F = [], []
        for i in index:
                gradV = cells.grad(i, V, reverse_index, **grad_kwargs)
                if gradV is not None:
                        index_.append(i)
                        F.append(-gradV)
        if F:
                F = pd.DataFrame(np.stack(F, axis=0), index=index_, \
                        columns=[ 'force ' + col for col in cells.space_cols ])
                DVF = DVF.join(F)
        else:
                warn('not any cell is suitable for evaluating the local force', RuntimeWarning)

        # add extra information if required
        if export_centers:
                xy = np.vstack([ cells[i].center for i in index ])
                DVF = DVF.join(pd.DataFrame(xy, index=index, \
                        columns=cells.space_cols))
                #DVF.to_csv('results.csv', sep='\t')

        return DVF

