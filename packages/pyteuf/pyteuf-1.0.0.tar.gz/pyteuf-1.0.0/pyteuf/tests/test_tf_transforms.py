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
"""Test of the :mod:pyteuf.tf_transforms module.

.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Florent Jaillet
"""
import pytest
from fractions import gcd

import numpy as np
from ltfatpy.comp.arg_firwin import arg_firwin
from ltfatpy import gabwin, gabdual, gabtight
from ltfatpy.signals.gspi import gspi

from madarrays import Waveform
from pyteuf.tf_transforms import _get_win_description, _get_transform_length
from pyteuf.tf_transforms import BaseStft
from pyteuf.tf_transforms import Stft
from pyteuf.tf_transforms import Istft
from pyteuf.tf_data import TfData

# TODO (future) test tightness of windows


@pytest.fixture(scope='class')
def get_data(request):

    win_len = np.random.randint(low=8, high=256)

    request.cls.n_bins = (
        int(2**np.floor(np.log2(win_len) + np.random.randint(low=2, high=5))))
    request.cls.hop = np.random.randint(low=win_len // 6, high=win_len // 4)

    request.cls.win_name = np.random.choice(list(arg_firwin()), 1)[0]
    request.cls.win_len = win_len
    request.cls.win_array = np.random.rand(win_len)

    request.cls.is_tight = np.random.choice([False, True])
    request.cls.zero_pad_full_sig = np.random.choice([False, True])
    request.cls.param_constraint = np.random.choice(['fix', 'pow2', 'pad'])
    request.cls.convention = np.random.choice(['lp', 'bp'])


@pytest.mark.usefixtures('get_data')
class TestFunctions:

    def test_get_transform_length(self):

        sig_len = _get_transform_length(self.n_bins*self.hop*2,
                                        hop=self.hop,
                                        n_bins=self.n_bins,
                                        win_len=100,
                                        param_constraint='fix',
                                        zero_pad_full_sig=False)
        assert sig_len == self.n_bins*self.hop*2

        sig_len = _get_transform_length(1000,
                                        hop=self.hop,
                                        n_bins=self.n_bins,
                                        win_len=100,
                                        param_constraint='pad',
                                        zero_pad_full_sig=False)

        lcm = self.hop * self.n_bins // gcd(self.hop, self.n_bins)
        exp_siglen = int(np.ceil(1000 / lcm) * lcm)
        assert sig_len == exp_siglen

        sig_len = _get_transform_length(1000,
                                        hop=self.hop,
                                        n_bins=self.n_bins,
                                        win_len=100,
                                        param_constraint='pad',
                                        zero_pad_full_sig=True)

        lcm = self.hop * self.n_bins // gcd(self.hop, self.n_bins)
        exp_siglen = int(np.ceil(1100 / lcm) * lcm)
        assert sig_len == exp_siglen

        match = '`hop` \(\w+\) is not a divisor of `sig_len` \(\w+\).'
        with pytest.raises(ValueError, match=match):
            _get_transform_length(sig_len=512,
                                  hop=13, win_len=100,
                                  n_bins=64, param_constraint='fix',
                                  zero_pad_full_sig=False)

        match = '`n_bins` \(\w+\) is not a divisor of `sig_len` \(\w+\).'
        with pytest.raises(ValueError, match=match):
            _get_transform_length(sig_len=512,
                                  hop=16, win_len=100, n_bins=63,
                                  param_constraint='fix',
                                  zero_pad_full_sig=False)

    def test_get_win_description(self):

        sig_len = self.hop * self.n_bins // gcd(self.hop, self.n_bins)

        # Gauss window
        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len, win_name='gauss',
                                        sig_len=sig_len)

        assert win_desc == {'name': 'gauss', 'width': self.win_len}

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len, win_name='gauss',
                                        sig_len=sig_len, is_tight=True)

        assert win_desc == {'name': ('tight', 'gauss'), 'width': self.win_len}
        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len,
                                        win_name=self.win_name,
                                        sig_len=sig_len)

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len, win_name='gauss',
                                        sig_len=sig_len, is_dual=True)

        assert win_desc == {'name': ('dual', 'gauss'), 'width': self.win_len}

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len, win_name='gauss',
                                        sig_len=sig_len, is_tight=True,
                                        is_dual=True)

        assert isinstance(win_desc, np.ndarray)
        np.testing.assert_equal(win_desc,
                                gabdual(g=gabwin(g={'name': ('tight', 'gauss'),
                                                    'width': self.win_len},
                                                 a=self.hop,
                                                 M=self.n_bins,
                                                 L=sig_len)[0],
                                        a=self.hop,
                                        M=self.n_bins,
                                        L=sig_len))

        match = '`sig_len` must be set for a gauss window.'
        with pytest.raises(ValueError, match=match):
            _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                 win_len=self.win_len, win_name='gauss',
                                 is_tight=True, is_dual=True)

        # Other window
        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len,
                                        win_name=self.win_name,
                                        sig_len=sig_len)

        assert win_desc == {'name': self.win_name, 'M': self.win_len}

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len,
                                        win_name=self.win_name,
                                        sig_len=sig_len, is_tight=True)

        assert win_desc == {
            'name': ('tight', self.win_name), 'M': self.win_len}

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len,
                                        win_name=self.win_name,
                                        sig_len=sig_len, is_dual=True)

        assert win_desc == {'name': ('dual', self.win_name), 'M': self.win_len}

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_len=self.win_len,
                                        win_name=self.win_name,
                                        sig_len=sig_len, is_tight=True,
                                        is_dual=True)

        assert isinstance(win_desc, np.ndarray)
        np.testing.assert_equal(
            win_desc,
            gabdual(g=gabwin(g={'name': ('tight', self.win_name),
                                'M': self.win_len},
                             a=self.hop,
                             M=self.n_bins,
                             L=sig_len)[0],
                    a=self.hop,
                    M=self.n_bins,
                    L=sig_len))

        # Array
        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_array=self.win_array,
                                        sig_len=sig_len)

        assert isinstance(win_desc, np.ndarray)
        np.testing.assert_equal(win_desc,
                                gabwin(g=self.win_array,
                                       a=self.hop,
                                       M=self.n_bins,
                                       L=sig_len)[0])

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_array=self.win_array,
                                        sig_len=sig_len, is_tight=True)

        assert isinstance(win_desc, np.ndarray)
        np.testing.assert_equal(win_desc,
                                gabtight(g=self.win_array,
                                         a=self.hop,
                                         M=self.n_bins,
                                         L=sig_len))

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_array=self.win_array,
                                        sig_len=sig_len, is_dual=True)

        assert isinstance(win_desc, np.ndarray)
        np.testing.assert_equal(win_desc,
                                gabdual(g=self.win_array,
                                        a=self.hop,
                                        M=self.n_bins,
                                        L=sig_len))

        win_desc = _get_win_description(n_bins=self.n_bins, hop=self.hop,
                                        win_array=self.win_array,
                                        sig_len=sig_len, is_tight=True,
                                        is_dual=True)

        assert isinstance(win_desc, np.ndarray)
        np.testing.assert_equal(win_desc,
                                gabdual(g=gabtight(g=self.win_array,
                                                   a=self.hop,
                                                   M=self.n_bins,
                                                   L=sig_len),
                                        a=self.hop,
                                        M=self.n_bins,
                                        L=sig_len))

        # Raises
        match = '`win_len` should be a positive integer \(given: -\w+\)'
        with pytest.raises(ValueError, match=match):
            _get_win_description(hop=self.hop, n_bins=self.n_bins,
                                 win_name=self.win_name, win_len=-self.win_len)

        match = 'Window cannot be specified by setting both `win_name` and '\
            '`win_array`, only one of them should be set.'
        with pytest.raises(ValueError, match=match):
            _get_win_description(hop=self.hop, n_bins=self.n_bins,
                                 win_name=self.win_name, win_len=self.win_len,
                                 win_array=self.win_array)

        match = 'Window should be specified by setting either `win_name` or '\
            '`win_array`.'
        with pytest.raises(ValueError, match=match):
            _get_win_description(hop=self.hop, n_bins=self.n_bins)

        match = 'Window length `win_len` should be specified.'
        with pytest.raises(ValueError, match=match):
            _get_win_description(hop=self.hop, n_bins=self.n_bins,
                                 win_name=self.win_name)

        match = 'Window length argument is ignored.'
        with pytest.warns(UserWarning, match=match):
            _get_win_description(hop=self.hop, n_bins=self.n_bins,
                                 win_array=self.win_array,
                                 win_len=self.win_len)

        match = 'Window \w+ is unknown or not implemented.'
        with pytest.raises(ValueError, match=match):
            _get_win_description(hop=self.hop, n_bins=self.n_bins,
                                 win_name='windows98', win_len=self.win_len)


