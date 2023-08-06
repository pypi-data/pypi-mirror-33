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
"""Definition of a masked array.

.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Valentin Emiya
.. moduleauthor:: Florent Jaillet
"""
import numpy as np


def _merge_masks(ma1, ma2):
    """Merge the masks of two :class:`MadArray` objects and return the
    arguments used for initialisation of the resulting :class:`MadArray`
    object.

    Parameters
    ----------
    ma1 : MadArray
       First masked array to consider.
    ma2 : MadArray
       Second masked array to consider.

    Returns
    -------
    dict
        Arguments to be used for the initialisation of a :class:`MadArray`
        object.
    """
    if ma1._complex_masking or ma2._complex_masking:

        if ma1._complex_masking:
            mm1 = ma1.get_unknown_mask('magnitude')
            mp1 = ma1.get_unknown_mask('phase')
        else:
            mm1 = ma1.get_unknown_mask('any')
            mp1 = ma1.get_unknown_mask('any')

        if ma2._complex_masking:
            mm2 = ma2.get_unknown_mask('magnitude')
            mp2 = ma2.get_unknown_mask('phase')
        else:
            mm2 = ma2.get_unknown_mask('any')
            mp2 = ma2.get_unknown_mask('any')

        mask_magnitude = np.logical_or(mm1, mm2)
        mask_phase = np.logical_or(mp1, mp2)

        return {'mask_magnitude': mask_magnitude, 'mask_phase': mask_phase}
    else:
        return {'mask': (ma1.get_unknown_mask()) | (ma2.get_unknown_mask())}


UFUNC_NOT_RETURNING_MADARRAYS = ['bitwise_and', 'bitwise_or', 'bitwise_xor',
                                 'invert', 'left_shift', 'right_shift',
                                 'greater', 'greater_equal', 'less',
                                 'less_equal', 'not_equal', 'equal',
                                 'logical_and', 'logical_or', 'logical_xor',
                                 'logical_not', 'maximum', 'minimum', 'fmax',
                                 'fmin', 'isfinite', 'isinf', 'isnan', 'isnat',
                                 'signbit', 'copysign', 'nextafter', 'spacing',
                                 'modf',  'frexp', 'fmod']


