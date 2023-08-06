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
"""Direct and inverse short-time Fourier transforms.

Implementation of the STFT and its inverse computed using :mod:`ltfatpy`.
Module ``pyteuf`` provides a class :class:`Stft` and a class :class:`Istft`,
which are an interface to :mod:`ltfatpy` in order to facilitate the use of
direct and inverse short-time Fourier transforms,  especially for applied
signal processing and engineering purposes. In  particular, it includes some
intuitive and ergonomic ways to choose either an analysis or a synthesis
window, to control transform parameters and boundary effects.

.. _choosing_a_window:

**Choosing a window**: the window contents can be described using a
high-level description, or a low-level array:

* *High-level setting: window name and length*: The user provides the
  window name as a string in ``win_name``, and the characteristic length of
  the window as an integer in ``win_len`` (leaving argument ``win_array``
  to the default None value). In this case, the window is built internally
  when needed. The available windows are the FIR and Gaussian windows
  available in :mod:`ltfatpy`. The characteristic length of a window is its
  actual length in the case of a FIR window, and the standard deviation for
  a Gaussian window (its actual length equals the signal length).

* *Low-level setting: window array*: The user provides an arbitrary window
  vector as an nd-array in ``win_array`` (leaving arguments ``win_name``
  and ``win_len`` to the default None value). The window length is
  automatically set to the length of the array.

.. _analysis_synthesis_windows:

**Analysis and synthesis windows**: depending on the user's motivations,
one may prefer to chooser either the analysis window or the synthesis
window and to obtain the other window automatically. In order to
implement this both in :class:`~pyteuf.tf_transforms.Stft` and
:class:`~pyteuf.tf_transforms.Istft`, the user can set parameter
``win_type`` to ``analysis`` or ``synthesis`` so that the specified
parameters (``win_name``, ``win_len``, ``win_array``) are used to build
either the analysis or the synthesis window; the other related window is
then automatically computed as the canonical dual window.

.. _stft-param-settings:

**Rules on parameter settings**: the :mod:`ltfatpy` implementation requires
constraints on the parameters of the STFT: the transform length must be a
multiple of both the hop size ``hop`` and the number of frequency bins
``n_bins``. This implementation offers three strategies to enforce this
constraint, that can be selected through the parameter ``param_constraint``
that can have three different values:

* ``'pad'``: ``hop`` and ``n_bins`` are kept unchanged, while the transform
  length is adjusted to the smallest multiple of ``n_bins`` by zero-padding
  the signal. This is appropriate when ``hop`` and ``n_bins`` must not
  change while zero-padding is allowed, but the transform length may be
  very large;

* ``'pow2'``: ``hop`` is rounded to the closest power of two, ``n_bins`` is
  rounded to the smallest higher power of two and the transform length is
  adjusted to the smallest multiple of `n_bins` by zero-padding the signal.
  This strategy limits the zero-padding of the signal by adjusting
  parameters ``hop`` and ``n_bins``. As a consequence, the input STFT
  parameters may not be exactly the same as the parameters used in the
  transform;

* ``'fix'``: parameters ``hop`` and ``n_bins`` should satisfy the constraint
  that the transform length is a common multiple of them, otherwise, an
  error is generated. This option is suited to users that want to control
  parameters by themselves without any rounding.

See also :ref:`tutorial on constraints on the transform length
</_notebooks/time_frequency_transform_length_constraint.ipynb>`

.. _boundary-effects:

**Boundary effects**: various usages of the STFT have been observed
regarding the way the first and last signal samples are windowed:

* adding zeros before the first samples and after the last samples such
  that these samples are windowed by several frames;
* getting STFT coefficients coming only from full signal frames, even if
  the reconstruction is not possible or inaccurate at the boundaries of the
  signal;
* considering the signal being circular, such  that frames at the boundary
  of the signal include both samples from the beginning and samples from
  the end of the sound.

By default, the implementation uses the last stategy. It is controlled
using ``zero_pad_full_sig`` to the appropriate value and process the STFT
data carefully:

* if ``zero_pad_full_sig`` is set to False, a circular transform is
  obtained.
* If ``zero_pad_full_sig`` is set to True, the signal is padded with
  ``win_len`` zeros such that frames can include either first samples or
  last samples, but not both. The circular implementation is nonetheless
  used, First and last frames should then be considered with caution).

See also :ref:`tutorial on boundary effects
</_notebooks/time_frequency_boundary_effects.ipynb>`

.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Florent Jaillet
"""
import warnings
from fractions import gcd
from abc import ABC, abstractmethod