class MockStft(BaseStft):
    pass


@pytest.mark.usefixtures('get_data')
class TestBaseStft:

    def test_init(self):

        # basic init
        my_stft = MockStft(n_bins=self.n_bins, hop=self.hop,
                           win_name=self.win_name, win_len=self.win_len)

        assert my_stft.get_params() == {'hop': self.hop,
                                        'n_bins': self.n_bins,
                                        'win_type': 'analysis',
                                        'win_name': self.win_name,
                                        'win_len': self.win_len,
                                        'win_array': None,
                                        'is_tight': False,
                                        'convention': 'lp'}

        my_stft = MockStft(n_bins=self.n_bins, hop=self.hop,
                           win_array=self.win_array)

        assert my_stft.get_params() == {'hop': self.hop,
                                        'n_bins': self.n_bins,
                                        'win_type': 'analysis',
                                        'win_name': None,
                                        'win_len': None,
                                        'win_array': self.win_array,
                                        'is_tight': False,
                                        'convention': 'lp'}

        # Raises
        match = '`n_bins` should be a positive integer \(given: -\d+\)'
        with pytest.raises(ValueError, match=match):
            my_stft = MockStft(n_bins=-self.n_bins, hop=self.hop,
                               win_name=self.win_name, win_len=self.win_len)

        match = '`hop` should be a positive integer \(given: -\d+\)'
        with pytest.raises(ValueError, match=match):
            my_stft = MockStft(n_bins=self.n_bins, hop=-self.hop,
                               win_name=self.win_name, win_len=self.win_len)

        match = 'Unknown value for `win_type`: thesis'
        with pytest.raises(ValueError, match=match):
            my_stft = MockStft(n_bins=self.n_bins, hop=self.hop,
                               win_name=self.win_name, win_len=self.win_len,
                               win_type='thesis')

        match = 'Unknown value for `convention`: rp'
        with pytest.raises(ValueError, match=match):
            my_stft = MockStft(n_bins=self.n_bins, hop=self.hop,
                               win_name=self.win_name, win_len=self.win_len,
                               convention='rp')

    def test_get_win_array(self):

        my_stft = MockStft(n_bins=self.n_bins, hop=self.hop,
                           win_name=self.win_name, win_len=self.win_len)

        win = my_stft.get_win_array()
        assert isinstance(win, np.ndarray)


