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
"""Definition of a time-frequency data structure.

.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Florent Jaillet
"""
from ltfatpy import plotdgtreal, plotdgt
import matplotlib.pyplot as plt
import numpy as np

from madarrays import MadArray
# TODO (future) add a `crop` method to return a TfData after removing boundary effects


class TfData(MadArray):
    """Subclass of :class:`~madarrays.mad_array.MadArray` to handle
    Time-Frequency representations of real signals.

    A TfData object is 2D :class:`~madarrays.mad_array.MadArray`, with either
    real or
    complex entries. It is initialized in the same way as
    a :class:`~madarrays.mad_array.MadArray` object using binary or complex
    masks (see documentation of :class:`~madarrays.mad_array.MadArray`) It also
    two additional dictionaries `tf_params`  and `signal_params`
    that contain respectively the parameters of the time-frequency
    transformation, such as the hop size or the window, as well as the
    parameters needed to reconstruct the signals, such as the sampling
    frequency or the length. These two dictionaries can be used by any
    time-frequency transformation methods, and may be empty.

    Parameters
    ----------
    data : array of shape (n_frequencies, n_frames)
        Time-frequency data matrix.
    mask : boolean array_like, optional
        See parameter `mask` in :class:`~madarrays.mad_array.MadArray`
    mask_magnitude : boolean array_like or None, optional
        See parameter `mask_magnitude` in
        :class:`~madarrays.mad_array.MadArray`
    mask_phase : boolean array_like or None, optional
        See parameter `mask_phase` in :class:`~madarrays.mad_array.MadArray`
    masked_indexing : bool or None, optional
        See parameter `masked_indexing` in
        :class:`~madarrays.mad_array.MadArray`
    tf_params : dict
        Time-frequency parameters. The dictionary keys should be parameters
        for the constructor of a :class:`~pyteuf.tf_transforms.Stft` object so
        that `Stft(**tf_params)` returns an STFT similar to the one used to
        generate the current :class:`~pyteuf.tf_data.TfData` object.
    signal_params : dict
        Parameters of the original signal. The dictionary keys should be the
        sampling frequency `fs` and the length `sig_len` of the original
        signal (useful to reconstruct a signal of the exact same length as
        the original one).

    Attributes
    ----------
    tf_params : dict
        Time-frequency parameters (as described in the parameters section).
    signal_params : dict
        Parameters of the original signal (as described in the parameters
        section).

    See also
    --------
    :class:`madarrays.mad_array.MadArray`

    """
    def __new__(cls, data, tf_params=None, signal_params=None, mask=None,
                mask_magnitude=None, mask_phase=None, masked_indexing=None):

        obj = super().__new__(cls, data, mask=mask,
                              mask_magnitude=mask_magnitude,
                              mask_phase=mask_phase,
                              masked_indexing=masked_indexing)

        # Check TF arguments
        if tf_params is None:
            if isinstance(data, TfData):
                tf_params = data.tf_params
            else:
                tf_params = {}

        if signal_params is None:
            if isinstance(data, TfData):
                signal_params = data.signal_params
            else:
                signal_params = {}

        # test that the array is two-dimensional
        if not obj.ndim == 2:
            errmsg = '`data` should be a two-dimensional ndarray.'
            raise ValueError(errmsg)

        # add the supplementary attributes
        obj.tf_params = tf_params.copy()
        obj.signal_params = signal_params.copy()

        return obj

    def __array_finalize__(self, obj):

        super().__array_finalize__(obj)

        self.tf_params = getattr(obj, 'tf_params', {})
        self.signal_params = getattr(obj, 'signal_params', {})

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):

        output = super().__array_ufunc__(ufunc, method, *inputs, **kwargs)

        if isinstance(output, MadArray):
            output = output.view(TfData)
            tf_data = inputs[0] if isinstance(inputs[0], TfData) else inputs[1]
            output.tf_params = tf_data.tf_params
            output.signal_params = tf_data.signal_params
        return output

    @property
    def n_frequencies(self):
        """
        Number of Fourier frequencies (int).

        If the original signal is real, the number of frequencies correspond
        to non-negative Fourier frequencies and negative frequencies are
        discarded due to Hermitian symmetry, while the number of bins
        specified in the transform correspond to all (positive and negative)
        frequencies.
        """
        return self.shape[0]

    @property
    def n_frames(self):
        """Number of frames (int)."""
        return self.shape[1]

    @property
    def frequencies(self):
        """ Array of Fourier frequencies (array of shape (n_frequencies,)) """
        fs = self.signal_params['fs'] if 'fs' in self.signal_params else 1
        n_bins = self.tf_params['n_bins'] if 'n_bins' in self.tf_params else 1
        return np.arange(self.n_frequencies) / n_bins * fs

    @property
    def start_times(self):
        """Starting times of all the frames (array of shape (n_frames,)).

        Starting times are computed by considering that the first frame is
        centered at time 0 and returned as an array of floats values with
        starting times in seconds.
        """
        win_len = self.tf_params['win_len'] if 'win_len' in self.tf_params \
            else 1
        fs = self.signal_params['fs'] if 'fs' in self.signal_params else 1

        return self.mid_times - np.floor((win_len - 1) / 2) / fs

    @property
    def mid_times(self):
        """Middle times of all the frames (array of shape (n_frames,)).

        Middle times are computed by considering that the first frame is
        centered at time 0 and returned as an array of floats values with
        middle times in seconds.
        """
        hop = self.tf_params['hop'] if 'hop' in self.tf_params else 1
        fs = self.signal_params['fs'] if 'fs' in self.signal_params else 1

        return np.arange(self.n_frames) * hop / fs

    @property
    def end_times(self):
        """Ending times of all the frames (array of shape (n_frames,)).

        End times are computed by considering that the first frame is
        centered at time 0 and returned as an array of floats values with
        ending times in seconds.
        """
        win_len = self.tf_params['win_len'] if 'win_len' in self.tf_params \
            else 1
        fs = self.signal_params['fs'] if 'fs' in self.signal_params else 1
        return self.mid_times + np.floor((win_len - 1) / 2) / fs

    @property
    def magnitude_spectrogram(self):
        """Magnitude spectrogram (TfData)."""
        return TfData(np.abs(self), mask=self.get_unknown_mask('magnitude'))

    @property
    def energy_spectrogram(self):
        """Power spectrogram (TfData)."""
        return TfData(np.abs(self)**2, mask=self.get_unknown_mask('magnitude'))

    @property
    def phase(self):
        """Phase (TfData)."""
        # np.angle does not return a TfData object
        return TfData(np.angle(self), mask=self.get_unknown_mask('phase'),
                      tf_params=self.tf_params,
                      signal_params=self.signal_params)

    def signal_is_complex(self):
        """Indicate if the TF representation includes negative frequencies."""
        if 'n_bins' not in self.tf_params:
            errmsg = 'Missing information in `tf_params`: n_bins'
            raise ValueError(errmsg)

        return self.n_frequencies == self.tf_params['n_bins']

    def plot_spectrogram(self, mask_type='any', **kwargs):
        """Display the spectrogram of the STFT.

        Parameters
        ----------
        mask_type : {'any', 'all', 'magnitude', 'phase', 'magnitude_only', \
                    'phase_only'}, optional
            Type of mask to be displayed as unknown data.

        Other Parameters
        ----------------
        **kwargs : :func:`~ltfatpy.gabor.tfplot.tfplot` properties, optional
            `kwargs` are used to specify properties like the dynamic range,
            colormap, and so on. See documentation of
            :func:`~ltfatpy.gabor.tfplot.tfplot`. Note that the sampling
            frequency may not be included in `kwargs` since it is read from
            attribute :attr:`signal_params`.

        Returns
        -------
        numpy.ndarray
            The processed image data used in the plotting as returned by
            :meth:`~ltfatpy.gabor.plotdgt.plotdgt` or
            :meth:`~ltfatpy.gabor.plotdgt.plotdgtreal`.
        """
        mask = self.get_unknown_mask(mask_type)
        array = np.array(self)
        array[mask] = np.nan

        if len(plt.gcf().axes) > 1:
            plt.gcf().delaxes(plt.gcf().axes[1])
            plt.gcf().subplots_adjust(right=1.1)

        # clear the current axis
        if self.signal_is_complex():
            image_data = plotdgt(coef=array,
                                 a=self.tf_params['hop'],
                                 fs=self.signal_params['fs'],
                                 **kwargs)

        else:
            image_data = plotdgtreal(coef=array,
                                     a=self.tf_params['hop'],
                                     M=self.n_frequencies,
                                     fs=self.signal_params['fs'],
                                     **kwargs)
        return image_data

    def plot_mask(self, mask_type='any', **kwargs):
        """Display the mask as an image, with several possible mask types

        Parameters
        ----------
        mask_type : {'any', 'all', 'magnitude', 'phase', 'magnitude only', \
                    'phase only'}, optional
            Type of mask to be displayed, with True values for unknown data.

        Other Parameters
        ----------------
        **kwargs : :func:`~ltfatpy.gabor.tfplot.tfplot` properties, optional
            `kwargs` are used to specify properties like the dynamic range,
            colormap, and so on. See documentation of
            :func:`~ltfatpy.gabor.tfplot.tfplot`. Note that the sampling
            frequency may not be included in `kwargs` since it is read from
            attribute :attr:`signal_params`.

        Returns
        -------
        numpy.ndarray
            The processed image data used in the plotting as returned by
            :meth:`~ltfatpy.gabor.plotdgt.plotdgt` or
            :meth:`~ltfatpy.gabor.plotdgt.plotdgtreal`.
        """

        mask = self.get_unknown_mask(mask_type)

        if self.signal_is_complex():
            image_data = plotdgt(coef=mask,
                                 a=self.tf_params['hop'],
                                 fs=self.signal_params['fs'],
                                 clim=(0, 1),
                                 normalization='lin',
                                 **kwargs)
        else:
            image_data = plotdgtreal(coef=mask,
                                     a=self.tf_params['hop'],
                                     M=self.n_frequencies,
                                     fs=self.signal_params['fs'],
                                     clim=(0, 1),
                                     normalization='lin',
                                     **kwargs)
        return image_data

    def copy(self):
        """Copy the object.

        Returns
        -------
        TfData
        """
        return TfData(self)

    def __str__(self):
        string = ['========================',
                  'TF representation',
                  '------------------------',
                  'TF parameters',
                  '{}'.format(self.tf_params),
                  '------------------------',
                  'Signals parameters',
                  '{}'.format(self.signal_params),
                  '------------------------',
                  '{} frequency bins'.format(self.n_frequencies),
                  '{} frames'.format(self.n_frames)]

        return '\n'.join(string)

    def __repr__(self):
        string = '<TfData at {}>'
        return string.format(hex(id(self)))