import numpy as np

from ltfatpy.comp.arg_firwin import arg_firwin
from ltfatpy.gabor.dgtreal import dgtreal
from ltfatpy.gabor.idgtreal import idgtreal
from ltfatpy.gabor.dgt import dgt
from ltfatpy.gabor.idgt import idgt
from ltfatpy import gabwin, gabdual, gabtight

from madarrays import Waveform

from .tf_data import TfData


def _get_transform_length(sig_len, hop, n_bins, win_len, param_constraint,
                          zero_pad_full_sig):
    """Compute the appropriate transform length from signal length.

    The appropriate transform length depends on the setting used to handle
    boundary effects (see :ref:`Boundary effects <boundary-effects>`), and on
    the type of constraint set on STFT parameters
    (see :ref:`Rules on parameter settings <stft-param-settings>`).

    If ``zero_pad_full_sig`` is True, the signal length is increased by the
    window length (or Gaussian width). If it does not satisfy the constraint
    set on STFT parameters, an exception is raised if ``param_constraint`` is
    'fix', or the value is increased to satisfy the constraint.

    Parameters
    ----------
    sig_len : int
        Original signal length.

    Returns
    -------
    int
        Transform length.
    """
    w_pad = win_len - 1 if zero_pad_full_sig else 0

    y_len = sig_len + w_pad

    if param_constraint == 'fix':

        # y_len must be a multiple of hop and n_bins
        if (y_len % hop) > 0:
            errmsg = '`hop` ({}) is not a divisor of `sig_len` ({}).'
            raise ValueError(errmsg.format(hop, y_len))

        if (y_len % n_bins) > 0:
            errmsg = '`n_bins` ({}) is not a divisor of `sig_len` ({}).'
            raise ValueError(errmsg.format(n_bins, y_len))

        return y_len

    else:
        # y_len is adjusted to the smallest higher multiple of hop and n_bins
        lcm = hop * n_bins // gcd(hop, n_bins)
        return int(np.ceil(y_len / lcm) * lcm)