@pytest.mark.usefixtures('get_data')
class TestStft:

    def test_init(self):

        # basic init
        my_stft = Stft(n_bins=self.n_bins, hop=self.hop,
                       win_name=self.win_name, win_len=self.win_len)

        assert my_stft.get_params() == {'hop': self.hop,
                                        'n_bins': self.n_bins,
                                        'param_constraint': 'fix',
                                        'win_type': 'analysis',
                                        'win_name': self.win_name,
                                        'win_len': self.win_len,
                                        'win_array': None,
                                        'is_tight': False,
                                        'zero_pad_full_sig': True,
                                        'convention': 'lp'}

        # Init n_bins and hop when param_constraints is pow2
        my_stft = Stft(n_bins=self.n_bins,
                       hop=self.hop,
                       param_constraint='pow2',
                       win_name=self.win_name,
                       win_len=self.win_len)

        assert my_stft.param_constraint == 'pow2'
        assert my_stft.n_bins == int(
            2**np.ceil(np.log2(self.n_bins)))
        assert my_stft.hop == int(
            2**np.round(np.log2(self.hop)))

        match = 'Unknown value for `param_constraint`: abc'
        with pytest.raises(ValueError, match=match):
            my_stft = Stft(n_bins=self.n_bins, hop=self.hop,
                           param_constraint='abc', win_name=self.win_name,
                           win_len=self.win_len)

    def test_get_win_array(self):

        my_stft = Stft(n_bins=self.n_bins, hop=self.hop,
                       win_name=self.win_name, win_len=self.win_len)

        win = my_stft.get_win_array()
        assert isinstance(win, np.ndarray)

        my_stft = Stft(n_bins=self.n_bins, hop=self.hop,
                       win_name='gauss', win_len=self.win_len,
                       zero_pad_full_sig=False)

    def test_boundaries_isolated_dirac(self):
        """Functional test based on the example called `Examples with isolated
        diracs` in notebook :ref:`time_frequency_boundary_effects`.
        """
        # The signal is composed of a dirac at initial time t=0 for testing the
        # boundary effects and another dirac time t=9 for control.
        signal_params_nopad = {'sig_len': 16, 'fs': 1}
        x_nopad = np.zeros(signal_params_nopad['sig_len'])
        x_nopad[0] = x_nopad[9] = 1
        signal_params_pad = {'sig_len': signal_params_nopad['sig_len'] + 1,
                             'fs': signal_params_nopad['fs']}
        x_pad = np.zeros(signal_params_pad['sig_len'])
        x_pad[0] = x_pad[9] = 1

        # Let us define two similar Stft objects that differ only on the use of
        # additional zero-padding. No additional zero-padding results in a
        # circular transform.
        stft_params = {'hop': 1, 'n_bins': 4, 'win_name': 'hann', 'win_len': 4,
                       'param_constraint': 'fix'}
        stft_nopad = Stft(zero_pad_full_sig=False, **stft_params)
        stft_pad = Stft(zero_pad_full_sig=True, **stft_params)

        X_nopad = stft_nopad.apply(x_nopad)
        X_pad = stft_pad.apply(x_pad)
        np.testing.assert_array_equal(X_nopad.shape, (3, 16))
        np.testing.assert_array_equal(X_pad.shape, (3, 20))

        # Dirac at time t=0 spreads at times t=0, t=1 and t=-1
        np.testing.assert_array_less(
            np.abs(X_nopad[:, [-2, -1, 1, 2]]).to_np_array(),
            np.abs(X_nopad[:, [-1, 0, 0, 1]]).to_np_array())
        np.testing.assert_array_less(
            np.abs(X_pad[:, [-2, -1, 1, 2]]).to_np_array(),
            np.abs(X_pad[:, [-1, 0, 0, 1]]).to_np_array())

        # Compare coefficients of the tested and control diracs
        np.testing.assert_array_almost_equal(
            np.abs(X_nopad[:, [-1, 0, 1]]).to_np_array(),
            np.abs(X_nopad[:, [8, 9, 10]]).to_np_array())
        np.testing.assert_array_almost_equal(
            np.abs(X_pad[:, [-1, 0, 1]]).to_np_array(),
            np.abs(X_pad[:, [8, 9, 10]]).to_np_array())

        # With additional zero-padding, the dirac at time t=0 does not spread
        # at t=15 any more since the signal has been zero-padded to avoid
        # circular effects. Energy is observed at time t=19, i.e. in the area
        # where the signal has been extended.
        np.testing.assert_array_almost_equal(
            np.abs(X_nopad[:, [-1, 0, 1]]).to_np_array(),
            np.abs(X_pad[:, [-1, 0, 1]]).to_np_array())

        # Check zero columns
        i_zeros = list(range(X_nopad.shape[1]))
        i_zeros.remove(0)
        i_zeros.remove(1)
        i_zeros.remove(8)
        i_zeros.remove(9)
        i_zeros.remove(10)
        i_zeros.remove(15)
        np.testing.assert_array_almost_equal(
            X_nopad[:, i_zeros].to_np_array(), 0)
        i_zeros = list(range(X_pad.shape[1]))
        i_zeros.remove(0)
        i_zeros.remove(1)
        i_zeros.remove(8)
        i_zeros.remove(9)
        i_zeros.remove(10)
        i_zeros.remove(19)
        np.testing.assert_array_almost_equal(
            X_pad[:, i_zeros].to_np_array(), 0)

        # Check that all rows are equal in magnitude
        for i in range(1, X_pad.shape[0]):
            np.testing.assert_array_almost_equal(
                np.abs(X_pad[0, :]).to_np_array(),
                np.abs(X_pad[i, :]).to_np_array())

        for i in range(1, X_nopad.shape[0]):
            np.testing.assert_array_almost_equal(
                np.abs(X_nopad[0, :]).to_np_array(),
                np.abs(X_nopad[i, :]).to_np_array())

    def test_diracs_at_both_boundaries(self):
        """ Functional test based on the example called `Examples with diracs
        at boundaries` in notebook :ref:`time_frequency_boundary_effects`.
        """
        signal_params_nopad = {'sig_len': 16, 'fs': 1}
        x_nopad = Waveform(np.zeros(signal_params_nopad['sig_len']),
                           fs=signal_params_nopad['fs'])
        x_nopad[0] = x_nopad[-1] = x_nopad[8] = x_nopad[9] = 1

        signal_params_pad = {'sig_len': signal_params_nopad['sig_len'] + 1,
                             'fs': signal_params_nopad['fs']}
        x_pad = Waveform(np.zeros(signal_params_pad['sig_len']),
                         fs=signal_params_pad['fs'])
        x_pad[0] = x_pad[-1] = x_pad[8] = x_pad[9] = 1

        # Let us define two similar Stft objects that differ only on the use
        # of additional zero-padding. No additional zero-padding results in a
        # circular transform.
        stft_params = {'hop': 1, 'n_bins': 4, 'win_name': 'hann', 'win_len':
                       4, 'param_constraint': 'fix'}

        stft_nopad = Stft(zero_pad_full_sig=False, **stft_params)
        stft_pad = Stft(zero_pad_full_sig=True, **stft_params)

        X_nopad = stft_nopad.apply(x_nopad)
        X_pad = stft_pad.apply(x_pad)
        np.testing.assert_array_equal(X_nopad.shape, (3, 16))
        np.testing.assert_array_equal(X_pad.shape, (3, 20))

        # Circular case: diracs at time t=-1 and t=0 spread at times t=-2 to 1
        # summation is performed to avoid equality cases
        np.testing.assert_array_less(
            np.sum(np.abs(X_nopad[:, [-3, -2, 1, 2]]), axis=0),
            np.sum(np.abs(X_nopad[:, [-2, -1, 0, 1]]), axis=0))
        np.testing.assert_array_almost_equal(
            np.abs(X_nopad[:, [-2, -1]]).to_np_array(),
            np.abs(X_nopad[:, [1, 0]]).to_np_array())
        # Compare coefficients of the tested and control diracs
        np.testing.assert_array_almost_equal(
            np.abs(X_nopad[:, [-2, -1, 0, 1]]).to_np_array(),
            np.abs(X_nopad[:, [7, 8, 9, 10]]).to_np_array())
        # Check zero columns
        i_zeros = list(range(X_nopad.shape[1]))
        i_zeros.remove(0)
        i_zeros.remove(1)
        i_zeros.remove(7)
        i_zeros.remove(8)
        i_zeros.remove(9)
        i_zeros.remove(10)
        i_zeros.remove(14)
        i_zeros.remove(15)
        np.testing.assert_array_almost_equal(
            X_nopad[:, i_zeros].to_np_array(), 0)

        # Pad case: dirac at time t=0 spread at times t=-1 to 1
        np.testing.assert_array_less(
            np.abs(X_pad[:, [-2, -1, 1, 2]]).to_np_array(),
            np.abs(X_pad[:, [-1, 0, 0, 1]]).to_np_array())
        # Pad case: dirac at time t=15 spread at times t=15 to 17
        np.testing.assert_array_less(
            np.abs(X_pad[:, [14, 15, 17, 18]]).to_np_array(),
            np.abs(X_pad[:, [15, 16, 16, 17]]).to_np_array())
        # Dirac patterns should be equal
        np.testing.assert_array_almost_equal(
            np.abs(X_pad[:, [-2, -1, 0, 1, 2]]).to_np_array(),
            np.abs(X_pad[:, [14, 15, 16, 17, 18]]).to_np_array())
        # Compare control diracs in both transforms
        np.testing.assert_array_almost_equal(
            np.abs(X_nopad[:, [7, 8, 9, 10]]).to_np_array(),
            np.abs(X_pad[:, [7, 8, 9, 10]]).to_np_array())
        # Check zero columns
        i_zeros = list(range(X_pad.shape[1]))
        i_zeros.remove(0)
        i_zeros.remove(1)
        i_zeros.remove(7)
        i_zeros.remove(8)
        i_zeros.remove(9)
        i_zeros.remove(10)
        i_zeros.remove(15)
        i_zeros.remove(16)
        i_zeros.remove(17)
        i_zeros.remove(19)
        np.testing.assert_array_almost_equal(
            X_pad[:, i_zeros].to_np_array(), 0)

    def test_boundaries_sine(self):
        """ Functional test based on the example called `Examples with a
        sinusoid` in notebook :ref:`time_frequency_boundary_effects`.
        """
        signal_params_nopad = {'sig_len': 32}
        signal_params_nopad['fs'] = signal_params_nopad['sig_len'] - 1
        signal_params_pad = {'sig_len': signal_params_nopad['sig_len'] + 1}
        signal_params_pad['fs'] = signal_params_pad['sig_len'] - 1
        f0 = 4 / signal_params_nopad['sig_len']
        x_nopad = Waveform(
            np.sin(2 * np.pi * f0 * np.arange(signal_params_nopad['sig_len'])),
            fs=signal_params_nopad['fs'])
        f0_pad = 4 / signal_params_pad['sig_len']
        x_pad = Waveform(np.sin(
            2 * np.pi * f0_pad * np.arange(signal_params_pad['sig_len'])),
                         fs=signal_params_pad['fs'])

        stft_params = {'hop': 1, 'n_bins': 16, 'win_name': 'hann',
                       'win_len': 16, 'param_constraint': 'fix'}

        stft_nopad = Stft(zero_pad_full_sig=False, **stft_params)
        X_nopad = stft_nopad.apply(x_nopad)
        np.testing.assert_array_equal(X_nopad.shape, (9, 32))

        # Check that all cols are equal in magnitude
        for i in range(1, X_nopad.shape[1]):
            np.testing.assert_array_almost_equal(
                np.abs(X_nopad[:, 0]).to_np_array(),
                np.abs(X_nopad[:, i]).to_np_array())

        # Check that max is in row 2
        np.testing.assert_array_less(
            np.abs(X_nopad[[0, 1, 3, 4], :]).to_np_array(),
            np.abs(X_nopad[[1, 2, 2, 3], :]).to_np_array())

        # Check zero rows
        np.testing.assert_array_almost_equal(
            np.abs(X_nopad[[0, 4, 5, 6, 7, 8], :]).to_np_array(), 0)

        stft_pad = Stft(zero_pad_full_sig=True, **stft_params)
        X_pad = stft_pad.apply(x_pad)
        np.testing.assert_array_equal(X_pad.shape, (9, 48))

        # Check previously zero rows are non-zero
        np.testing.assert_array_less(
            1, np.sum(np.abs(X_pad[[0, 4, 5, 6, 7, 8], :]), axis=1))

    def test_conventions(self):
        sig_len = 1000
        x = np.random.randn(sig_len)

        X_lp = Stft(n_bins=self.n_bins, hop=self.hop,
                    win_name=self.win_name, win_len=self.win_len,
                    param_constraint='pow2', convention='lp').apply(x)

        X_bp = Stft(n_bins=self.n_bins, hop=self.hop,
                    win_name=self.win_name, win_len=self.win_len,
                    param_constraint='pow2', convention='bp').apply(x)

        # Modulus should be equal
        np.testing.assert_array_almost_equal(np.abs(X_lp).to_np_array(),
                                             np.abs(X_bp).to_np_array())
        # Test equivalence
        F = np.exp(1j * 2 * np.pi / X_lp.tf_params['n_bins'] *
                   np.outer(np.arange(X_lp.shape[0]),
                            np.arange(X_lp.shape[1]) * X_lp.tf_params['hop']))
        np.testing.assert_array_almost_equal(X_lp.to_np_array() * F,
                                             X_bp.to_np_array(),
                                             decimal=1)

    def test_dgt_vs_dgtr(self):
        sig_len = 100

        # Build a complex signal with zero imaginary part and equivalent real
        # signal
        s = np.cos(2 * np.pi * 0.1 * np.arange(sig_len) + 0.2) + 1j * 0
        xc = s
        xr = np.real(s)

        stft = Stft(n_bins=self.n_bins, hop=self.hop, win_name=self.win_name,
                    win_len=self.win_len, param_constraint='pow2')

        Xc = stft.apply(xc)
        Xr = stft.apply(xr)

        n_bins = self.n_bins
        n_bins_r = self.n_bins // 2 + 1

        assert Xc.shape[0] == n_bins
        assert Xr.shape[0] == n_bins_r
        assert Xc.shape[1] == Xr.shape[1]
        np.testing.assert_array_almost_equal(
            Xc[:n_bins_r, :].to_np_array(),
            Xr.to_np_array(),
            err_msg='Contents for non-negative frequencies.')
        np.testing.assert_array_almost_equal(
            Xc[1:n_bins_r + 1, :].to_np_array(),
            np.conj(Xc[-1:-n_bins_r - 1:-1, :]).to_np_array(),
            err_msg='Hermitian symmetry')

    def test_str(self):

        my_stft = Stft(hop=4, n_bins=32, win_name='hann', win_len=16,
                       win_type='synthesis', is_tight=False,
                       param_constraint='fix', zero_pad_full_sig=True,
                       convention='lp')

        exp_str = ['*' * 29 + ' STFT ' + '*' * 29]

        exp_str.append('Specified synthesis window: hann, 16 samples')
        exp_str.append('Tight: False')
        exp_str.append('Hop length: 4 samples')
        exp_str.append('32 frequency bins')
        exp_str.append('Convention: lp')
        exp_str.append('param_constraint: fix')
        exp_str.append('zero_pad_full_sig: True')
        exp_str.append('*' * 64)

        exp_str = '\n'.join(exp_str)

        np.testing.assert_equal(str(my_stft), exp_str)

        my_stft = Stft(hop=4, n_bins=32, win_array=np.random.randn(16),
                       win_type='synthesis', is_tight=False,
                       param_constraint='fix', zero_pad_full_sig=True,
                       convention='lp')

        exp_str = ['*' * 29 + ' STFT ' + '*' * 29]

        exp_str.append('Built-in synthesis window, 16 samples')
        exp_str.append('Tight: False')
        exp_str.append('Hop length: 4 samples')
        exp_str.append('32 frequency bins')
        exp_str.append('Convention: lp')
        exp_str.append('param_constraint: fix')
        exp_str.append('zero_pad_full_sig: True')
        exp_str.append('*' * 64)

        exp_str = '\n'.join(exp_str)

        np.testing.assert_equal(str(my_stft), exp_str)