class MadArray(np.ndarray):
    """Subclass of numpy.ndarray to handle data with missing elements.

    .. _type_entry_madarray:

    **Type of entry**: entries of array can be *int*, *float*, or *complex*.

    .. _masking_madarray:

    **Masking**: the masking of entries has two different modes:

    * Entries can be either masked or not masked, leading to a boolean mask,
      whose entries are equal to True if the corresponding data entry is
      masked, or False otherwise.
      
      This is the default mode and the mode selected when specifying ``mask``
      during creation.

    * Complex entries can have only the magnitude or phase component masked, or
      both. The resulting mask has integers entries, equal to:

        * *0* if the phase and the magnitude are not masked (known magnitude
          and phase);
        * *1* if only the phase is masked (known magnitude, unknown phase);
        * *2* if only the magnitude is masked (unknown magnitude, known phase);
        * *3* if the magnitude and the phase are masked (unknown magnitude and
          phase).

      This mode is selected when specifying ``mask_magnitude`` and/or
      ``mask_phase`` during creation.
      Entries are converted to a complex type.

      If entries are complex values and ``mask`` is given during creation, both
      the magnitude and phase are masked and the boolean mask mode is used.

    .. _indexing_madarray:

    **Indexing**: two different modes to index a :class:`MadArray` object are
    implemented:

    * a :class:`MadArray` object with shape corresponding to the indices is
      returned, with both the data matrix and the mask properly indexed. This
      is the default mode;
    * a :class:`MadArray` object with unchanged shape is returned, where
      non-indexed entries are set as masked. This mode is selected by setting
      the parameter ``masked_indexing`` to True.

    .. _numpy_behaviour_madarray:

    **Numpy behaviour**: it is possible to use standard operations (+, -, /,
    //, \*, T) between two :class:`MadArray` objects, likewise operations
    between numpy arrays. The resulting object has a mask consisting of the
    union of the operands. It is also possible to use pickle operations to
    jointly store the data and the mask.

    Parameters
    ----------
    data : array_like
        Multidimensional array. See :ref:`Type of Entry<type_entry_madarray>`.
    mask : boolean array_like, optional
        Mask for boolean masking mode.
        See :ref:`Masking<masking_madarray>`.
    mask_magnitude : boolean array_like or None, optional
        Magnitude mask for masking with complex data.
        See :ref:`Masking<masking_madarray>`.
    mask_phase : boolean or array_like or None, optional
        Phase mask for masking with complex data.
        See :ref:`Masking<masking_madarray>`.
    masked_indexing : bool or None, optional
        Indicate how the indexing is performed. If None, set to False.
        See :ref:`Indexing<indexing_madarray>`.

    Warnings
    --------
    This class inherits from ndarray or subclass of ndarray. Instances can be
    then manipulated like ndarrays (e.g., indexation). While some methods have
    been implemented taking into account the mask, some may cause unexpected
    behavior (e.g., mean).

    See also
    --------
    :mod:`numpy.doc.subclassing`.

    Notes
    -----
    This class implements an alternative masked array different from
    :class:`numpy.ma.MaskedArray`. The reason of this choice is that it is only
    used as a container of a ndarray and a mask. No masked operations are
    needed.
    """
    def __new__(cls, data, mask=None, mask_magnitude=None, mask_phase=None,
                masked_indexing=None, **kwargs):

        if mask is not None and mask_magnitude is not None:
            errmsg = ('Parameters mask and mask_magnitude are mutually '
                'exclusive')
            raise ValueError(errmsg)

        if mask is not None and mask_phase is not None:
            errmsg = 'Parameters mask and mask_phase are mutually exclusive'
            raise ValueError(errmsg)

        _data = np.array(data, **kwargs)

        if not (np.issubdtype(_data.dtype, np.floating) or
                np.issubdtype(_data.dtype, np.integer) or
                np.issubdtype(_data.dtype, np.complexfloating)):
            errmsg = 'Invalid dtype: {}'
            raise TypeError(errmsg.format(data.dtype))

        if mask is not None:
            complex_masking = False
        elif mask_magnitude is not None or mask_phase is not None:
            complex_masking = True
        elif isinstance(data, MadArray):
            complex_masking = data._complex_masking
        else:
            complex_masking = False

        if masked_indexing is None:
            if isinstance(data, MadArray):
                masked_indexing = data._masked_indexing
            else:
                masked_indexing = False

        if not complex_masking:

            if mask is None:
                if isinstance(data, MadArray):
                    mask = data.get_unknown_mask()
                else:
                    mask = np.zeros(_data.shape, dtype=np.bool)
            else:
                mask = np.array(mask, dtype=np.bool)
                if mask.shape != _data.shape:
                    errmsg = "Mask shape {} and data shape {} not compatible."
                    raise ValueError(errmsg.format(mask.shape, data.shape))
                mask = mask

        else:

            if not np.issubdtype(_data.dtype, np.complexfloating):
                _data = _data.astype(np.complex)

            if mask_magnitude is None:
                if isinstance(data, MadArray) and mask_phase is None:
                    mask_magnitude = data.get_unknown_mask('magnitude')
                    mask_phase = data.get_unknown_mask('phase')
                else:
                    mask_magnitude = np.zeros_like(data, dtype=np.bool)
            else:
                mask_magnitude = np.array(mask_magnitude, dtype=np.bool)
                if mask_magnitude.shape != _data.shape:
                    errmsg = 'Magnitude mask shape {} and data shape {} not '\
                        'compatible.'
                    raise ValueError(errmsg.format(mask_magnitude.shape,
                                                   _data.shape))

            if mask_phase is None:
                mask_phase = np.zeros_like(data, dtype=np.bool)

            else:
                mask_phase = np.array(mask_phase, dtype=np.bool)
                if mask_phase.shape != _data.shape:
                    errmsg = 'Phase mask shape {} and data shape {} not '\
                        'compatible.'
                    raise ValueError(errmsg.format(
                        mask_phase.shape, _data.shape))

            mask = np.zeros(_data.shape, dtype=np.uint8)
            mask[np.logical_and(mask_phase, ~mask_magnitude)] = 1
            mask[np.logical_and(~mask_phase, mask_magnitude)] = 2
            mask[np.logical_and(mask_phase, mask_magnitude)] = 3

        # create the object
        obj = np.ndarray.__new__(cls, _data.shape, dtype=_data.dtype)
        obj[:] = _data
        obj._mask = mask
        obj._masked_indexing = masked_indexing
        obj._complex_masking = complex_masking

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._mask = getattr(obj, '_mask', None)
        self._complex_masking = getattr(obj, '_complex_masking', None)
        self._masked_indexing = getattr(obj, '_masked_indexing', None)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):

        args = []
        is_mad = []
        for input_ in inputs:
            if isinstance(input_, MadArray):
                args.append(input_.view(np.ndarray))
                is_mad.append(True)
            else:
                args.append(input_)
                is_mad.append(False)

        if len(is_mad) > 1:
            if np.all(is_mad):
                if inputs[0]._complex_masking or inputs[1]._complex_masking:
                    errmsg = 'Operation not permitted when complex masking.'
                    raise ValueError(errmsg)

                mask = MadArray(inputs[0].data, **
                                _merge_masks(inputs[0], inputs[1]))._mask
                complex_masking = inputs[0]._complex_masking
                masked_indexing = inputs[0]._masked_indexing
            else:
                where_is_mad = np.argwhere(is_mad).squeeze()
                mask = inputs[where_is_mad]._mask
                complex_masking = inputs[where_is_mad]._complex_masking
                masked_indexing = inputs[where_is_mad]._masked_indexing

        else:
            mask = inputs[0]._mask
            complex_masking = inputs[0]._complex_masking
            masked_indexing = inputs[0]._masked_indexing

        outputs = kwargs.pop('out', None)
        if outputs:
            out_args = []
            for output in outputs:
                out_args.append(output.view(np.ndarray))
            kwargs['out'] = tuple(out_args)
        else:
            outputs = (None,) * ufunc.nout

        results = (super().__array_ufunc__(ufunc, method, *args, **kwargs), )

        new_results = []
        for result, output in zip(results, outputs):
            if output is None:
                if (method == '__call__' and
                        ufunc.__name__ not in UFUNC_NOT_RETURNING_MADARRAYS):
                    new_results.append(np.asarray(result).view(MadArray))
                    new_results[-1]._mask = mask
                    new_results[-1]._complex_masking = complex_masking
                    new_results[-1]._masked_indexing = masked_indexing
                else:
                    new_results.append(np.asarray(result).view(np.ndarray))
            else:
                new_results.append(output)
        results = tuple(new_results)

        return results[0] if len(results) == 1 else results

    def __getitem__(self, index):

        if (getattr(self, '_masked_indexing', None) is not None and
                self._masked_indexing):

            mask = np.zeros(self.shape, dtype=np.bool)
            mask[index] = True
            return MadArray(self, mask=np.logical_or(~mask, self._mask))
        else:
            out_arr = super().__getitem__(index)
            if getattr(out_arr, '_mask', None) is not None:
                out_arr._mask = out_arr._mask[index]
            return out_arr

    def __reduce__(self):
        pickled_state = super().__reduce__()
        new_state = pickled_state[2] + (self._mask, self._complex_masking,
                                        self._masked_indexing)
        return pickled_state[0], pickled_state[1], new_state

    def __setstate__(self, state):
        self._mask = state[-3]
        self._complex_masking = state[-2]
        self._masked_indexing = state[-1]
        super().__setstate__(state[0:-3])

    @property
    def n_missing_data(self):
        """Number of missing data (double or tuple).

        Number of masked coefficients if dtype is int or float. Number of
        masked coefficients in phase and magnitude masks if dtype is complex.
        """
        if self._complex_masking:
            return (np.sum(self.get_unknown_mask('magnitude')),
                    np.sum(self.get_unknown_mask('phase')))
        else:
            return np.sum(self.get_unknown_mask())

    @property
    def ratio_missing_data(self):
        """Ratio of missing data (double or tuple).

        Ratio of masked coefficients if dtype is int or float. Ratio of
        masked coefficients in phase and magnitude masks if dtype is complex.
        """
        if self._complex_masking:
            return (np.average(self.get_unknown_mask('magnitude')),
                    np.average(self.get_unknown_mask('phase')))
        else:
            return np.average(self.get_unknown_mask())

    def is_masked(self):
        """Indicate if one or several elements are masked."""
        return np.any(self._mask)

    def to_np_array(self, fill_value=None):
        """Return a numpy array.

        If ``fill_value`` is not None, masked elements are replaced according
        to the type of entries:

        * ``fill_value`` if the type of entries is *int* or *float*;
        * If the type is *complex*, missing entries are replaced either by:
            * a complex number with the known magnitude value without the phase
              information if only the phase is masked;
            * a complex number of magnitude 1 with the known phase if only the
              magnitude is masked;
            * by ``fill_value`` if both magnitude and phase are masked.

        Parameters
        ----------
        fill_value : scalar or None
            Value used to fill masked elements. If None, the initial value is
            kept.

        Returns
        -------
        nd-array
        """
        data = np.array(self)
        if fill_value is not None:
            if self._complex_masking:
                upom = self.get_unknown_mask('phase only')
                umom = self.get_unknown_mask('magnitude only')
                data[upom] = np.abs(data[upom])
                data[umom] = np.exp(1j * np.angle(data[umom]))
                data[self.get_unknown_mask('all')] = fill_value
            else:
                data[self.get_unknown_mask()] = fill_value
        return data

    def __eq__(self, other):
        if isinstance(other, MadArray):
            return np.logical_and(self.to_np_array(0) == other.to_np_array(0),
                                  self._mask == self._mask)
        else:
            return np.array(self) == other

    def __ne__(self, other):
        return np.logical_not(self == other)

    def is_equal(self, other):
        if not isinstance(other, MadArray):
            return False

        if not np.all(self == other):
            return False

        if not (self._complex_masking == other._complex_masking and
                self._masked_indexing == other._masked_indexing):
            return False

        return True

    @property
    def T(self):
        """Transpose of the MadArray."""
        return self.transpose()

    def copy(self):
        return MadArray(self)

    def transpose(self):
        mat = super().transpose()
        mat._mask = mat._mask.transpose()
        return mat

    def __str__(self):
        arr = np.array(self)

        if np.issubdtype(self.dtype, np.integer):
            arr = arr.astype(np.float64)

        arr[self.get_unknown_mask()] = np.nan
        arr_str = np.ndarray.__str__(arr)
        if np.isrealobj(arr):
            arr_str = arr_str.replace('nan', '  x')
        else:
            arr_str = arr_str.replace('nan+0.j', '  x    ')

        if np.issubdtype(self.dtype, np.integer):
            arr_str = arr_str.replace('.', '')

        if self._complex_masking:
            n_all_unknown = np.count_nonzero(self.get_unknown_mask('all'))
            string = 'MadArray, dtype={0}, ' \
                     '{1[0]} missing magnitudes ({2[0]:.1%}) ' \
                     'and {1[1]} missing phases ({2[1]:.1%}), ' \
                     ' including {3} missing magnitudes and phases jointly ' \
                     '({4:.1%})\n{5}'
            return string.format(self.dtype,
                                 self.n_missing_data,
                                 self.ratio_missing_data,
                                 n_all_unknown,
                                 n_all_unknown/self.size,
                                 arr_str)
        else:
            string = 'MadArray, dtype={}, {} missing entries ({:.1%})\n{}'

            return string.format(self.dtype,
                                 self.n_missing_data,
                                 self.ratio_missing_data, arr_str)

    def __repr__(self):
        string = '<MadArray at {}>'
        return string.format(hex(id(self)))

    def get_known_mask(self, mask_type='all'):
        """Boolean mask for known coefficients.

        Compute the boolean mask marking known coefficients as True.

        Parameters
        ----------
        mask_type : {'all', 'any', 'magnitude', 'phase', 'magnitude only', \
                    'phase only'}
            Type of mask:

            - ``all``: mark coefficients for wich both the magnitude and the
              phase are known,
            - ``any``: mark coefficients for wich the magnitude or the phase
              are known (including when both the magnitude and the phase are
              known),
            - ``magnitude``: mark coefficients for wich the magnitude is
              known,
            - ``phase``: mark coefficients for wich the phase is known,
            - ``magnitude only``: mark coefficients for wich both the magnitude
              is known and the phase is unknown,
            - ``phase only``: mark coefficients for wich both the phase is
              known and the magnitude is unknown.
            
        Returns
        -------
        mask : boolean nd-array
            Boolean array with entries set to True if the corresponding value
            in the object is known.

        Raises
        ------
        ValueError
            If ``mask_type`` has an invalid value.
        """
        if mask_type == 'all':
            return ~self.get_unknown_mask('any')
        elif mask_type == 'any':
            return ~self.get_unknown_mask('all')
        elif mask_type == 'magnitude':
            return ~self.get_unknown_mask('magnitude')
        elif mask_type == 'phase':
            return ~self.get_unknown_mask('phase')
        elif mask_type == 'magnitude only':
            return self.get_unknown_mask('phase only')
        elif mask_type == 'phase only':
            return self.get_unknown_mask('magnitude only')

        errmsg = 'Invalid value for mask_type: {}'.format(mask_type)
        raise ValueError(errmsg)

    def get_unknown_mask(self, mask_type='any'):
        """Boolean mask for unknown coefficients.

        Compute the boolean mask marking unknown coefficients as True.

        Parameters
        ----------
        mask_type : {'any', 'all', 'magnitude', 'phase', 'magnitude only', \
                    'phase only'}
            Type of mask:

            - ``any``: mark coefficients for wich the magnitude or the phase
              are unknown (including when both the magnitude and the phase are
              unknown),
            - ``all``: mark coefficients for wich both the magnitude and the
              phase are unknown,
            - ``magnitude``: mark coefficients for wich the magnitude is
              unknown,
            - ``phase``: mark coefficients for wich the phase is unknown,
            - ``magnitude only``: mark coefficients for wich both the magnitude
              is unknown and the phase is known,
            - ``phase only``: mark coefficients for wich both the phase is
              unknown and the magnitude is known.

        Returns
        -------
        mask : boolean nd-array
            Boolean array with values set to True if the corresponding value in
            the object is unknown.

        Raises
        ------
        ValueError
            If ``mask_type`` has an invalid value.
        """
        if self._complex_masking:
            if mask_type == 'any':
                return self._mask != 0
            elif mask_type == 'all':
                return self._mask == 3
            elif mask_type == 'magnitude':
                return (self._mask == 3) | (self._mask == 2)
            elif mask_type == 'phase':
                return (self._mask == 3) | (self._mask == 1)
            elif mask_type == 'magnitude only':
                return self._mask == 2
            elif mask_type == 'phase only':
                return self._mask == 1
        else:
            if mask_type in ('any', 'all', 'magnitude', 'phase'):
                return np.copy(self._mask)
            elif mask_type in ('magnitude only', 'phase only'):
                return np.zeros_like(self._mask, dtype=np.bool)

        errmsg = 'Invalid value for mask_type: {}'.format(mask_type)
        raise ValueError(errmsg)