def _get_win_description(hop, n_bins, win_name=None, win_len=None,
                         win_array=None, is_dual=False, is_tight=False,
                         sig_len=None):
    """Window description, as required by the `g` parameter in
    :func:`~ltfatpy.gabor.gabwin.gabwin`.

    Parameters
    ----------
    hop : int
        Hop size.
    n_bins : int
        Number of bins in the transform.
    win_name : str or None, optional
        Window name.
    win_len : int or None, optional
        Window length.
    win_array : None or array_like, optional
        Window array, as an alternative to ``win_name`` and ``win_len``.
    is_dual : bool or None, optional
        If False, the window specified by the other parameters is computed.
        If True, its the canonical dual window is computed and returned.
    is_tight : bool or None, optional
        If True, the window is adapted to obtain a tight frame (see
        :func:`~ltfatpy.gabor.gabtight.gabtight`). If both `is_dual` and
        `is_tight` are set to True, the tight window is first computed and its
        canonical dual is then
        returned.
    sig_len : int or None, optional
        Signal length. This parameter is required for Gaussian windows and is
        ignored for FIR windows or for windows given by their array.

    Returns
    -------
    dict or array_like
        The type of the output depends on the parameters. If possible, a dict
        is returned in order to keep high-level information. Otherwise, an
        array is returned.

    Raises
    ------
    ValueError
        If neither ``win_name`` nor ``win_array`` are specified.
        If both ``win_name`` and ``win_array`` are specified.
        If ``win_name`` is specified and ``win_len`` is missing.
        If window name is unknown.
    UserWarning
        If both ``win_array`` and ``win_len`` are specified.
    """
    if win_name is None and win_array is None:
        errmsg = 'Window should be specified by setting either `win_name` '\
            'or `win_array`.'
        raise ValueError(errmsg)

    if win_name is not None and win_array is not None:
        errmsg = 'Window cannot be specified by setting both `win_name` and '\
            '`win_array`, only one of them should be set.'
        raise ValueError(errmsg)

    if win_name is not None and win_len is None:
        errmsg = 'Window length `win_len` should be specified.'
        raise ValueError(errmsg)

    if win_name is None:
        if win_len is not None:
            warnmsg = 'Window length argument is ignored.'
            warnings.warn(warnmsg)

    else:
        if win_len < 0:
            errmsg = '`win_len` should be a positive integer (given: {})'
            raise ValueError(errmsg.format(win_len))

    if win_name is not None:

        if win_name == 'gauss' and sig_len is None:
            errmsg = '`sig_len` must be set for a gauss window.'
            raise ValueError(errmsg)

        if win_name not in arg_firwin().union({'gauss', }):
            errmsg = 'Window {} is unknown or not implemented.'
            raise ValueError(errmsg.format(win_name))

        if win_name == 'gauss':
            g_name = {'name': win_name, 'width': win_len}
        else:
            g_name = {'name': win_name, 'M': win_len}

        if is_tight:
            g_name['name'] = ('tight', win_name)
            if is_dual:
                return gabdual(
                    g=gabwin(g=g_name, a=hop, M=n_bins, L=sig_len)[0],
                    a=hop,
                    M=n_bins,
                    L=sig_len)
            else:
                return g_name
        else:
            if is_dual:
                g_name['name'] = ('dual', win_name)
                return g_name
            else:
                return g_name
    else:
        if is_tight:
            g_tight = gabtight(g=win_array, a=hop, M=n_bins, L=sig_len)
            if is_dual:
                return gabdual(g=g_tight, a=hop, M=n_bins, L=sig_len)
            else:
                return g_tight
        else:
            if is_dual:
                return gabdual(g=win_array, a=hop, M=n_bins, L=sig_len)
            else:
                return gabwin(g=win_array, a=hop, M=n_bins, L=sig_len)[0]

