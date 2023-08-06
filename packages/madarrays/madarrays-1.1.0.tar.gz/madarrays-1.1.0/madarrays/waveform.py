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
"""Definition of a masked waveform.

.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Florent Jaillet
"""
import warnings

from fractions import Fraction
import numpy as np
import resampy
import simpleaudio as sa

from scipy.io import wavfile
from scipy.signal import hilbert
import matplotlib.pyplot as plt

from .mad_array import MadArray


VALID_IO_FS = {1, 8000, 16000, 32000, 48000, 11025, 22050, 44100, 88200}


def _check_compatibility_fs(w1, w2):
    """Raise an exception if the sampling frequency of the two Waveforms
    are different."""
    if w1.fs != w2.fs:
        errmsg = 'Waveforms do not have the same fs: {} and {}.'
        raise ValueError(errmsg.format(w1.fs, w2.fs))


class Waveform(MadArray):
    """Subclass of MadArray to handle mono and stereo audio signals.

    :class:`Waveform` inherits from :class:`~madarrays.mad_array.MadArray` and
    adds an attribute :attr:`fs` to store the sampling frequency, as well as
    methods to facilitate the manipulation of audio files.

    .. _type_entry_waveform:

    **Type of entries**: audio data entries can have different types, that are
    associated with specific constraints on the values:

    * *float*: the values are float between -1 and 1;
    * *int*: the values are integers between a range that depends on the
      precision.
    * *complex*: the real and imaginary parts are float between -1 and 1.

    High-precision types (float128, int64, complex256) may lead to problems and
    should be used with caution.

    The casting of a waveform in a different dtype depends on the current dtype
    and the desired dtype (complex casting is similar to float casting):

    * *Integer-to-real* casting is performed by applying on each entry
      :math:`x` the function :math:`f(x)=\\frac{x - z}{2^{n-1}}`, where the
      source integral type is coded with :math:`n` bits, and :math:`z` is the
      integer associated with zero, i.e., :math:`z=0` for a signed type (`int`)
      and :math:`z=2^{n-1}` for an unsigned type (`uint`).
    * *Real-to-integer* casting is performed by applying on each entry
      :math:`x` the function :math:`f(x)=\\lfloor\\left(x + 1\\right) 2^{n-1} +
      m\\rfloor`, where the target integral type is coded with :math:`n` bits,
      and :math:`m` is the minimum integer value, i.e., :math:`m=-2^{n-1}` for
      a signed type (`int`) and :math:`z=0` for an unsigned type (`uint`);
    * *Real-to-real* casting is obtained by a basic rounding operation;
    * *Integer-to-integer* casting is obtained by chaining an
      integer-to-float64 casting and a float64-to-integer casting.

    Clipping is performed for unexpected values:

    * When casting to `float`, values outside :math:`[-1, 1]` are clipped;
    * When casting to `int`, values outside the minimum and maximum values
      allowed by the integral type are clipped:

        * :math:`\\left[-2^{n-1}, 2^{n-1}-1\\right]` for :math:`n`-bits signed
          integers;
        * :math:`\\left[0, 2^{n}-1\\right]` for :math:`n`-bits unsigned
          integers.

    These constraints are only applied when calling explicitely the method
    :meth:`astype`.

    ..  _masking:

    **Masking**: Waveform allows for complex entries, but only real-like
    masking is permitted, i.e. it is not possible to mask only the phase or the
    amplitude. In particular, this implies that the attribute
    :attr:`_is_complex` inherited from :class:`~madarrays.mad_array.MadArray`
    is always equal to False.

    Parameters
    ----------
    data : nd-array [N] or [N, 2]
        Audio samples, as a N-length vector for a mono signal or a
        [N, 2]-shape array for a stereo signal
    fs : int or float, optional
        Sampling frequency of the original signal, in Hz. If float, truncated.
        If None and ``data`` is a Waveform, use ``data.fs``, otherwise it
        is set to 1.
    mask : nd-array, optional
        Boolean mask with True values for missing samples. Its shape must be
        the same as ``data``.
    indexing :
        See :class:`~madarrays.mad_array.MadArray`.
    """

    def __new__(cls, data, fs=None, mask=None, masked_indexing=None):
        if fs is None:
            if isinstance(data, Waveform):
                fs = data.fs
            else:
                fs = 1

        # create the MadArray
        data = data.squeeze()
        if isinstance(data, MadArray) and data._complex_masking \
                and mask is None :
            warnmsg = ('Construction of a Waveform from a MadArray with '
                       'complex masking: the original masking data are '
                       'discarded and a boolean mask set to False is used.')
            warnings.warn(warnmsg)
            # Create mask to force boolean masking
            mask = np.zeros_like(data, dtype=np.bool)

        obj = MadArray.__new__(cls=cls, data=data, mask=mask,
                               masked_indexing=masked_indexing)

        if obj.ndim > 2 or obj.ndim == 2 and obj.shape[1] > 2:
            raise ValueError('`data` should be either mono or stereo.')

        # add the new attribute to the created instance
        obj.fs = fs

        return obj

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):

        if len(inputs) == 2:
            if (isinstance(inputs[0], Waveform) and
                    isinstance(inputs[1], Waveform)):
                _check_compatibility_fs(*inputs)

        output = super().__array_ufunc__(ufunc, method, *inputs, **kwargs)

        if isinstance(output, MadArray):
            output = output.view(Waveform)
            output.fs = inputs[0].fs if isinstance(inputs[0], Waveform) \
                else inputs[1].fs

        return output

    def __array_finalize__(self, obj):
        super().__array_finalize__(obj)
        self._fs = getattr(obj, '_fs', 1)
        self._play_object = getattr(obj, '_play_object', None)

    def __reduce__(self):
        pickled_state = super().__reduce__()
        new_state = pickled_state[2] + (self._fs, )
        return pickled_state[0], pickled_state[1], new_state

    def __setstate__(self, state):
        self._play_object = None
        self._fs = state[-1]
        super().__setstate__(state[0:-1])

    @property
    def fs(self):
        """Frequency sampling of the audio signal (int or float).

        The signal is not resampled when the sampling frequency is modified.

        Raises
        ------
        ValueError
            If `fs` is not positive.
        """
        return self._fs

    @fs.setter
    def fs(self, fs):
        if fs <= 0:
            errmsg = 'fs is not strictly positive (given: {})'
            raise ValueError(errmsg.format(fs))
        self._fs = fs

    @property
    def rms(self):
        """Root mean square error of the masked signal (float).

        Raises
        ------
        NotImplementedError
            If data is with an integer type.
        """
        if np.issubdtype(self.dtype, np.integer):
            errmsg = 'RMS is not available for integer data types'
            raise NotImplementedError(errmsg)

        return np.sqrt(np.mean(np.abs(self.to_np_array(0))**2))

    @property
    def length(self):
        """Length of the signal, in samples."""
        return self.shape[0]

    @property
    def duration(self):
        """Duration of the signal, in seconds."""
        return self.length / self.fs

    @property
    def n_channels(self):
        """Number of channels (1 for mono, 2 for stereo)."""
        return 1 if self.ndim == 1 else self.shape[1]

    @property
    def time_axis(self):
        """Time axis."""
        return np.arange(self.length) / self.fs

    def is_stereo(self):
        """Indicates whether the signal is stereo or not."""
        return self.n_channels == 2

    def set_rms(self, rms):
        """Set root mean square error of the signal.

        Parameters
        ----------
        rms : float
            Root mean square of the signal.

        Raises
        ------
        ValueError
            If `rms` is negative.
        NotImplementedError
            If data is with an integer type.
        """
        if rms < 0:
            errmsg = '`rms` should be a positive float (given: {})'
            raise ValueError(errmsg.format(rms))

        self[:] /= self.rms
        self[:] *= rms

    def resample(self, fs):
        """Resample the audio signal, in place.

        Can be only performed on a waveform without missing data.

        Note that if the current or the new sampling frequencies are not
        integers, the new sampling frequency may be different from the
        desired value since the resampling method only allows input and
        output frequencies of type ``int``. In this case, a warning is
        raised.

        Parameters
        ----------
        fs : int or float
            New sampling frequency.

        Raises
        ------
        ValueError
            If `fs` is not a positive number.
            If `self` has missing samples.
        UserWarning

        """
        assert np.issubdtype(type(fs), np.integer) \
               or np.issubdtype(type(fs), np.floating)

        if fs <= 0:
            errmsg = '`fs` should be a positive number (given: {})'
            raise ValueError(errmsg.format(fs))

        if np.issubdtype(type(fs), np.floating) \
                or np.issubdtype(type(self.fs), np.floating):
            # Find a good rational number to approximate the ratio between
            # sampling frequencies
            fs_ratio = Fraction(fs/self.fs)
            fs_ratio = fs_ratio.limit_denominator(10000)
            # Sampling frequencies used for the resampling (need to be int)
            resample_new_fs = fs_ratio.numerator
            resample_old_fs = fs_ratio.denominator
            # Adjust new sampling frequency
            new_fs = fs_ratio * self.fs
            if new_fs != fs:
                warnings.warn('New sampling frequency adjusted to {} instead '
                              'of {} in order to use ``int`` values in '
                              '``resample``.'.format(fs_ratio * self.fs, fs))
            fs = new_fs
        else:
            resample_new_fs = fs
            resample_old_fs = self.fs

        if self.is_masked():
            errmsg = 'Waveform has missing entries.'
            raise ValueError(errmsg)

        if resample_new_fs != resample_old_fs:
            x = self.to_np_array()

            y = resampy.resample(x, resample_old_fs, resample_new_fs, axis=0)

            self.resize(y.shape, refcheck=False)
            self[:] = y
            self._fs = fs
            self._mask = np.zeros_like(self, dtype=np.bool)

    def plot(self, x_axis_label='Time (s)', y_axis_label='',
             cpx_mode='real', fill_value=0, **kwargs):
        """Plot the signal.

        Parameters
        ----------
        x_axis_label : str
            Label of the x axis.
        y_axis_label : str
            Label of the y axis.
        cpx_mode : {'real', 'imag', 'both'}
            In case of a complex-valued signal, plot the real part only
            ('real'), the imaginary part only ('imag'), or both curves
            ('both'). This option has no effect if the signal is real-valued.
        fill_value : scalar or None
            Value used to fill missing data for display. If None, the existing
            value is used (e.g., for clipping).

        Other Parameters
        ----------------
        kwargs
            See :func:`matplotlib.pyplot.plot`.

        Returns
        -------
        List of Line
            See :func:`matplotlib.pyplot.plot`.
        """
        x = self.to_np_array(fill_value)

        if np.issubdtype(x.dtype, np.complexfloating):
            if cpx_mode == 'real':
                lines = plt.plot(self.time_axis, np.real(x), **kwargs)
            elif cpx_mode == 'imag':
                lines = plt.plot(self.time_axis, np.imag(x), **kwargs)
            elif cpx_mode == 'both':
                lines_real = plt.plot(self.time_axis, np.real(x), **kwargs)
                lines_complex = plt.plot(
                    self.time_axis, np.imag(x), **kwargs)
                lines = lines_real + lines_complex
            else:
                errmsg = 'Unknown complex mode (given: {}).'
                raise ValueError(errmsg.format(cpx_mode))
        else:
            lines = plt.plot(self.time_axis, x, **kwargs)

        # add label_dict
        if x_axis_label is not None:
            plt.xlabel(x_axis_label)
        if y_axis_label is not None:
            plt.ylabel(y_axis_label)

        return lines

    def plot_mask(self,
                  x_axis_label='Time (s)',
                  y_axis_label='',
                  **kwargs):
        """Plot the mask.

        Parameters
        ----------
        x_axis_label : str
            Label of the time axis (horizontal axis).
        y_axis_label : str
            Label of the frequency axis (vertical axis).
        """
        plt.step(
            self.time_axis, self._mask, linewidth=2, where='pre', **kwargs)
        plt.ylim(-0.25, 1.25)
        plt.yticks([0, 1])

        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.grid()

    def to_wavfile(self, filename, dtype=None):
        """Save the wavefile as an audio wav file.

        Parameters
        ----------
        filename : str or :class:`pathlib.Path`
            Name of the file including paths and extension
        dtype : data-type or None, optional
            Type of the entries of the wav file. If None, use current dtype of
            data.

        Raises
        ------
        UserWarning
            If the signal is complex.
        ValueError
            If the sampling frequency is not an integer from the set of
            supported frequencies ``madarrays.waveform.VALID_IO_FS``).
        NotImplementedError
            If dtype is not supported by the current implementation.

        See also
        --------
        scipy.io.wavfile.write
        """
        if self.fs not in VALID_IO_FS:
            errmsg = '`fs` is not a valid sampling frequency (given: {}).'
            raise ValueError(errmsg.format(self.fs))

        if dtype is None:
            dtype = self.dtype

        y = self.to_np_array(0)

        if np.iscomplexobj(y):
            warnmsg = 'Complex values have been stored by keeping only the '\
                'real part, the imaginary part has been discarded.'
            warnings.warn(warnmsg)

            y = np.real(y)

            if np.issubdtype(dtype, np.complexfloating):
                dtype = np.float32

        if dtype == np.float64:
            dtype = np.float32
        elif dtype == np.int64:
            raise NotImplementedError

        # catch clipping error
        y = y.astype(dtype=dtype)

        if not np.all(np.isfinite(y)):
            errmsg = 'Data should be finite.'
            raise ValueError(errmsg)

        wavfile.write(str(filename), data=y, rate=self.fs)

    @staticmethod
    def from_wavfile(filename, dtype=np.float64, conversion_to_mono=None):
        """Load an audio file and return an Waveform object.

        Parameters
        ----------
        filename : str or :class:`pathlib.Path`
            Name of the audio file
        dtype : data-type, optional
            Output data type. If None, the data type from the wavfile is kept.
            See :ref:`Type of Entry<type_entry_waveform>`.
        conversion_to_mono : {'left', 'right', 'mean'} or None, optional
            If None (default), no conversion is performed. If str, select the
            appropriate channel (left or right), or the mean between the left
            and right channels if stereo.

        Returns
        -------
        :class:`Waveform`
        """
        fs, x = wavfile.read(str(filename))

        if dtype is None:
            dtype = x.dtype

        if x.ndim > 1:
            if conversion_to_mono is not None:

                if conversion_to_mono == 'left':
                    x = x[:, 0]

                elif conversion_to_mono == 'right':
                    x = x[:, 1]

                elif conversion_to_mono == 'mean':
                    x = np.mean(x, axis=1)

                else:
                    errmsg = '`conversion_to_mono` in invalid (given: {}).'
                    raise ValueError(errmsg.format(conversion_to_mono))

        return Waveform(x, fs=fs).astype(dtype=dtype)

    def fade(self, mode='both', fade_duration=None, fade_length=None):
        """Apply fade-in and/or fade-out.

        Half a hanning window with the specified length or duration is used
        (exactly one parameter `fade_duration` or `fade_length` must be set).

        Parameters
        ----------
        mode : {'both', 'in', 'out'}, optional
            Signal to be processed.
        fade_duration : float, optional
            Duration, in seconds, of the fade effect.
        fade_length : int, optional
            Length, in samples, of the fade effect.

        Raises
        ------
        ValueError
            If neither `fade_duration` nor `fade_length` is given.
            If both `fade_duration` and `fade_length` are given.
            If `fade_duration` or `fade_length` are greater than the
            duration or length of the waveform.
            If `fade_duration` or `fade_length` are negative.
            If `mode` is invalid.
        """
        if fade_duration is None and fade_length is None:
            errmsg = 'Either `fade_duration` or `fade_length` must be given.'
            raise ValueError(errmsg)

        if fade_duration is not None and fade_length is not None:
            errmsg = '`fade_duration` and `fade_length` cannot be given '\
                'simultaneously.'
            raise ValueError(errmsg)

        if mode not in ['both', 'in', 'out']:
            errmsg = 'Mode is unknown: {}.'
            raise ValueError(errmsg.format(mode))

        if fade_length is None:
            fade_length = int(np.round(fade_duration * self.fs))

        if fade_length == 0:
            return

        if fade_length < 0:
            errmsg = 'Fade length cannot be negative.'
            raise ValueError(errmsg)

        if fade_length > self.shape[0]:
            errmsg = 'Fade length ({}) is greater than data length ({})'
            raise ValueError(errmsg.format(fade_length, self.shape[0]))

        w = np.sin(np.pi / 2 / fade_length * np.arange(fade_length))**2

        if mode in ['both', 'in']:
            self[:len(w)] *= w

        if mode in ['both', 'out']:
            self[-len(w):] *= w[-1::-1]

    def show_player(self):
        """
        Show the player when using jupyter notebook.

        Raises
        ------
        ValueError
            If sampling frequency is 1.
        """
        try:
            from IPython.display import Audio
            if self.fs == 1:
                errmsg = 'Invalid sampling frequency: {}Hz'
                raise ValueError(errmsg.format(self.fs))

            if np.iscomplexobj(self):
                warnmsg = 'Only the real part is played.'
                warnings.warn(warnmsg)

            x = np.real(self).to_np_array(0)
            return Audio(data=x, rate=self.fs)
        except ImportError:
            print('This method should only be called in notebooks.')

    def play(self, scale=False):
        """Play the audio file.

        Parameters
        ----------
        scale : bool
            If True, the data is normalized by maximum value.

        Returns
        -------
        `simpleaudio.PlayObject`
            Object useful to handle the played audio stream.

        Raises
        ------
        ValueError
            If sampling frequency is 1.
        """

        if self.fs == 1:
            errmsg = 'Invalid sampling frequency: {}Hz'
            raise ValueError(errmsg.format(self.fs))

        if np.iscomplexobj(self):
            warnmsg = 'Only the real part is played.'
            warnings.warn(warnmsg)

        x = np.real(self)

        if scale:
            x = x.astype(np.float64)
            maxima = np.max(np.abs(self))
            if maxima > 0:
                x[:] = x / maxima * (1 - np.finfo(np.float64).eps)

        x = x.astype(dtype=np.int16).to_np_array(0)
        self._play_object = sa.play_buffer(x, num_channels=self.n_channels,
                                           bytes_per_sample=2,
                                           sample_rate=self.fs)

    def stop(self):
        """Stop playing (does nothing if the sound is not played) """
        if self.is_playing():
            self._play_object.stop()

    def is_playing(self):
        """Indicates whether the sound is currently being played.

        Returns
        -------
        bool
            True if the sound is currently being played, False otherwise.
        """
        return (hasattr(self._play_object, 'is_playing') and
                self._play_object.is_playing())

    def get_analytic_signal(self, N=None, axis=0):
        """Return the analytic waveform.

        Parameters
        ----------
        N : int, optional
            Number of Fourier components. If None, set to x.shape[axis].
        axis : int, optional
            Axis along which to do the transformation.

        Returns
        -------
        Waveform

        Raises
        ------
        TypeError
            If Waveform has missing samples.

        See Also
        --------
        scipy.signal.hilbert
        """
        if np.any(self.get_unknown_mask()):
            errmsg = 'Waveform has missing samples.'
            raise TypeError(errmsg)

        y = hilbert(self, N=N, axis=axis)
        return Waveform(data=y, fs=self.fs)

    def clip(self, min_value=None, max_value=None):
        """Clip audio data according to given bound values.

        See :ref:`Type of Entry<type_entry_waveform>` for details.

        Parameters
        ----------
        max_value : float, optional
            Clipping is applied above this value.
        min_value : float, optional
            Clipping is applied below this value.

        Raises
        ------
        UserWarning
            If some coefficients are actually clipped.

        Notes
        -----
        Masked values can be also clipped.
        """
        if min_value is None:
            min_value = np.min(self)

        if max_value is None:
            max_value = np.max(self)

        if np.issubdtype(self.dtype, np.complexfloating):
            w_real = Waveform(np.real(self))
            w_imag = Waveform(np.imag(self))

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                w_real.clip(min_value=min_value, max_value=max_value)

            warnmsg = 'Real part of the complex entries: {}'
            for w_i in w:
                warnings.warn(warnmsg.format(str(w_i.message)))

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                w_imag.clip(min_value=min_value, max_value=max_value)

            warnmsg = 'Imaginary part of the complex entries: {}'
            for w_i in w:
                warnings.warn(warnmsg.format(str(w_i.message)))

            self[:] = np.array(w_real) + 1j * np.array(w_imag)

        else:
            ind_min = self < min_value
            if np.any(ind_min):
                self[ind_min] = min_value
                warnmsg = '{} values lower than {} have been clipped.'
                warnings.warn(warnmsg.format(self.dtype, min_value))

            ind_max = self > max_value
            if np.any(ind_max):
                self[ind_max] = max_value
                warnmsg = '{} values greater than {} have been clipped.'
                warnings.warn(warnmsg.format(self.dtype, max_value))

    def astype(self, dtype):
        """Cast the waveform into a given type (float, int, or complex).

        Parameters
        ----------
        dtype : data-type, optional
            Output data type. See :ref:`Type of Entry<type_entry_waveform>`.

        Returns
        -------
        nd-array
            Waveform with the desired dtype.

        Raises
        ------
        TypeError
            If argument `dtype` is an unsupported data type.
        UserWarning
            If some coefficients are actually clipped.
        """
        y = self.copy()

        if (np.issubdtype(self.dtype, np.floating) or
                np.issubdtype(self.dtype, np.complexfloating)):

            if (np.issubdtype(dtype, np.floating) or
                    np.issubdtype(dtype, np.complexfloating)):
                y.clip(min_value=-1, max_value=(1 - np.finfo(dtype).eps))
                y = np.asarray(y, dtype=dtype)

            elif np.issubdtype(dtype, np.integer):
                target_type_info = np.iinfo(dtype)
                int_range = target_type_info.max - target_type_info.min + 1
                y = np.floor((np.real(y) + 1) / 2 * int_range +
                             target_type_info.min)
                y.clip(min_value=np.iinfo(dtype).min,
                       max_value=np.iinfo(dtype).max)
                y = np.asarray(y, dtype=dtype)

            else:
                errmsg = 'Unsupported target type {}.'
                raise TypeError(errmsg.format(dtype))

        else:
            src_iinfo = np.iinfo(y.dtype)

            if np.issubdtype(dtype, np.floating):
                int_range = src_iinfo.max - src_iinfo.min + 1
                zero = src_iinfo.min + int_range // 2
                y = ((super(type(y), y).astype(dtype) - zero)
                     / (int_range // 2))
                y.clip(min_value=-1, max_value=1-np.finfo(dtype).eps)
                y = np.asarray(y, dtype=dtype)

            elif np.issubdtype(dtype, np.integer):
                y = y.astype(dtype=np.float64)
                y = y.astype(dtype=dtype)
                y = np.asarray(y)

            elif np.issubdtype(dtype, np.complexfloating):
                y = y.astype(dtype=np.float64)
                y = np.asarray(y, dtype=dtype)

            else:
                errmsg = 'Unsupported target type {}.'
                raise TypeError(errmsg.format(dtype))

        return Waveform(y, mask=self.get_unknown_mask(), fs=self.fs)

    def copy(self):
        return Waveform(self)

    def __eq__(self, other):
        if isinstance(other, Waveform):
            _check_compatibility_fs(self, other)

        return super().__eq__(other)

    def is_equal(self, other):
        return self.fs == other.fs and super().is_equal(other)

    def __str__(self):

        string = super().__str__()
        string = string.replace('MadArray', 'Waveform, fs={}Hz, length={}')

        return string.format(self.fs, self.length)

    def __repr__(self):
        string = super().__repr__()
        string = string.replace('MadArray', 'Waveform')
        return string