@pytest.mark.usefixtures('get_data')
class TestIstft:

    def test_transform_array(self):

        my_stft = Stft(n_bins=self.n_bins, hop=self.hop,
                       win_name=self.win_name, win_len=self.win_len,
                       param_constraint='pow2')

        sig_len = int(2 * my_stft.n_bins + 123)
        x = Waveform(np.random.randn(sig_len), fs=44100)
        X = my_stft.apply(x)

        istft = my_stft.get_istft()
        x_ref = istft.apply(X)

        X_array = X.to_np_array()

        # Test with original signal parameters
        x_array = istft.apply(X_array, signal_params=X.signal_params)
        np.testing.assert_equal(x_array.fs, 44100)
        np.testing.assert_equal(x_array.size, sig_len)
        np.testing.assert_array_almost_equal(x_array, x_ref)

        # Test with no signal parameters
        x_array_no_sigparams = istft.apply(X_array)
        assert x_array_no_sigparams.fs == 1
        assert x_array_no_sigparams.size == my_stft.hop * X.shape[1]

        np.testing.assert_array_almost_equal(
            x_array_no_sigparams[:sig_len].to_np_array(),
            x_ref.to_np_array())
        np.testing.assert_array_almost_equal(
            np.array(x_array_no_sigparams[sig_len:]), 0)

    def test_get_win_array(self):

        my_istft = Istft(n_bins=self.n_bins, hop=self.hop,
                         win_name=self.win_name, win_len=self.win_len)

        win = my_istft.get_win_array()
        assert isinstance(win, np.ndarray)

        my_istft = Istft(n_bins=self.n_bins, hop=self.hop,
                         win_name='gauss', win_len=self.win_len)

        match = '`sig_len` must be set for a gauss window.'
        with pytest.raises(ValueError, match=match):
            my_istft.get_win_array()

    def test_str(self):

        my_istft = Istft(hop=4, n_bins=32, win_name='hann', win_len=16,
                         win_type='synthesis', is_tight=False,
                         convention='lp')

        exp_str = ['*' * 28 + ' ISTFT ' + '*' * 29]

        exp_str.append('Specified synthesis window: hann, 16 samples')
        exp_str.append('Tight: False')
        exp_str.append('Hop length: 4 samples')
        exp_str.append('32 frequency bins')
        exp_str.append('Convention: lp')
        exp_str.append('*' * 64)

        exp_str = '\n'.join(exp_str)

        np.testing.assert_equal(str(my_istft), exp_str)

        my_istft = Istft(hop=4, n_bins=32, win_array=np.random.randn(16),
                         win_type='analysis', is_tight=False,
                         convention='lp')

        exp_str = ['*' * 28 + ' ISTFT ' + '*' * 29]

        exp_str.append('Built-in analysis window, 16 samples')
        exp_str.append('Tight: False')
        exp_str.append('Hop length: 4 samples')
        exp_str.append('32 frequency bins')
        exp_str.append('Convention: lp')
        exp_str.append('*' * 64)

        exp_str = '\n'.join(exp_str)

        np.testing.assert_equal(str(my_istft), exp_str)