class BaseStft(ABC):
    """Base class for direct and inverse short-time Fourier transforms.

    Parameters
    ----------
    hop : int
        Desired hop size in samples. Subject to rounding
        (see :ref:`Rules on parameter settings <stft-param-settings>`).
    n_bins : int
        Desired number of frequency bins in samples. Subject to rounding
        (see :ref:`Rules on parameter settings <stft-param-settings>`).
    win_type : {'analysis', 'synthesis'}, optional
        Type of the window (see :ref:`Analysis and synthesis windows
        <analysis_synthesis_windows>`).
    win_name : None or str, optional
        Window type among 'gauss' or one of the FIR windows listed in
        :func:`~ltfatpy.sigproc.firwin.firwin`
        (see :ref:`Choosing a window <choosing_a_window>`).
    win_len : None or int, optional
        If win_name is set, FIR window length or Gaussian window width,
        in samples
        (see :ref:`Choosing a window <choosing_a_window>`).
    win_array : None or array_like, optional
        Window array, as an alternative to win_name and win_len
        (see :ref:`Choosing a window <choosing_a_window>`).
    is_tight : bool, optional
        If True, the window is adapted to obtain a tight frame (see
        :func:`~ltfatpy.gabor.gabtight.gabtight`). If both
        `is_dual='synthesis'` and `is_tight=True` are set, the tight synthesis
        window is first computed and the related analysis window is then
        computed.
    convention : {'lp', 'bp'}
        Type of convention : 'lp' for low-pass (i.e. frequency invariant) or
        'bp' for band-pass (i.e. time invariant).
    """

    def __init__(self, hop, n_bins, win_type='analysis', win_name=None,
                 win_len=None, win_array=None, is_tight=False,
                 convention='lp'):

        # Hop
        if int(hop) < 0:
            errmsg = '`hop` should be a positive integer (given: {})'
            raise ValueError(errmsg.format(hop))
        self._hop = hop

        # Number of frequency bins
        if int(n_bins) < 0:
            errmsg = '`n_bins` should be a positive integer (given: {})'
            raise ValueError(errmsg.format(n_bins))
        self._n_bins = n_bins

        # Type of window
        if win_type not in {'analysis', 'synthesis'}:
            errmsg = 'Unknown value for `win_type`: {}'
            raise ValueError(errmsg.format(win_type))
        self._win_type = win_type

        # Window
        sig_len = self.hop * self.n_bins // gcd(self.hop, self.n_bins)

        is_dual = self.win_type == 'synthesis'
        # get window descriptions for checking parameters only
        _get_win_description(hop=hop, n_bins=n_bins, win_name=win_name,
                             win_len=win_len, win_array=win_array,
                             is_dual=is_dual, is_tight=is_tight,
                             sig_len=sig_len)

        self._win_len = win_len
        self._win_name = win_name
        self._raw_win_array = win_array
        self._is_tight = is_tight

        # get STFT convention
        if convention not in {'lp', 'bp'}:
            errmsg = 'Unknown value for `convention`: {}'
            raise ValueError(errmsg.format(convention))
        self._convention = convention

    @property
    def n_bins(self):
        """Actual number of frequency bins (int).

        If parameter `param_constraint` is set to 'pow2', the actual value is
        automatically computed from the desired number of bins
        (see :ref:`rules on parameter settings <stft-param-settings>`).
        """
        return self._n_bins

    @property
    def hop(self):
        """ Actual hop size (int).

        If parameter `param_constraint` is set to 'pow2', the
        actual value is automatically computed from the desired hop size
        (see :ref:`Rules on parameter settings <stft-param-settings>`).
        """
        return self._hop

    @property
    def win_type(self):
        """Window type ({'analysis', 'synthesis'}).
        """
        return self._win_type

    @property
    def win_len(self):
        """Window length (None or int).

        None if window is defined by `win_array`.
        """
        return self._win_len

    @property
    def win_name(self):
        """Window name (None or str).

        None if window is defined by `win_array`.
        """
        return self._win_name

    @property
    def raw_win_array(self):
        """Window array (None or array_like).

        Window array if parameter `win_array` has been specified at object
        creation. If `is_tight` is `True`, attribute :attr:`raw_win_array`
        may differ from parameter `win_array`.
        """
        return self._raw_win_array

    @property
    def is_tight(self):
        """Tight frame flag (bool)."""
        return self._is_tight

    @property
    def convention(self):
        """Type of convention ({'lp', 'bp'}).

        Type of convention : 'lp' for low-pass (i.e. frequency invariant) or
        'bp' for band-pass (i.e. time invariant).
        """
        return self._convention

    def get_params(self):
        """Returns the parameters of the transform."""
        return {'hop': self.hop,
                'n_bins': self.n_bins,
                'win_name': self.win_name,
                'win_len': self.win_len,
                'win_array': self.raw_win_array,
                'win_type': self.win_type,
                'is_tight': self.is_tight,
                'convention': self.convention}

    def get_win_array(self, sig_len=None, compute_dual=False):
        """ Window array.

        Parameters
        ----------
        sig_len : int
            Length of the signal. Needed for a Gaussian window, otherwise, this
            parameter has no effect.
        compute_dual : bool
            If ``False``, compute the window specified by the attributes
            ``win_name``, ``win_len``, and so on. If ``True``, compute the
            dual of this window.

        Returns
        -------
        array_like
        """
        # TODO (future) add an option to switch end/beginning or add a second output for time indices

        compute_dual = self.win_type == 'synthesis'

        return gabwin(g=_get_win_description(win_name=self.win_name,
                                             win_len=self.win_len,
                                             win_array=self.raw_win_array,
                                             is_dual=compute_dual,
                                             is_tight=self.is_tight,
                                             hop=self.hop,
                                             n_bins=self.n_bins,
                                             sig_len=sig_len),
                      a=self.hop,
                      M=self.n_bins,
                      L=sig_len)[0]

    def __str__(self):
        string = []

        if self.win_name is None:
            string.append('Built-in {} window, {} samples'.format(
                self.win_type, len(self.raw_win_array)))
        else:
            string.append('Specified {} window: {}, {} samples'
                          .format(self.win_type, self.win_name, self.win_len))
        string.append('Tight: {}'.format(self.is_tight))
        string.append('Hop length: {} samples'.format(self.hop))
        string.append('{} frequency bins'.format(self.n_bins))
        string.append('Convention: {}'.format(self.convention))
        string.append('*' * 64)

        return string


