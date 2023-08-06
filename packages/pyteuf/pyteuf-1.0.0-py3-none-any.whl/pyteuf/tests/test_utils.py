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
"""Test of the :mod:pyteuf.utils module.

.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Florent Jaillet
"""
import pytest
import numpy as np

from pyteuf.utils import make_random_stft_parameters


class TestFunctions:

    def test_make_random_stft_parameters(self):

        res = make_random_stft_parameters()

        expected_keys = {
            'win_name', 'win_len', 'hop', 'n_bins', 'param_constraint',
            'zero_pad_full_sig', 'is_tight', 'win_type', 'convention',
            }

        assert set(res.keys()) == expected_keys

        res = make_random_stft_parameters(win_name_set={'gauss', 'hann'},
                                          with_array=True)

        expected_keys = {
            'win_array', 'hop', 'n_bins', 'param_constraint',
            'zero_pad_full_sig', 'is_tight', 'win_type', 'convention',
            }

        assert set(res.keys()) == expected_keys