@pytest.mark.usefixtures('get_data')
class TestIntegration:
    def test_noise_signal_reconstruction(self):

        x = Waveform(np.random.randn(100), fs=1000)

        my_stft = Stft(win_name=self.win_name,
                       win_len=self.win_len,
                       hop=self.hop,
                       n_bins=self.n_bins,
                       param_constraint='pow2',
                       zero_pad_full_sig=True)

        X = my_stft.apply(x)
        my_istft = my_stft.get_istft()
        y = my_istft.apply(X)

        reconstruction_error = 10 * np.log10(np.mean(np.abs(x - y)**2))
        np.testing.assert_allclose(actual=y, desired=x, rtol=0, atol=10**-10)
        assert y.fs == x.fs

    def test_windows_and_pad_full_sig_options(self):
        """Test reconstruction with different windows and zero_pad_full_sig"""

        sig_len = np.random.randint(1000, 2000)
        x = Waveform(np.random.rand(sig_len), fs=1000)
        for win_name in arg_firwin() | {'gauss'}:
            print('Window: {}'.format(win_name))
            if win_name in ('gauss', 'tight'):
                n_bins = int(2**np.floor(
                    np.log2(win_len) + np.random.randint(low=4, high=6)))
            else:
                n_bins = self.n_bins

            win_len = self.win_len
            hop = self.hop
            n_bins = self.n_bins

            for zero_pad_full_sig in (False, True):
                print('zero_pad_full_sig option: {}'.format(zero_pad_full_sig))
                if zero_pad_full_sig and win_name == 'gauss':
                    with pytest.raises(
                            ValueError,
                            match="Cannot pad full signal if win_name is "
                                  "gauss, use a FIR window instead or set "
                                  "zero_pad_full_sig=False"):
                        Stft(win_name=win_name,
                             win_len=win_len,
                             hop=hop,
                             n_bins=n_bins,
                             param_constraint='pow2',
                             zero_pad_full_sig=zero_pad_full_sig)
                    continue
                my_stft = Stft(win_name=win_name,
                               win_len=win_len,
                               hop=hop,
                               n_bins=n_bins,
                               param_constraint='pow2',
                               zero_pad_full_sig=zero_pad_full_sig)
                X = my_stft.apply(x)
                y = my_stft.get_istft().apply(X)
                mean_err = np.mean((y - x)**2)

                np.testing.assert_allclose(
                    actual=mean_err, desired=0, atol=10**-15, rtol=0)
                np.testing.assert_allclose(
                    actual=y, desired=x, rtol=0, atol=10**-5)
                assert y.fs == x.fs

    def test_real_sound_reconstruction(self):

        s, fs = gspi()
        x = Waveform(data=s, fs=fs)

        win_name = 'sine'
        win_len = int(2048 / 44100 * x.fs)
        hop = win_len // 8
        n_bins = int(2**np.floor(np.log2(win_len) + 1))
        my_stft = Stft(win_name=win_name,
                       win_len=win_len,
                       hop=hop,
                       n_bins=n_bins,
                       param_constraint='pow2',
                       zero_pad_full_sig=True)

        my_istft = my_stft.get_istft()

        X = my_stft.apply(x)
        y = my_istft.apply(X)

        np.testing.assert_allclose(actual=y, desired=x, rtol=0, atol=10**-15)

        Y = Stft(**my_istft.get_params(), param_constraint='pow2',
                 zero_pad_full_sig=True).apply(y)

        np.testing.assert_allclose(actual=Y.to_np_array(),
                                   desired=X.to_np_array(),
                                   rtol=0, atol=10**-13)

    def test_apply_adjoint(self):
        sig_len = self.hop * self.n_bins // gcd(self.hop, self.n_bins)

        # Complex signals
        x = np.random.randn(sig_len) + 1j * np.random.randn(sig_len)
        for win_type in {'analysis', 'synthesis'}:
            print('win_type:', win_type)

            my_stft = Stft(win_name=self.win_name,
                           win_len=self.win_len,
                           win_type=win_type,
                           hop=self.hop,
                           n_bins=self.n_bins,
                           param_constraint='pow2',
                           zero_pad_full_sig=True)
            X = my_stft.apply(x)

            Y = np.random.randn(*X.shape) + 1j * np.random.randn(*X.shape)
            Y = TfData(data=Y, tf_params=X.tf_params,
                       signal_params=X.signal_params)
            y = my_stft.apply_adjoint(Y)

            np.testing.assert_array_almost_equal(np.vdot(x, y),
                                                 np.vdot(X, Y))

        # Real signals
        x = np.random.randn(sig_len)
        for stft_wintype in {'analysis', 'synthesis'}:
            print('win_type:', stft_wintype)

            my_stft = Stft(win_name=self.win_name,
                           win_len=self.win_len,
                           win_type=win_type,
                           hop=self.hop,
                           n_bins=self.n_bins,
                           param_constraint='pow2',
                           zero_pad_full_sig=True)

            X = my_stft.apply(x)

            Y = np.random.randn(*X.shape) + 1j * np.random.randn(*X.shape)
            Y = TfData(data=Y, tf_params=X.tf_params,
                       signal_params=X.signal_params)

            match = ('DGT adjoint operator for real signal is not valid \(not '
                     'correctly implemented yet\), you may use '
                     '\(artificially\) complex signals as inputs.')
            with pytest.raises(NotImplementedError, match=match):
                y = my_stft.apply_adjoint(x)