class Stft(BaseStft):
    """Short-time Fourier transform object for 1D signals.

    Parameters
    ----------
    hop : int
        Desired hop size in samples. Subject to rounding
        (see :ref:`Rules on parameter settings <stft-param-settings>`).
    n_bins : int
        Desired number of frequency bins in samples. Subject to rounding
        (see :ref:`Rules on parameter settings <stft-param-settings>`).
    win_type : {'analysis', 'synthesis'}, optional
        Type of the window. If 'synthesis', the canonical dual window is
        computed as the analysis window (see
        :ref:`Analysis and synthesis windows <analysis_synthesis_windows>`).
    win_name : None or str, optional
        Window type among 'gauss' or one of the FIR windows listed in
        :func:`~ltfatpy.sigproc.firwin.firwin`
        (see :ref:`Choosing a window <choosing_a_window>`).
    win_len : None or int, optional
        If win_name is set, FIR window length or Gaussian window width,
        in samples
        (see :ref:`Choosing a window <choosing_a_window>`).
    win_array : None or array_like, optional
        Window array, as an alternative to win_name and win_len
        (see :ref:`Choosing a window <choosing_a_window>`).
    is_tight : bool, optional
        If True, the window is adapted to obtain a tight frame (see
        :func:`~ltfatpy.gabor.gabtight.gabtight`). If both
        `is_dual='synthesis'` and `is_tight=True` are set, the tight synthesis
        window is first computed and the related analysis window is then
        computed.
    param_constraint : {'fix', 'pad', 'pow2'}, optional
        Strategy to adjust parameters hop and n_bins
        (see :ref:`Rules on parameter settings <stft-param-settings>`).
    zero_pad_full_sig : bool, optional
        If True, the full signal is padded with win_len zeros to avoid a
        circular transform (see :ref:`Boundary effects <boundary-effects>`).
    convention : {'lp', 'bp'}
        Type of convention : 'lp' for low-pass (i.e. frequency invariant) or
        'bp' for band-pass (i.e. time invariant).
    """

    def __init__(self, hop, n_bins, win_type='analysis', win_name=None,
                 win_len=None, win_array=None, is_tight=False,
                 param_constraint='fix', zero_pad_full_sig=True,
                 convention='lp'):

        super().__init__(hop, n_bins, win_type=win_type, win_name=win_name,
                         win_len=win_len, win_array=win_array,
                         is_tight=is_tight, convention=convention)

        # Parameters constraint
        if param_constraint not in ['pow2', 'fix', 'pad']:
            errmsg = 'Unknown value for `param_constraint`: {}'
            raise ValueError(errmsg.format(param_constraint))
        self._param_constraint = param_constraint

        # Hop
        if self.param_constraint == 'pow2':
            self._hop = int(2**np.round(np.log2(self.hop)))
        else:
            self._hop = int(self.hop)

        # Number of frequency bins
        if self.param_constraint == 'pow2':
            self._n_bins = int(2**np.ceil(np.log2(self.n_bins)))
        else:
            self._n_bins = int(self.n_bins)
        if zero_pad_full_sig and win_name == 'gauss':
            raise ValueError('Cannot pad full signal if win_name is gauss, '
                             'use a FIR window instead or set '
                             'zero_pad_full_sig=False')
        self._zero_pad_full_sig = zero_pad_full_sig

    @property
    def param_constraint(self):
        """Strategy to adjust `hop` and `n_bins` ({'fix', 'pad', 'pow2'}).

        See :ref:`Rules on parameter settings <stft-param-settings>`.
        """
        return self._param_constraint

    @property
    def zero_pad_full_sig(self):
        """Zero padding flag (bool).

        If True, the full signal is padded with win_len zeros to avoid a
        circular transform (see :ref:`Boundary effects <boundary-effects>`).
        """
        return self._zero_pad_full_sig

    def get_params(self):
        """Returns the parameters of the Stft."""
        tf_params = super().get_params()
        tf_params['param_constraint'] = self.param_constraint
        tf_params['zero_pad_full_sig'] = self.zero_pad_full_sig
        return tf_params

    def get_win_array(self, sig_len=None):
        """Analysis window array.

        Parameters
        ----------
        sig_len : int
            Length of the signal. Needed for a Gaussian window, otherwise, this
            parameter has no effect.

        Returns
        -------
        array_like
        """
        compute_dual = self.win_type == 'synthesis'
        return super().get_win_array(sig_len=sig_len,
                                     compute_dual=compute_dual)

    def apply(self, x, fs=None):
        """Compute Short-Time Fourier Transform of a signal.

        Parameters
        ----------
        x : array_like
            Input signal to be transformed.

        Returns
        -------
        TfData
            Time-frequency matrix with related parameters. If input `x` is
            real, only coefficients for non-negative frequencies are returned.
        """
        if fs is None and isinstance(x, Waveform):
            fs = x.fs

        y_len = _get_transform_length(x.shape[0], hop=self.hop,
                                      n_bins=self.n_bins, win_len=self.win_len,
                                      param_constraint=self.param_constraint,
                                      zero_pad_full_sig=self.zero_pad_full_sig)

        is_dual = self.win_type == 'synthesis'
        g = _get_win_description(win_name=self.win_name,
                                 win_len=self.win_len,
                                 win_array=self.raw_win_array,
                                 is_dual=is_dual,
                                 is_tight=self.is_tight,
                                 hop=self.hop,
                                 n_bins=self.n_bins,
                                 sig_len=y_len)

        pt = 'freqinv' if self.convention == 'lp' else 'timeinv'

        if np.iscomplexobj(x):
            X, _, g = dgt(x, g=g, a=self.hop, M=self.n_bins, L=y_len, pt=pt)
        else:
            X, _, g = dgtreal(x, g=g, a=self.hop,
                              M=self.n_bins, L=y_len, pt=pt)

        return TfData(data=X, tf_params=self.get_params(),
                      signal_params={'fs': fs, 'sig_len': x.shape[0]})

    def get_istft(self):
        """Return the inverse STFT (canonical dual) with the same parameters.

        Returns
        -------
        :class:`~pyteuf.tf_transforms.Istft`
        """
        return Istft(win_name=self.win_name,
                     win_len=self.win_len,
                     win_type=self.win_type,
                     win_array=self.raw_win_array,
                     is_tight=self.is_tight,
                     hop=self.hop,
                     n_bins=self.n_bins,
                     convention=self.convention)

    def apply_adjoint(self, x):
        """Apply the adjoint operator of the current STFT.

        Parameters
        ----------
        x : TfData
            Adjoint operator.

        Returns
        -------
        array_like
        """
        if np.iscomplexobj(x):
            win_type = 'analysis' if self.win_type == 'synthesis' \
                else 'synthesis'

            return Istft(win_name=self.win_name,
                         win_len=self.win_len,
                         win_type=win_type,
                         win_array=self.raw_win_array,
                         is_tight=self.is_tight,
                         hop=self.hop,
                         n_bins=self.n_bins,
                         convention=self.convention).apply(x)
        else:
            raise NotImplementedError(
                'DGT adjoint operator for real signal is not valid (not '
                'correctly implemented yet), you may use (artificially) '
                'complex signals as inputs.')

    def __str__(self):
        string = super().__str__()
        string.insert(0, '*' * 29 + ' STFT ' + '*' * 29)

        string.insert(-1, 'param_constraint: {}'.format(self.param_constraint))
        string.insert(-1, 'zero_pad_full_sig: {}'.format(
            self.zero_pad_full_sig))

        return '\n'.join(string)


