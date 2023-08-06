# -*- coding: utf-8 -*-
# ######### COPYRIGHT #########
#
# Copyright(c) 2018
# -----------------
#
# * Laboratoire d'Informatique et Systèmes <http://www.lis-lab.fr/>
# * Université d'Aix-Marseille <http://www.univ-amu.fr/>
# * Centre National de la Recherche Scientifique <http://www.cnrs.fr/>
# * Université de Toulon <http://www.univ-tln.fr/>
#
# Contributors
# ------------
#
# * Ronan Hamon <firstname.lastname_AT_lis-lab.fr>
# * Valentin Emiya <firstname.lastname_AT_lis-lab.fr>
# * Florent Jaillet <firstname.lastname_AT_lis-lab.fr>
#
# Description
# -----------
#
# pyteuf is a package for time-frequency analysis in Python.
#
# Licence
# -------
# This file is part of pyteuf.
#
# pyteuf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ######### COPYRIGHT #########
"""Utils functions and classes for testing.

.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Ronan Hamon

"""
import random
import numpy as np

import ltfatpy


def make_random_stft_parameters(win_name_set=None,
                                win_len_lim=(8, 256),
                                hop_divisor_lim=(6, 4),
                                n_bins_factor_lim=(2, 5),
                                with_array=False,
                                param_constraint='fix',
                                zero_pad_full_sig=True,
                                is_tight=False,
                                win_type='analysis',
                                convention='lp'):
    """Draw parameters for :class:`~pyteuf.tf_transforms.Stft` objects at
    random from ranges of values.

    Parameters
    ----------
    win_name_set : set, optional
        Set of possible window names. If None, the name is chosen among the
        set of available FIR windows and a Gaussian window.
    win_len_lim : 2-tuple, optional
        Range for the window length.
    hop_divisor_lim : 2-tuple, optional
        Range for divisors of the window length in order to draw a hop size.
    n_bins_factor_lim : 2-tuple, optional
        Range for powers of 2 to be multiplied by the window length to draw
        the number of bins.
    with_array : bool, optional
        If True, a window with random coefficients (uniformly drawn in [0, 1])
        is returned, and parameter `win_name_set` is ignored.
    param_constraint : {'fix', 'pad', 'pow2'}, optional
        Fixed choice for `param_constraint`.
    zero_pad_full_sig : bool, optional
        Fixed choice for `zero_pad_full_sig`.
    is_tight : bool, optional
        Fixed choice for `is_tight`.
    win_type : {'analysis', 'synthesis'}, optional
        Fixed choice for `win_type`.
    convention : {'lp', 'bp'}, optional
         Convention to use: 'lp' for low-pass (i.e. frequency invariant) or
         'bp' for band-pass (a.k.a. time invariant).

    Returns
    -------
    dict
        If parameter ``with_array`` is True, the dictionary contains values
        for the keys ``'win_array'``, ``'hop'``, ``'n_bins'``,
        ``'param_constraint'``, ``'zero_pad_full_sig'``, ``'is_tight'``,
        ``'win_type'`` and ``'convention'``. Otherwise, value with key
        ``'win_array'`` is replaced by values with keys ``'win_name'`` and
        ``'win_len'``.
    """
    if win_name_set is None:
        win_name_set = ltfatpy.arg_firwin() | {'gauss'}

    # draw a window name
    win_name = random.sample(win_name_set, 1)[0]

    # draw a window length
    win_len = np.random.randint(low=win_len_lim[0], high=win_len_lim[1])

    # draw a hop size
    hop = np.random.randint(low=win_len // hop_divisor_lim[0],
                            high=win_len // hop_divisor_lim[1])

    # draw a number of bins
    n_bins = int(2**np.floor(np.log2(win_len) + np.random.randint(
        low=n_bins_factor_lim[0], high=n_bins_factor_lim[1])))

    if with_array:
        win_array = np.random.rand(win_len)
        return {'win_array': win_array,
                'hop': hop,
                'n_bins': n_bins,
                'param_constraint': param_constraint,
                'zero_pad_full_sig': zero_pad_full_sig,
                'is_tight': is_tight,
                'win_type': win_type,
                'convention': convention}

    else:
        return {'win_name': win_name,
                'win_len': win_len,
                'hop': hop,
                'n_bins': n_bins,
                'param_constraint': param_constraint,
                'zero_pad_full_sig': zero_pad_full_sig,
                'is_tight': is_tight,
                'win_type': win_type,
                'convention': convention}
