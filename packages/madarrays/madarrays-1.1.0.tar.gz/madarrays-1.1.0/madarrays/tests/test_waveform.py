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
# Python package for audio data structures with missing entries
#
# Licence
# -------
# This file is part of madarrays.
#
# madarrays is free software: you can redistribute it and/or modify
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
"""Test of the module :mod:`waveform`.

NOTE: This module uses random generation for some tests, the use of
pytest-randomly is recommanded to manage the seeds used in these tests.

TODO: handle warnings with `astype` methods (currenly, all warnings are caught
using 'warnings.catch_warnings(record=True)').

.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Florent Jaillet
"""
import pickle
import pytest
import tempfile
import unittest.mock as mock
import warnings


import simpleaudio as sa

import matplotlib.pyplot as plt
import numpy as np

from scipy.io import wavfile
from IPython.display import Audio

from madarrays.mad_array import MadArray
from madarrays.waveform import Waveform

from .utils import assert_array_less_or_equal
from .utils import generate_mask_50

FLT_DTYPES = [np.float16, np.float32, np.float64]
INT_DTYPES = [np.uint8, np.int16, np.int32]
CPX_DTYPES = [np.complex64, np.complex128]

FLT_EPS = {s: np.finfo(s).eps for s in FLT_DTYPES}
CPX_EPS = {s: np.finfo(s).eps for s in CPX_DTYPES}
INT_MAX = {s: np.iinfo(s).max for s in INT_DTYPES}
INT_MIN = {s: np.iinfo(s).min for s in INT_DTYPES}
INT_ZERO = {s: (np.iinfo(s).max + np.iinfo(s).min + 1) / 2 for s in INT_DTYPES}

FS = [8000, 16000, 32000, 48000, 11025, 22050, 44100, 88200]


def assert_clipping(x_clipped, x_ref, min_value, max_value):
    """Test clipping of a referenced signal given min and max values."""

    ind_clipped_max = x_ref > max_value
    ind_clipped_min = x_ref < min_value
    ind_nonclipped = np.logical_and(~ind_clipped_max, ~ind_clipped_min)

    err_msg = 'Large values have not been clipped correctly'
    np.testing.assert_almost_equal(x_clipped[ind_clipped_max],
                                   max_value,
                                   err_msg=err_msg)

    err_msg = 'Small values have not been clipped correctly'
    np.testing.assert_almost_equal(x_clipped[ind_clipped_min],
                                   min_value, err_msg=err_msg)

    err_msg = 'Non-clipped values have been modified'
    np.testing.assert_almost_equal(x_clipped[ind_nonclipped],
                                   x_ref[ind_nonclipped], err_msg=err_msg)


