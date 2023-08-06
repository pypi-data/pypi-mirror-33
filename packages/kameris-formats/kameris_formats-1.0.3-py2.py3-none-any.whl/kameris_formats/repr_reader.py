from __future__ import absolute_import, division, unicode_literals

import numpy as np
import scipy.sparse as sparse
from six.moves import range
import struct

from . import _common as common


class repr_reader():
    def __init__(self, filename):
        self.file = open(filename, 'rb')

        # check header
        file_signature = self.file.read(len(common.REPR_SIGNATURE))
        if file_signature != common.REPR_SIGNATURE:
            raise RuntimeError('The given file is not a valid mm-repr '
                               'file')

        # fetch header values
        self.is_sparse = bool(ord(self.file.read(1)))
        key_type_val = ord(self.file.read(1))
        self.key_type = common.dtype_for_element_type[key_type_val]
        value_type_val = ord(self.file.read(1))
        self.value_type = common.dtype_for_element_type[value_type_val]
        self.count, = struct.unpack('<Q', self.file.read(8))
        self.rows, = struct.unpack('<Q', self.file.read(8))
        self.cols, = struct.unpack('<Q', self.file.read(8))

        if self.is_sparse:
            self.sizes = np.fromfile(self.file, dtype=np.dtype('<u8'),
                                     count=self.count)

    def read_matrix(self, index, flatten=False):
        if self.is_sparse:
            self.file.seek(common.REPR_HEADER_SIZE + (8 * self.count) +
                           sum(self.sizes[0:index]))

            if flatten:
                rows = 1
                cols = self.rows * self.cols
            else:
                rows = self.rows
                cols = self.cols
            result = sparse.dok_matrix((rows, cols),
                                       dtype=self.value_type)
            for i in range(self.sizes[index]):
                key, = np.fromfile(self.file, dtype=self.key_type, count=1)
                value, = np.fromfile(self.file, dtype=self.value_type, count=1)
                result[key // cols, key % cols] = value
            return result.tocsr()
        else:
            self.file.seek(common.REPR_HEADER_SIZE + (index * self.rows *
                           self.cols * self.value_type.itemsize))
            result = np.fromfile(self.file, dtype=self.value_type,
                                 count=self.rows * self.cols)
            if flatten:
                return result
            else:
                return result.reshape((self.rows, self.cols))
