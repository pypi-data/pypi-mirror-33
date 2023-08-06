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
"""Test of the :mod:pyteuf.tf_data module.

.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Florent Jaillet
"""
import pytest
import numpy as np

from ltfatpy import gabwin
from ltfatpy.gabor.dgtreal import dgtreal
from ltfatpy.gabor.dgt import dgt
from madarrays import MadArray, Waveform

from pyteuf.tf_data import TfData


@pytest.fixture(scope='class')
def get_data(request):
    request.cls.shape = np.random.randint(100, 1000, 2)
    request.cls.X_complex = np.random.random(
        request.cls.shape) + 1j * np.random.random(request.cls.shape)
    request.cls.X_float = np.random.random(request.cls.shape)
    request.cls.tf_params = {'win_len': 100, 'hop': 40, 'n_bins': 1024,
                             'win_name': 'hann', 'is_tight': True}
    request.cls.signal_params = {'sig_len': 10000, 'fs': 1000}
    request.cls.mask_phase = np.random.random(request.cls.shape) < 0.8
    request.cls.mask_magnitude = np.random.random(request.cls.shape) < 0.8


@pytest.mark.usefixtures('get_data')
class TestTfData:

    def test_init_complex(self):

        tfd = TfData(self.X_complex, mask_magnitude=self.mask_magnitude,
                     mask_phase=self.mask_phase)
        assert tfd.tf_params == {}
        assert tfd.signal_params == {}

        tfd = TfData(self.X_complex,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        assert tfd.tf_params == self.tf_params
        assert tfd.signal_params == self.signal_params

        n_bins = self.tf_params['n_bins']
        fs = self.signal_params['fs']
        assert tfd.n_frequencies == self.shape[0]
        np.testing.assert_equal(tfd.frequencies,
                                np.arange(self.shape[0]) * fs / n_bins)

        assert tfd.n_frames == self.shape[1]
        mid_times = np.arange(
            self.shape[1]) * self.tf_params['hop'] / self.signal_params['fs']
        start_times = (mid_times - np.floor((self.tf_params['win_len'] - 1) /
                                            2) / self.signal_params['fs'])
        end_times = mid_times + np.floor(
            (self.tf_params['win_len'] - 1) / 2) / self.signal_params['fs']

        np.testing.assert_almost_equal(tfd.start_times, start_times)
        np.testing.assert_almost_equal(tfd.mid_times, mid_times)
        np.testing.assert_almost_equal(tfd.end_times, end_times)

        with pytest.raises(
                ValueError,
                match='`data` should be a two-dimensional ndarray.'):
            TfData(np.random.rand(100))

    def test_init_float(self):

        tfd = TfData(self.X_float, mask=self.mask_magnitude)
        assert tfd.tf_params == {}
        assert tfd.signal_params == {}

        tfd = TfData(self.X_complex,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        assert tfd.tf_params == self.tf_params
        assert tfd.signal_params == self.signal_params

        n_bins = self.tf_params['n_bins']
        fs = self.signal_params['fs']
        assert tfd.n_frequencies == self.shape[0]
        np.testing.assert_equal(tfd.frequencies,
                                np.arange(self.shape[0]) * fs / n_bins)

        assert tfd.n_frames == self.shape[1]
        mid_times = np.arange(
            self.shape[1]) * self.tf_params['hop'] / self.signal_params['fs']
        start_times = mid_times - \
            np.floor((self.tf_params['win_len'] - 1) /
                     2) / self.signal_params['fs']
        end_times = mid_times + np.floor(
            (self.tf_params['win_len'] - 1) / 2) / self.signal_params['fs']

        np.testing.assert_almost_equal(tfd.start_times,
                                       start_times, err_msg='start times')
        np.testing.assert_almost_equal(tfd.mid_times,
                                       mid_times, err_msg='mid times')
        np.testing.assert_almost_equal(tfd.end_times,
                                       end_times, err_msg='end times')

        with pytest.raises(
                ValueError,
                match='`data` should be a two-dimensional ndarray.'):
            TfData(np.random.rand(100))

    def test_init_from_tfdata(self):

        old_tfd = TfData(self.X_complex,
                         mask_phase=self.mask_phase,
                         mask_magnitude=self.mask_magnitude,
                         tf_params=self.tf_params,
                         signal_params=self.signal_params)

        tfd = TfData(old_tfd)
        assert tfd.tf_params == old_tfd.tf_params
        assert tfd.signal_params == old_tfd.signal_params
        np.testing.assert_equal(tfd._mask, old_tfd._mask)
        assert not id(tfd.tf_params) == id(old_tfd.tf_params)
        assert not id(tfd.signal_params) == id(old_tfd.signal_params)
        assert not id(tfd._mask) == id(old_tfd._mask)

        tfd = TfData(old_tfd, tf_params=self.tf_params,
                     signal_params=self.signal_params)
        assert tfd.tf_params == old_tfd.tf_params
        assert tfd.signal_params == old_tfd.signal_params
        np.testing.assert_equal(tfd._mask, old_tfd._mask)
        assert not id(tfd.tf_params) == id(old_tfd.tf_params)
        assert not id(tfd.signal_params) == id(old_tfd.signal_params)
        assert not id(tfd._mask) == id(old_tfd._mask)

        new_mask = np.random.random(self.shape) < 0.5

        tfd = TfData(old_tfd, mask_magnitude=new_mask)
        np.testing.assert_equal(tfd.get_unknown_mask('magnitude'), new_mask)

        tfd = TfData(old_tfd, mask_phase=new_mask)
        np.testing.assert_equal(tfd.get_unknown_mask('phase'), new_mask)

    def test_plot(self):

        tfd = TfData(self.X_complex,
                     mask_phase=self.mask_phase,
                     mask_magnitude=self.mask_magnitude,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        tfd.plot_spectrogram()
        tfd.plot_spectrogram('any')
        tfd.plot_spectrogram('all')
        tfd.plot_spectrogram('magnitude')
        tfd.plot_spectrogram('phase')
        tfd.plot_spectrogram('magnitude only')
        tfd.plot_spectrogram('phase only')
        with pytest.raises(
                ValueError,
                match='Invalid value for mask_type: error'):
            tfd.plot_spectrogram('error')
        tfd.plot_mask()
        tfd.plot_mask('any')
        tfd.plot_mask('all')
        tfd.plot_mask('magnitude')
        tfd.plot_mask('phase')
        tfd.plot_mask('magnitude only')
        tfd.plot_mask('phase only')
        with pytest.raises(
                ValueError,
                match='Invalid value for mask_type: error'):
            tfd.plot_mask('error')

        tf_params = self.tf_params.copy()
        tf_params['n_bins'] = tfd.shape[0]

        tfd = TfData(self.X_complex,
                     mask_phase=self.mask_phase,
                     mask_magnitude=self.mask_magnitude,
                     tf_params=tf_params,
                     signal_params=self.signal_params)

        tfd.plot_spectrogram()
        tfd.plot_spectrogram('any')
        tfd.plot_spectrogram('all')
        tfd.plot_spectrogram('magnitude')
        tfd.plot_spectrogram('phase')
        tfd.plot_spectrogram('magnitude only')
        tfd.plot_spectrogram('phase only')
        with pytest.raises(
                ValueError,
                match='Invalid value for mask_type: error'):
            tfd.plot_spectrogram('error')
        tfd.plot_mask()
        tfd.plot_mask('any')
        tfd.plot_mask('all')
        tfd.plot_mask('magnitude')
        tfd.plot_mask('phase')
        tfd.plot_mask('magnitude only')
        tfd.plot_mask('phase only')
        with pytest.raises(
                ValueError,
                match='Invalid value for mask_type: error'):
            tfd.plot_mask('error')

        tfd = TfData(self.X_float,
                     mask=self.mask_phase,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        tfd.plot_spectrogram()
        tfd.plot_spectrogram('any')
        tfd.plot_spectrogram('all')
        tfd.plot_spectrogram('magnitude')
        tfd.plot_spectrogram('phase')
        tfd.plot_spectrogram('magnitude only')
        tfd.plot_spectrogram('phase only')
        with pytest.raises(
                ValueError,
                match='Invalid value for mask_type: error'):
            tfd.plot_spectrogram('error')
        tfd.plot_mask()
        tfd.plot_mask('any')
        tfd.plot_mask('all')
        tfd.plot_mask('magnitude')
        tfd.plot_mask('phase')
        tfd.plot_mask('magnitude only')
        tfd.plot_mask('phase only')
        with pytest.raises(
                ValueError,
                match='Invalid value for mask_type: error'):
            tfd.plot_mask('error')

    def test_spectrograms_unmasked(self):

        empty_mask = np.zeros(self.shape, dtype=np.bool)

        tfd = TfData(self.X_complex,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        magnitude_spec = tfd.magnitude_spectrogram
        assert type(magnitude_spec) == TfData
        assert magnitude_spec.tf_params == self.tf_params
        assert magnitude_spec.signal_params == self.signal_params
        np.testing.assert_equal(magnitude_spec.get_unknown_mask(),
                                empty_mask)
        np.testing.assert_equal(np.array(magnitude_spec),
                                np.abs(self.X_complex))

        energy_spec = tfd.energy_spectrogram
        assert type(energy_spec) == TfData
        assert energy_spec.tf_params == self.tf_params
        assert energy_spec.signal_params == self.signal_params
        np.testing.assert_equal(
            energy_spec.get_unknown_mask(), empty_mask)
        np.testing.assert_equal(np.array(energy_spec),
                                np.abs(self.X_complex)**2)

        phase = tfd.phase
        assert type(phase) == TfData
        assert phase.tf_params == self.tf_params
        assert phase.signal_params == self.signal_params
        np.testing.assert_equal(
            phase.get_unknown_mask(), empty_mask)
        np.testing.assert_equal(np.array(phase), np.angle(self.X_complex))

        tfd = TfData(self.X_float,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

    def test_spectrograms_masked(self):

        tfd = TfData(self.X_complex,
                     mask_phase=self.mask_phase,
                     mask_magnitude=self.mask_magnitude,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        magnitude_spec = tfd.magnitude_spectrogram
        assert type(magnitude_spec) == TfData
        np.testing.assert_equal(magnitude_spec.get_unknown_mask(),
                                self.mask_magnitude)
        np.testing.assert_equal(
            np.array(magnitude_spec), np.abs(self.X_complex))

        energy_spec = tfd.energy_spectrogram
        assert type(energy_spec) == TfData
        np.testing.assert_equal(energy_spec.get_unknown_mask(),
                                self.mask_magnitude)
        np.testing.assert_equal(np.array(energy_spec),
                                np.abs(self.X_complex)**2)

        phase = tfd.phase
        assert type(phase) == TfData
        np.testing.assert_equal(phase.get_unknown_mask(), self.mask_phase)
        np.testing.assert_equal(np.array(phase), np.angle(self.X_complex))

    def test_signal_is_complex(self):

        hop = 20
        n_bins = 512
        sig_len = 10*hop*n_bins
        win_len = 128

        x_real = np.cos(2 * np.pi * 0.1 * np.arange(sig_len) + 0.2)
        x_complex = x_real + 1j * \
            np.sin(2 * np.pi * 0.1 * np.arange(sig_len) + 0.2)

        g = gabwin(g={'name': 'hann', 'M': win_len},
                   a=hop, M=n_bins, L=sig_len)[0]

        X_real_dgt = dgt(x_real, g=g, a=hop, M=n_bins, L=sig_len)[0]
        X_real_dgtreal = dgtreal(x_real, g=g, a=hop, M=n_bins, L=sig_len)[0]
        X_complex = dgt(x_complex, g=g, a=hop, M=n_bins, L=sig_len)[0]

        print(X_real_dgt.shape)
        print(X_real_dgtreal.shape)
        print(X_complex.shape)

        tfd = TfData(X_real_dgt,
                     tf_params={'hop': hop, 'n_bins': n_bins,
                                'win_len': win_len},
                     signal_params={'sig_len': sig_len, 'fs': 44100})

        assert tfd.signal_is_complex()

        tfd = TfData(X_real_dgtreal,
                     tf_params={'hop': hop, 'n_bins': n_bins,
                                'win_len': win_len},
                     signal_params={'sig_len': sig_len, 'fs': 1})
        print(tfd.n_frequencies)

        assert not tfd.signal_is_complex()

        tfd = TfData(X_complex,
                     tf_params={'hop': hop, 'n_bins': n_bins,
                                'win_len': win_len},
                     signal_params={'sig_len': sig_len, 'fs': 1})

        assert tfd.signal_is_complex()

        tfd = TfData(self.X_float,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        tfd = TfData(X_complex,
                     tf_params={'hop': hop, 'win_len': win_len},
                     signal_params={'sig_len': sig_len, 'fs': 1})

        match = 'Missing information in `tf_params`: n_bins'
        with pytest.raises(ValueError, match=match):
            tfd.signal_is_complex()

    def test_str_repr_win_name(self):

        tfd = TfData(self.X_complex, tf_params=self.tf_params,
                     signal_params=self.signal_params)

        exp_str = ['========================',
                   'TF representation',
                   '------------------------',
                   'TF parameters',
                   '{}'.format(self.tf_params),
                   '------------------------',
                   'Signals parameters',
                   '{}'.format(self.signal_params),
                   '------------------------',
                   '{} frequency bins'.format(self.shape[0]),
                   '{} frames'.format(self.shape[1])]
        exp_str = '\n'.join(exp_str)
        assert str(tfd) == exp_str

        tfd = TfData(self.X_complex,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        exp_str = ['========================',
                   'TF representation',
                   '------------------------',
                   'TF parameters',
                   '{}'.format(self.tf_params),
                   '------------------------',
                   'Signals parameters',
                   '{}'.format(self.signal_params),
                   '------------------------',
                   '{} frequency bins'.format(self.shape[0]),
                   '{} frames'.format(self.shape[1])]

        assert str(tfd) == '\n'.join(exp_str)

        exp_repr = '<TfData at {}>'.format(hex(id(tfd)))
        assert repr(tfd) == exp_repr

    def test_copy(self):

        tfd = TfData(self.X_complex,
                     mask_phase=self.mask_phase,
                     mask_magnitude=self.mask_magnitude,
                     tf_params=self.tf_params,
                     signal_params=self.signal_params)

        tfd_copy = tfd.copy()
        np.testing.assert_equal(tfd, tfd_copy)
        assert not id(tfd) == id(tfd_copy)
        assert not id(tfd._mask) == id(tfd_copy._mask)
