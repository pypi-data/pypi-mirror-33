from __future__ import absolute_import, division, unicode_literals

import numpy as np
import struct

from . import _common as common


class dist_reader():
    @staticmethod
    def read_matrix(filename):
        with open(filename, 'rb') as file:
            # check header
            file_signature = file.read(len(common.DIST_SIGNATURE))
            if file_signature != common.DIST_SIGNATURE:
                raise RuntimeError('The given file is not a valid mm-dist '
                                   'file')

            # fetch header values
            value_type = ord(file.read(1))
            size, = struct.unpack('<Q', file.read(8))

            # read matrix values
            matrix_data_size = int(size * (size - 1) / 2)
            np_dtype = common.dtype_for_element_type[value_type]
            matrix_data = np.fromfile(file, dtype=np.dtype(np_dtype),
                                      count=matrix_data_size)

            # reshape to square
            result = np.zeros((size, size))
            result[np.triu_indices(size, 1)] = matrix_data
            return result + result.T