@pytest.fixture(scope='class')
def get_data(request):

    request.cls.fs = np.random.choice(FS)
    request.cls.length = np.random.randint(
        request.cls.fs*2, request.cls.fs * 3)

    request.cls.x_mono = np.random.rand(request.cls.length)
    request.cls.x_mono_2 = np.random.rand(request.cls.length, 1)
    request.cls.m_mono = generate_mask_50(request.cls.length)

    request.cls.x_stereo = np.random.rand(request.cls.length, 2)
    request.cls.m_stereo = np.stack((generate_mask_50(request.cls.length),
                                     generate_mask_50(request.cls.length)),
                                    axis=-1)

    # Toy signals
    request.cls.w_float_ref = {s: Waveform(np.array(
        [-1] * 4 + [-0.5, 0, 0.5] + [1 - FLT_EPS[s]] * 4, dtype=s), fs=1)
        for s in FLT_DTYPES}

    request.cls.w_int_ref = {s: Waveform(np.array(
        [INT_MIN[s]] * 4 +
        [(INT_MIN[s] + INT_ZERO[s] + 1) // 2] +
        [INT_ZERO[s]] +
        [(INT_MAX[s] + INT_ZERO[s] + 1) // 2] +
        [INT_MAX[s]] * 4, dtype=s), fs=1) for s in INT_DTYPES}

    request.cls.w_complex_ref = {s: Waveform((1 + 1j) * np.array(
        [-1] * 4 + [-0.5, 0, 0.5] + [1 - CPX_EPS[s]] * 4,
        dtype=s), fs=1) for s in CPX_DTYPES}

    request.cls.w_float_clip = {s: Waveform(np.array(
        [-100, -2, -1.1, -1, -0.5, 0, 0.5, 1, 1, 2, 100],
        dtype=s), fs=1) for s in FLT_DTYPES}

    request.cls.w_complex_clip = {s: Waveform((1 + 1j) * np.array(
        [-100, -2, -1.1, -1, -0.5, 0, 0.5, 1, 1.1, 2, 100], dtype=s), fs=1)
        for s in CPX_DTYPES}


@pytest.mark.usefixtures('get_data')
class TestWaveform:

    def test_init_mono(self):

        w = Waveform(self.x_mono, mask=self.m_mono)

        assert w.fs == 1
        assert w.length == self.length
        assert w.duration == self.length
        assert not w.is_stereo()
        np.testing.assert_equal(w.time_axis, np.arange(self.length))

        w = Waveform(data=self.x_mono, mask=self.m_mono, fs=self.fs)

        assert w.fs == self.fs
        assert w.length == self.length
        assert w.duration == self.length / self.fs
        np.testing.assert_equal(w.time_axis, np.arange(self.length) / self.fs)

        w = Waveform(data=self.x_mono_2, mask=self.m_mono, fs=self.fs)

        assert w.fs == self.fs
        assert w.length == self.length
        assert w.duration == self.length / self.fs
        np.testing.assert_equal(w.time_axis, np.arange(self.length) / self.fs)

    def test_init_stereo(self):

        w = Waveform(self.x_stereo, mask=self.m_stereo)

        assert w.fs == 1
        assert w.length == self.length
        assert w.duration == self.length
        assert w.is_stereo()
        np.testing.assert_equal(w.time_axis, np.arange(self.length))

        w = Waveform(data=self.x_stereo, mask=self.m_stereo, fs=self.fs)

        assert w.fs == self.fs
        assert w.length == self.length
        assert w.duration == self.length / self.fs
        np.testing.assert_equal(w.time_axis, np.arange(self.length) / self.fs)

    def test_init_raises(self):

        # Non-stereo
        with pytest.raises(ValueError,
                           match='`data` should be either mono or stereo.'):
            Waveform(np.random.rand(100, 1000), fs=44100)

        # Non 1D or 2D array
        with pytest.raises(ValueError,
                           match='`data` should be either mono or stereo.'):
            Waveform(np.random.rand(2, 100, 1000), fs=44100)

        # Negative frequency sampling
        match = 'fs is not strictly positive \(given: -\d+\)'
        with pytest.raises(ValueError, match=match):
            Waveform(self.x_mono, fs=-self.fs)

        # Frequency sampling equal to 0
        with pytest.raises(ValueError,
                           match='fs is not strictly positive \(given: 0\)'):
            Waveform(self.x_mono, fs=0)

    def test_init_from_waveform(self):

        w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)
        w2 = Waveform(w)
        assert w2.fs == self.fs
        np.testing.assert_array_equal(w._mask, w2._mask)

    def test_init_from_madarray(self):

        w = MadArray(self.x_mono, mask=self.m_mono)
        w2 = Waveform(w)
        np.testing.assert_array_equal(w2._mask, w._mask)

        w = MadArray(self.x_mono, mask_magnitude=self.m_mono)
        match = ('Construction of a Waveform from a MadArray with '
                 'complex masking: the original masking data are '
                 'discarded and a boolean mask set to False is used.')
        with pytest.warns(UserWarning, match=match):
            w2 = Waveform(w)
            np.testing.assert_array_equal(
                w2._mask, np.zeros_like(w2, dtype=np.bool))

    def test_resample(self):

        # Common integer values
        for fs in FS:
            # Mono
            w = Waveform(self.x_mono, fs=self.fs)
            w.resample(fs=fs)

            assert w.fs == fs
            assert w.length == int(np.floor(fs / self.fs * self.length))
            assert not w.is_stereo()
            print(self.length, self.fs)
            assert w.duration == pytest.approx(self.length / self.fs, 1e-4)
            np.testing.assert_equal(
                w.time_axis,
                np.arange(np.floor(fs / self.fs * self.length)) / fs)

            # Stereo
            w = Waveform(self.x_stereo, fs=self.fs)
            w.resample(fs=fs)

            assert w.fs == fs
            assert w.length == int(np.floor(fs / self.fs * self.length))
            assert w.is_stereo()
            assert w.duration == pytest.approx(self.length / self.fs, 1e-4)
            np.testing.assert_equal(
                w.time_axis,
                np.arange(np.floor(fs / self.fs * self.length)) / fs)

        # Floating values with ratios that are exact rationals
        for (old_fs, new_fs) in [(1, 1.5), (0.5, 3), (100.1, 200.2)]:
            w = Waveform(self.x_mono, fs=old_fs)
            w.resample(fs=new_fs)
            assert w.fs == new_fs
            assert w.length == int(new_fs / old_fs * self.length)

        # Floating values with ratios that are not well approximated
        # by rationals
        old_fs = np.sqrt(2)
        new_fs = np.pi
        with pytest.warns(UserWarning):
            w = Waveform(self.x_mono, fs=old_fs)
            w.resample(fs=new_fs)
            np.testing.assert_almost_equal(w.fs, new_fs)
            np.testing.assert_almost_equal(
                w.length, int(new_fs * self.length / old_fs))

        # Negative frequency sampling
        with pytest.raises(
                ValueError,
                match='`fs` should be a positive number \(given: -\d+\)'):
            w.resample(fs=-self.fs)

        # Frequency sampling equal to 0
        with pytest.raises(
                ValueError,
                match='`fs` should be a positive number \(given: 0\)'):
            w.resample(fs=0)

        # Masked data
        w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)
        with pytest.raises(ValueError, match='Waveform has missing entries.'):
            w.resample(fs=fs)

    def test_set_rms(self):

        # Float
        w = Waveform(self.x_mono, fs=self.fs)
        assert w.rms == pytest.approx(np.sqrt(1 / 3), 1e-1)

        w.set_rms(1)
        assert w.rms == pytest.approx(1, 1e-7)
        assert np.sqrt(np.mean(w**2)) == pytest.approx(1, 1e-7)

        # Negative rms
        with pytest.raises(
                ValueError,
                match='`rms` should be a positive float \(given: -1\)'):
            w.set_rms(-1)

        # Int
        w = Waveform(self.x_mono, fs=self.fs)
        for w_int in self.w_int_ref.values():
            # Getting RMS
            with pytest.raises(
                    NotImplementedError,
                    match='RMS is not available for integer data types'):
                w_int.rms

    def test_clip_float(self):

        min_value = -np.random.rand() * np.random.randint(100)
        max_value = np.random.rand() * np.random.randint(100)

        x_noclip = np.linspace(min_value, max_value, 1000)
        x_below_clip = np.linspace(min_value - 1, max_value, 1000)
        x_above_clip = np.linspace(min_value, max_value + 1, 1000)

        # No clipping
        w = Waveform(x_noclip)
        w.clip(max_value=max_value, min_value=min_value)

        assert_clipping(x_clipped=w, x_ref=x_noclip,
                        min_value=min_value, max_value=max_value)

        # Clipping from below
        w = Waveform(x_below_clip)
        match = 'float\d+ values lower than -\d+.\d+ have been clipped.'
        with pytest.warns(UserWarning, match=match):
            w.clip(min_value=min_value)
        assert_clipping(x_clipped=w, x_ref=x_below_clip,
                        min_value=min_value, max_value=max_value)

        # Clipping by above
        w = Waveform(x_above_clip)
        match = 'float\d+ values greater than \d+.\d+ have been clipped.'
        with pytest.warns(UserWarning, match=match):
            w.clip(max_value=max_value)

        assert_clipping(x_clipped=w, x_ref=x_above_clip,
                        min_value=min_value, max_value=max_value)

    def test_clip_complex(self):

        min_value = -np.random.rand() * np.random.randint(100)
        max_value = np.random.rand() * np.random.randint(100)

        x_noclip = (np.linspace(min_value, max_value, 1000) +
                    1j * np.linspace(min_value, max_value, 1000))
        x_real_below_clip = (np.linspace(min_value - 1, max_value, 1000) +
                             1j * np.linspace(min_value, max_value, 1000))
        x_imag_above_clip = (np.linspace(min_value, max_value, 1000) +
                             1j * np.linspace(min_value, max_value + 1, 1000))

        # No clipping
        w = Waveform(x_noclip)
        w.clip(max_value=max_value, min_value=min_value)

        assert_clipping(x_clipped=np.real(w), x_ref=np.real(x_noclip),
                        min_value=min_value, max_value=max_value)
        assert_clipping(x_clipped=np.imag(w), x_ref=np.imag(x_noclip),
                        min_value=min_value, max_value=max_value)

        # Clipping from below of the real part
        match = 'Real part of the complex entries: float\d+ values lower than'\
                ' -\d+.\d+ have been clipped.'
        w = Waveform(x_real_below_clip)

        with pytest.warns(UserWarning, match=match):
            w.clip(max_value=max_value, min_value=min_value)

        assert_clipping(x_clipped=np.real(w), x_ref=np.real(x_real_below_clip),
                        min_value=min_value, max_value=max_value)
        assert_clipping(x_clipped=np.imag(w), x_ref=np.imag(x_real_below_clip),
                        min_value=min_value, max_value=max_value)

        # Clipping by above of the imaginary part
        match = 'Imaginary part of the complex entries: float\d+ values '\
                'greater than \d+.\d+ have been clipped.'
        w = Waveform(x_imag_above_clip)

        with pytest.warns(UserWarning, match=match):
            w.clip(max_value=max_value, min_value=min_value)

        assert_clipping(x_clipped=np.real(w), x_ref=np.real(x_imag_above_clip),
                        min_value=min_value, max_value=max_value)
        assert_clipping(x_clipped=np.imag(w), x_ref=np.imag(x_imag_above_clip),
                        min_value=min_value, max_value=max_value)

    def test_astype_float_float(self):

        match = 'float\d+ values greater than \d+.\d+ have been clipped.'
        for dtype_src, w_src in self.w_float_ref.items():
            for dtype_targ, w_targ in self.w_float_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))

                if FLT_EPS[dtype_src] < FLT_EPS[dtype_targ]:
                    with pytest.warns(UserWarning, match=match):
                        w_est = w_src.astype(dtype_targ)
                else:
                    w_est = w_src.astype(dtype_targ)

                assert w_est.dtype == w_targ.dtype

                if FLT_EPS[dtype_src] <= FLT_EPS[dtype_targ]:
                    np.testing.assert_equal(w_est, w_targ)
                else:
                    np.testing.assert_allclose(
                        w_est, w_targ, atol=FLT_EPS[dtype_src], rtol=0)

        for dtype_src, w_src in self.w_float_clip.items():
            for dtype_targ, w_targ in self.w_float_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))
                with pytest.warns(UserWarning, match=match):
                    w_est = w_src.astype(dtype=dtype_targ)

                if FLT_EPS[dtype_src] <= FLT_EPS[dtype_targ]:
                    np.testing.assert_equal(w_est, w_targ)
                else:
                    np.testing.assert_allclose(
                        w_est, w_targ, atol=FLT_EPS[dtype_src], rtol=0)

    def test_astype_int_int(self):
        for dtype_src, w_src in self.w_int_ref.items():
            for dtype_targ, w_targ in self.w_int_ref.items():
                print("Casting from {} to {}.".format(dtype_src, dtype_targ))

                w_est = w_src.astype(dtype_targ)
                atol = ((INT_MAX[dtype_targ] - INT_MIN[dtype_targ] + 1) /
                        (INT_MAX[dtype_src] - INT_MIN[dtype_src] + 1))

                np.testing.assert_allclose(w_est, w_targ, atol=atol, rtol=0)
                assert w_est.dtype == w_targ.dtype

    def test_astype_complex_complex(self):

        match = 'float\d+ values greater than \d+.\d+ have been clipped.'
        for dtype_src, w_src in self.w_complex_ref.items():
            for dtype_targ, w_targ in self.w_complex_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))

                atol = 2 * (CPX_EPS[dtype_src] + CPX_EPS[dtype_targ])

                if CPX_EPS[dtype_src] < CPX_EPS[dtype_targ]:
                    with pytest.warns(UserWarning, match=match):
                        w_est = w_src.astype(dtype_targ)
                else:
                    w_est = w_src.astype(dtype_targ)

                np.testing.assert_allclose(w_est, w_targ, atol=atol, rtol=0)
                assert w_est.dtype == w_targ.dtype

        for dtype_src, w_src in self.w_complex_clip.items():
            for dtype_targ, w_targ in self.w_complex_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))
                atol = 2 * (CPX_EPS[dtype_src] + CPX_EPS[dtype_targ])
                with pytest.warns(UserWarning, match=match):
                    w_est = w_src.astype(dtype=dtype_targ)
                    np.testing.assert_allclose(
                        w_est, w_targ, atol=atol, rtol=0)

    def test_astype_float_int(self):
        match = 'float\d+ values greater than \d+.\d+ have been clipped.'
        for dtype_src, w_src in self.w_float_ref.items():
            for dtype_targ, w_targ in self.w_int_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))
                w_est = w_src.astype(dtype_targ)

                atol = (FLT_EPS[dtype_src] *
                        (INT_MAX[dtype_targ] - INT_MIN[dtype_targ] + 1) / 2)
                np.testing.assert_allclose(w_est, w_targ, atol=atol, rtol=0)
                assert w_est.dtype == w_targ.dtype

        for dtype_src, w_src in self.w_float_clip.items():
            for dtype_targ, w_targ in self.w_int_ref.items():
                with pytest.warns(UserWarning, match=match):
                    print('Casting from {} to {}.'.format(
                        dtype_src, dtype_targ))
                    w_est = w_src.astype(dtype=dtype_targ)
                    np.testing.assert_array_equal(w_est, w_targ)

    def test_astype_int_float(self):
        for dtype_src, w_src in self.w_int_ref.items():
            for dtype_targ, w_targ in self.w_float_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))

                with warnings.catch_warnings(record=True):
                    w_est = w_src.astype(dtype_targ)

                atol = ((INT_MAX[dtype_src] - INT_MIN[dtype_src] + 1) +
                        FLT_EPS[dtype_targ] / 2)
                np.testing.assert_allclose(w_est, w_targ, atol=atol, rtol=0)
                assert w_est.dtype == w_targ.dtype

    def test_astype_float_complex(self):
        match = 'float\d+ values greater than \d+.\d+ have been clipped.'
        for dtype_src, w_src in self.w_float_ref.items():
            for dtype_targ, w_targ in self.w_complex_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))
                atol = FLT_EPS[dtype_src] + CPX_EPS[dtype_targ]

                if FLT_EPS[dtype_src] < CPX_EPS[dtype_targ]:
                    with pytest.warns(UserWarning, match=match):
                        w_est = w_src.astype(dtype_targ)
                else:
                    w_est = w_src.astype(dtype_targ)

                np.testing.assert_allclose(w_est, np.real(w_targ),
                                           atol=atol, rtol=0)
                assert w_est.dtype == w_targ.dtype

        for dtype_src, w_src in self.w_float_clip.items():
            for dtype_targ, w_targ in self.w_complex_ref.items():
                msg = "Casting from {} to {}.".format(dtype_src, dtype_targ)
                atol = FLT_EPS[dtype_src] + CPX_EPS[dtype_targ]
                with pytest.warns(UserWarning, match=match):
                    w_est = w_src.astype(dtype=dtype_targ)
                    np.testing.assert_allclose(w_est,
                                               np.real(w_targ).astype(
                                                   dtype_targ),
                                               atol=atol, rtol=0, err_msg=msg)

    def test_astype_complex_float(self):
        match = 'float\d+ values greater than \d+.\d+ have been clipped.'
        for dtype_src, w_src in self.w_complex_ref.items():
            for dtype_targ, w_targ in self.w_float_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))
                atol = CPX_EPS[dtype_src] + FLT_EPS[dtype_targ]

                if CPX_EPS[dtype_src] < FLT_EPS[dtype_targ]:
                    with pytest.warns(UserWarning, match=match):
                        w_est = w_src.astype(dtype_targ)
                else:
                    with pytest.warns(np.ComplexWarning):
                        w_est = w_src.astype(dtype_targ)
                np.testing.assert_allclose(w_est, w_targ, atol=atol, rtol=0)
                assert w_est.dtype == w_targ.dtype

    def test_astype_complex_int(self):
        for dtype_src, w_src in self.w_complex_ref.items():
            for dtype_targ, w_targ in self.w_int_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))
                atol = (CPX_EPS[dtype_src] *
                        (INT_MAX[dtype_targ] - INT_MIN[dtype_targ] + 1) / 2)

                w_est = w_src.astype(dtype_targ)
                np.testing.assert_allclose(w_est, w_targ, atol=atol, rtol=0)
                assert w_est.dtype == w_targ.dtype

    def test_astype_int_complex(self):
        for dtype_src, w_src in self.w_int_ref.items():
            for dtype_targ, w_targ in self.w_complex_ref.items():
                print('Casting from {} to {}.'.format(dtype_src, dtype_targ))
                atol = ((INT_MAX[dtype_src] - INT_MIN[dtype_src] + 1) +
                        CPX_EPS[dtype_targ] / 2)

                w_est = w_src.astype(dtype_targ)

                np.testing.assert_allclose(w_est, w_targ, atol=atol, rtol=0)
                assert w_est.dtype == w_targ.dtype

    def test_astype_invalid(self):
        match = "Unsupported target type <class 'list'>."
        with pytest.raises(TypeError, match=match):
            self.w_float_ref[np.float64].astype(list)

        with pytest.raises(TypeError, match=match):
            self.w_int_ref[np.int32].astype(list)

    def test_to_wavfile_mono(self):

        match = 'Complex values have been stored by keeping only the real '\
                'part, the imaginary part has been discarded.'

        for fs in FS:
            for dtype in (INT_DTYPES + FLT_DTYPES + CPX_DTYPES):
                print('Fs: {:d}, dtype: {}]'.format(fs, dtype))

                w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)

                with warnings.catch_warnings(record=True):
                    w = w.astype(dtype)

                with tempfile.NamedTemporaryFile(suffix='.wav') as tmp_file:

                    if dtype in CPX_DTYPES:
                        with pytest.warns(UserWarning, match=match):
                            w.to_wavfile(tmp_file.name)
                    else:
                        w.to_wavfile(tmp_file.name)

                    with warnings.catch_warnings(record=True):
                        w2 = Waveform.from_wavfile(tmp_file.name).astype(dtype)
                    np.testing.assert_almost_equal(w2.to_np_array(0),
                                                   w.to_np_array(0),
                                                   decimal=3)
                    assert w.fs == w2.fs

        for dtype in (INT_DTYPES + FLT_DTYPES + CPX_DTYPES):
            for dtype_targ in FLT_DTYPES:
                print('dtype: {}, dtype_targ: {}]'.format(dtype, dtype_targ))

                w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)

                with warnings.catch_warnings(record=True):
                    w = w.astype(dtype)

                with tempfile.NamedTemporaryFile(suffix='.wav') as tmp_file:

                    if dtype in CPX_DTYPES:
                        with pytest.warns(UserWarning, match=match):
                            w.to_wavfile(tmp_file.name, dtype=dtype_targ)
                    else:
                        with warnings.catch_warnings(record=True):
                            w.to_wavfile(tmp_file.name)

                    with warnings.catch_warnings(record=True):
                        w2 = Waveform.from_wavfile(
                            tmp_file.name).astype(dtype)
                    np.testing.assert_almost_equal(w2.to_np_array(),
                                                   w.to_np_array(0),
                                                   decimal=3)

    def test_to_wavfile_stereo(self):

        match = 'Complex values have been stored by keeping only the real '\
            'part, the imaginary part has been discarded.'
        for fs in FS:
            for dtype in (INT_DTYPES + FLT_DTYPES + CPX_DTYPES):
                print('Fs: {:d}, dtype: {}]'.format(fs, dtype))

                w = Waveform(self.x_stereo, mask=self.m_stereo, fs=self.fs)
                with warnings.catch_warnings(record=True):
                    w = w.astype(dtype)

                with tempfile.NamedTemporaryFile(suffix='.wav') as tmp_file:

                    if dtype in CPX_DTYPES:
                        with pytest.warns(UserWarning, match=match):
                            w.to_wavfile(tmp_file.name)
                    else:
                        with warnings.catch_warnings(record=True):
                            w.to_wavfile(tmp_file.name)

                    with warnings.catch_warnings(record=True):
                        w2 = Waveform.from_wavfile(tmp_file.name).astype(dtype)
                    np.testing.assert_almost_equal(w2.to_np_array(),
                                                   w.to_np_array(0),
                                                   decimal=3)
                    assert w.fs == w2.fs

        for dtype in (INT_DTYPES + FLT_DTYPES + CPX_DTYPES):
            for dtype_targ in FLT_DTYPES:
                print('dtype: {}, dtype_targ: {}]'.format(dtype, dtype_targ))

                w = Waveform(self.x_mono, fs=self.fs, mask=self.m_mono)

                with warnings.catch_warnings(record=True):
                    w = w.astype(dtype)

                with tempfile.NamedTemporaryFile(suffix='.wav') as tmp_file:

                    if dtype in CPX_DTYPES:
                        with pytest.warns(UserWarning, match=match):
                            w.to_wavfile(tmp_file.name, dtype=dtype_targ)
                    else:
                        with warnings.catch_warnings(record=True):
                            w.to_wavfile(tmp_file.name)

                    with warnings.catch_warnings(record=True):
                        w2 = Waveform.from_wavfile(tmp_file.name).astype(dtype)
                    np.testing.assert_almost_equal(w2.to_np_array(),
                                                   w.to_np_array(0),
                                                   decimal=3)

    def test_to_wavfile_raises(self):
        # Unsupported/Not implemented types
        for dtype in (np.int64,):
            w = Waveform(self.x_mono.astype(dtype), fs=self.fs)
            with pytest.raises(NotImplementedError):
                w.to_wavfile('')

        # Infinite values
        w = Waveform(self.x_mono, fs=self.fs)
        for infinite_value in (np.inf, -np.inf):
            w[w.size // 2] = infinite_value
            with pytest.raises(ValueError, match='Data should be finite.'):
                w.to_wavfile('')

        # Unsupported fs
        w = Waveform(self.x_mono, fs=1234)

        match = '`fs` is not a valid sampling frequency \(given: 1234\).'
        with pytest.raises(ValueError, match=match):
            w.to_wavfile('')

    def test_from_wavfile_mono(self):

        x_len = np.random.randint(100, 1000)
        fs = np.random.choice(FS)
        x = np.random.rand(x_len)

        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp_file:
            wavfile.write(filename=str(tmp_file.name), data=x,
                          rate=fs)

            # Given dtype
            w_l = Waveform.from_wavfile(tmp_file.name, dtype=np.float64)
            np.testing.assert_almost_equal(w_l.data, x, decimal=4)
            assert w_l.fs == fs

            # dtype is None
            w_m = Waveform.from_wavfile(tmp_file.name, dtype=None)
            np.testing.assert_almost_equal(w_m.data, x, decimal=4)
            assert w_l.fs == fs

            # dtype is int16
            w_m.to_wavfile(str(tmp_file.name), dtype=np.int16)
            w_m_i = Waveform.from_wavfile(tmp_file.name, dtype=None)
            assert w_m_i.dtype == np.int16

    def test_from_wavfile_stereo(self):

        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp_file:

            length_stereo = np.random.randint(100, 1000)
            fs_stereo = np.random.choice(FS)
            x_stereo = np.random.rand(length_stereo, 2)
            wavfile.write(filename=str(tmp_file.name), data=x_stereo,
                          rate=fs_stereo)

            # Conversion to mono is left
            w_l = Waveform.from_wavfile(tmp_file.name, dtype=np.float64,
                                        conversion_to_mono='left')
            np.testing.assert_almost_equal(x_stereo[:, 0], w_l.to_np_array(),
                                           decimal=4)
            assert w_l.fs == fs_stereo

            # Conversion to mono is right
            w_r = Waveform.from_wavfile(tmp_file.name,
                                        conversion_to_mono='right')

            np.testing.assert_almost_equal(x_stereo[:, 1],
                                           w_r.to_np_array(), decimal=4)
            assert w_l.fs == fs_stereo

            # Conversion to mono is mean
            w_m = Waveform.from_wavfile(tmp_file.name,
                                        conversion_to_mono='mean')

            np.testing.assert_almost_equal(np.mean(x_stereo, axis=1),
                                           w_m.to_np_array(), decimal=4)
            assert w_l.fs == fs_stereo

            # Stereo
            w_stereo = Waveform.from_wavfile(tmp_file.name)
            np.testing.assert_almost_equal(w_stereo.to_np_array(),
                                           x_stereo, decimal=4)
            assert w_stereo.fs == fs_stereo
            assert w_stereo.is_stereo()

            match = '`conversion_to_mono` in invalid \(given: center\).'
            with pytest.raises(ValueError, match=match):
                Waveform.from_wavfile(
                    tmp_file.name, conversion_to_mono='center')

    def test_plot_real(self):

        for x, m in zip([self.x_mono, self.x_stereo],
                        [self.m_mono, self.m_stereo]):
            w = Waveform(x, mask=m, fs=self.fs)

            lines = w.plot(fill_value=None)
            assert type(lines[0]) == plt.matplotlib.lines.Line2D
            lines = w.plot(None, None)
            assert type(lines[0]) == plt.matplotlib.lines.Line2D
            w.plot_mask()

    def test_plot_complex(self):
        w = Waveform(self.x_mono + 1j * self.x_mono,
                     mask=self.m_mono, fs=self.fs)

        lines = w.plot()
        assert type(lines[0]) == plt.matplotlib.lines.Line2D
        lines = w.plot(cpx_mode='imag')
        assert type(lines[0]) == plt.matplotlib.lines.Line2D
        lines = w.plot(cpx_mode='both')
        assert type(lines[0]) == plt.matplotlib.lines.Line2D
        assert type(lines[1]) == plt.matplotlib.lines.Line2D

        # Unknows complex mode
        with pytest.raises(
                ValueError,
                match='Unknown complex mode \(given: realandimag\).'):
            w.plot(cpx_mode='realandimag')

    def test_copy(self):

        w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)

        w_copy = w.copy()
        assert w.is_equal(w_copy)
        assert id(w) != id(w_copy)
        assert id(w._mask) != id(w_copy._mask)

    def test_str_repr(self):

        w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)

        x = np.copy(self.x_mono)
        x[self.m_mono] = np.nan
        arr_str = np.ndarray.__str__(x)
        arr_str = arr_str.replace('nan', '  x')
        n_miss = np.count_nonzero(self.m_mono)

        exp_str = 'Waveform, fs={}Hz, length={}, dtype={}, {} missing '\
                  'entries (50.0%)\n{}'.format(self.fs, self.length, x.dtype,
                                               n_miss, arr_str)
        assert str(w) == exp_str

        exp_str = '<Waveform at {}>'
        assert repr(w) == exp_str.format(hex(id(w)))

    def test_show_player(self, capsys):

        w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)
        player = w.show_player()

        assert isinstance(player, Audio)

        w = Waveform(self.x_mono, mask=self.m_mono,
                     fs=self.fs).astype(np.complex128)

        with pytest.warns(UserWarning, match='Only the real part is played.'):
            player = w.show_player()
        assert isinstance(player, Audio)

        # Wrong frequency sampling
        w = Waveform(self.x_mono, mask=self.m_mono, fs=1)
        with pytest.raises(ValueError,
                           match='Invalid sampling frequency: \d+Hz'):
            w.show_player()

        with mock.patch.dict('sys.modules', {'IPython.display': None}):
            w.show_player()
        captured = capsys.readouterr()
        exp_print = 'This method should only be called in notebooks.\n'
        assert captured[0] == exp_print

    def test_play_stop_isplaying_mono(self):

        try:
            import simpleaudio
            simpleaudio.play_buffer(np.zeros(1000), 1, 2, 44100)
            is_patched = False
        except sa._simpleaudio.SimpleaudioError:
            is_patched = True
            patcher1 = mock.patch('simpleaudio.PlayObject', )
            patcher2 = mock.patch('simpleaudio.play_buffer')
            patcher1.start()
            patcher2.start()

        for fs in FS:
            for dtype in (INT_DTYPES + FLT_DTYPES + CPX_DTYPES):
                print('Play {} data sample at {} Hz.'.format(dtype, fs))

                if np.issubdtype(dtype, np.integer):
                    w = Waveform(np.full(1000, fill_value=INT_ZERO[dtype],
                                         dtype=dtype), fs=fs)
                else:
                    w = Waveform(np.zeros(1000, dtype=dtype), fs=fs)

                assert not w.is_playing()
                w.stop()

                if np.issubdtype(dtype, np.complexfloating):
                    with pytest.warns(UserWarning,
                                      match='Only the real part is played.'):
                        w.play()
                else:
                    w.play()
                assert w.is_playing()
                w.stop()
                assert w.is_playing()

                if np.issubdtype(dtype, np.complexfloating):
                    with pytest.warns(UserWarning,
                                      match='Only the real part is played.'):
                        w.play(scale=True)
                else:
                    w.play(scale=True)

                w.stop()
                if not is_patched:
                    assert isinstance(w._play_object, sa.shiny.PlayObject)

        w = Waveform(np.zeros(1000), fs=1)

        with pytest.raises(ValueError,
                           match='Invalid sampling frequency: 1Hz'):
            w.play()

        if is_patched:
            patcher1.stop()
            patcher2.stop()

    def test_play_stop_isplaying_stereo(self):

        for fs in FS:
            for dtype in (INT_DTYPES + FLT_DTYPES + CPX_DTYPES):
                print('Play {} data sample at {} Hz.'.format(dtype, fs))

                if np.issubdtype(dtype, np.integer):
                    w = Waveform(np.full((1000, 2), fill_value=INT_ZERO[dtype],
                                         dtype=dtype), fs=fs)
                else:
                    w = Waveform(np.zeros((1000, 2), dtype=dtype), fs=fs)

                    assert not w.is_playing()
                    w.stop()

                if np.issubdtype(dtype, np.complexfloating):
                    with pytest.warns(UserWarning,
                                      match='Only the real part is played.'):
                        try:
                            w.play()
                        except sa._simpleaudio.SimpleaudioError:
                            pass
                else:
                    try:
                        w.play()
                        assert w.is_playing()
                        w.stop()
                        assert w.is_playing()
                    except sa._simpleaudio.SimpleaudioError:
                        pass

                if np.issubdtype(dtype, np.complexfloating):
                    with pytest.warns(UserWarning,
                                      match='Only the real part is played.'):
                        try:
                            w.play(scale=True)
                        except sa._simpleaudio.SimpleaudioError:
                            pass
                else:
                    try:
                        w.play(scale=True)
                        w.stop()

                        assert isinstance(w._play_object, sa.shiny.PlayObject)

                    except sa._simpleaudio.SimpleaudioError:
                        pass

        w = Waveform(np.zeros(1000), fs=1)

        with pytest.raises(ValueError,
                           match='Invalid sampling frequency: 1Hz'):
            try:
                w.play()
            except sa._simpleaudio.SimpleaudioError:
                pass

    def test_get_analytic_signal(self):

        for x, m in zip([self.x_mono, self.x_stereo],
                        [self.m_mono, self.m_stereo]):
            with pytest.raises(TypeError,
                               match='Waveform has missing samples'):
                Waveform(x, mask=m, fs=self.fs).get_analytic_signal()

            w = Waveform(x, fs=self.fs)
            np.testing.assert_array_almost_equal(
                np.real(w.get_analytic_signal()), x)

    def test_eq_ne_numpy(self):

        for x, m in zip([self.x_mono, self.x_stereo],
                        [self.m_mono, self.m_stereo]):
            w = Waveform(x, fs=self.fs)
            cmp_w = w == x
            assert type(cmp_w) == np.ndarray
            assert cmp_w.dtype == np.bool
            assert np.all(cmp_w)

        w = Waveform(np.ones(self.length), fs=self.fs)
        cmp_w = w == 0
        assert type(cmp_w) == np.ndarray
        assert cmp_w.dtype == np.bool
        assert np.all(~cmp_w)

    def test_basic_operations(self):

        x = self.x_mono

        w1 = Waveform(x, fs=self.fs)
        w2 = Waveform(x, fs=self.fs)
        w3 = Waveform(x, fs=1 if self.fs > 1 else 44100)
        ma = MadArray(x)

        for operator in ['+', '-', '*', '/', '//']:
            print('Operation: {}'.format(operator))

            xs = eval('x {} x'.format(operator))
            ws = eval('w1 {} w2'.format(operator))
            assert isinstance(ws, Waveform)
            np.testing.assert_equal(ws, xs)

            match = 'Waveforms do not have the same fs: \d+ and \d+'
            with pytest.raises(ValueError, match=match):
                eval('w1 {} w3'.format(operator))

            ms = eval('w1 {} ma'.format(operator))
            assert isinstance(ws, Waveform)
            np.testing.assert_equal(ws, xs)

    def test_advanced_operations(self):

        x = self.x_mono

        ma = MadArray(x, self.m_mono)

        m = np.mean(ma)
        assert not isinstance(m, MadArray)
        np.testing.assert_equal(m, np.mean(x))

        m = np.mean(ma, axis=0)
        assert not isinstance(m, MadArray)
        np.testing.assert_equal(m, np.mean(x, axis=0))

        m = np.std(ma)
        assert not isinstance(m, MadArray)
        np.testing.assert_equal(m, np.std(x))

    def test_eq(self):

        x = self.x_mono

        w1 = Waveform(x, fs=self.fs)
        w2 = Waveform(x, fs=self.fs)
        w3 = Waveform(x, fs=1 if self.fs > 1 else 44100)

        assert np.all(w1 == w2)

        match = 'Waveforms do not have the same fs: \d+ and \d+'
        with pytest.raises(ValueError, match=match):
            w1 == w3

        assert w2.is_equal(w2)
        assert not w1.is_equal(w3)

    def test_fade(self):
        all_modes = {'both', 'in', 'out'}
        for fade_len in {self.length // 10, self.length}:
            fade_dur = fade_len / self.fs
            w = dict()
            for mode in all_modes:
                print('fade_length={}, mode={}, fs={}'.format(
                    fade_len, mode, self.fs))

                w[mode] = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)
                w[mode].fade(mode=mode, fade_length=fade_len)
                w_with_dur = Waveform(
                    self.x_mono, mask=self.m_mono, fs=self.fs)
                w_with_dur.fade(mode=mode, fade_duration=fade_dur)

                np.testing.assert_array_equal(w[mode], w_with_dur)

            np.testing.assert_array_equal(
                np.array(w['both'][fade_len:-fade_len]),
                self.x_mono[fade_len:-fade_len],
                err_msg='Some samples have been modified in the center part.')

            np.testing.assert_array_equal(
                np.array(w['in'][fade_len:]),
                self.x_mono[fade_len:],
                err_msg='Samples modified after the fade-in area.')

            np.testing.assert_array_equal(
                np.array(w['out'][:-fade_len]),
                self.x_mono[:-fade_len],
                err_msg='Samples modified before the fade-out area.')

            for mode in {'both', 'in'}:
                print('fade_len={}, mode={}'.format(fade_len, mode))
                assert_array_less_or_equal(
                    np.array(w[mode][:fade_len]),
                    self.x_mono[:fade_len],
                    err_msg='Samples in the fade-in area greater.')

            for mode in {'both', 'out'}:
                print('fade_len={}, mode={}'.format(fade_len, mode))
                assert_array_less_or_equal(
                    np.array(w[mode][fade_len:]),
                    self.x_mono[fade_len:],
                    err_msg='Samples in the fade-out area  greater')

        w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)
        w.fade(mode='both', fade_length=0)
        np.testing.assert_array_equal(np.array(w), self.x_mono)

    def test_fade_exceptions(self):
        all_modes = {'both', 'in', 'out'}
        fade_len = self.length // 5
        fade_dur = fade_len / self.fs
        w = dict()
        for mode in all_modes:
            w[mode] = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)
            match = 'Either `fade_duration` or `fade_length` must be given.'
            with pytest.raises(ValueError, match=match):
                w[mode].fade(mode=mode)

            match = '`fade_duration` and `fade_length` cannot be given '\
                'simultaneously.'
            with pytest.raises(ValueError, match=match):
                w[mode].fade(mode=mode,
                             fade_length=fade_len,
                             fade_duration=fade_dur)

            match = 'Fade length \(\d+\) is greater than data length \(\d+\)'
            with pytest.raises(ValueError, match=match):
                w[mode].fade(mode=mode, fade_length=self.length + 1)

            with pytest.raises(ValueError,
                               match='Fade length cannot be negative.'):
                w[mode].fade(mode=mode, fade_length=-1)

            with pytest.raises(ValueError,
                               match='Fade length cannot be negative.'):
                w[mode].fade(mode=mode, fade_duration=-1 / self.fs)

        with pytest.raises(ValueError, match='Mode is unknown: stereo.'):
            w[mode].fade(mode='stereo', fade_length=fade_len)

    def test_pickle(self):

        w = Waveform(self.x_mono, mask=self.m_mono, fs=self.fs)

        with tempfile.NamedTemporaryFile() as tmp_file:
            with open(tmp_file.name, 'wb') as fout:
                pickle.dump(w, fout)

            with open(tmp_file.name, 'rb') as fin:
                pw = pickle.load(fin)

            assert w.is_equal(pw)