class Istft(BaseStft):
    """Inverse short-time Fourier transform for STFT representations.

    Parameters
    ----------
    hop : int
        Hop size in samples.
    n_bins : int
        Number of frequency bins.
    win_name : None or str, optional
        Window name (None if window is defined by `win_array`).
    win_len : None or int, optional
        Window length (None if window is defined by `win_array`).
    win_array : None or :class:`~numpy.ndarray`, optional
        Window array, as an alternative to win_name and win_len
        (see :ref:`Choosing a window <choosing_a_window>`).
    win_type : {'synthesis', 'analysis'}, optional
        Type of the window. If ``'synthesis'``, the canonical dual window is
        computed as the analysis window (see
        :ref:`Analysis and synthesis windows <analysis_synthesis_windows>`).
    is_tight : bool, optional
        If True, the window is adapted to obtain a tight frame (see
        :func:`~ltfatpy.gabor.gabtight.gabtight`). If both
        `is_dual='analysis'` and `is_tight=True` are set, the tight analysis
        window is first computed and the related synthesis window is then
        computed.
    convention : {'lp', 'bp'}
        Type of convention : 'lp' for low-pass (i.e. frequency invariant) or
        'bp' for band-pass (i.e. time invariant).
    """

    def __init__(self, hop, n_bins, win_name=None, win_len=None,
                 win_array=None, win_type='synthesis', is_tight=False,
                 convention='lp'):

        super().__init__(hop, n_bins, win_type=win_type, win_name=win_name,
                         win_len=win_len, win_array=win_array,
                         is_tight=is_tight, convention=convention)

    def get_win_array(self, sig_len=None):
        """Synthesis window array.

        Parameters
        ----------
        sig_len : int
            Length of the signal. Needed for a Gaussian window, otherwise, this
            parameter has no effect.

        Returns
        -------
        array
        """
        compute_dual = self.win_type == 'analysis'
        return super().get_win_array(sig_len=sig_len,
                                     compute_dual=compute_dual)

    def apply(self, X, signal_params=None):
        """Apply inverse short-time Fourier transform.

        Parameters
        ----------
        X : array_like
            Stft coefficients to be inverse-transformed.

        Returns
        -------
        :class:`~madarrays.waveform.Waveform`
        """

        if not isinstance(X, TfData):
            if signal_params is None:
                signal_params = {'sig_len': X.shape[1] * self.hop, 'fs': 1}
            X = TfData(X, tf_params=self.get_params(),
                       signal_params=signal_params)

        is_dual = self.win_type == 'analysis'

        g = _get_win_description(win_name=self.win_name,
                                 win_len=self.win_len,
                                 win_array=self.raw_win_array,
                                 is_dual=is_dual,
                                 is_tight=self.is_tight,
                                 hop=self.hop,
                                 n_bins=self.n_bins,
                                 sig_len=X.signal_params['sig_len'])

        pt = 'freqinv' if self.convention == 'lp' else 'timeinv'

        if X.signal_is_complex():
            y, _ = idgt(X, g=g, a=self.hop, Ls=X.signal_params['sig_len'],
                        pt=pt)
        else:
            y, _ = idgtreal(X, g=g, a=self.hop, M=self.n_bins,
                            Ls=X.signal_params['sig_len'], pt=pt)

        return Waveform(y, fs=X.signal_params['fs'])

    def __str__(self):
        string = super().__str__()
        string.insert(0, '*' * 28 + ' ISTFT ' + '*' * 29)

        return '\n'.join(string)
