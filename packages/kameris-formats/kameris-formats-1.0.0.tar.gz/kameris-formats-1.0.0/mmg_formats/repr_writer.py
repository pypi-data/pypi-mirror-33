from __future__ import absolute_import, division, unicode_literals

import numpy as np
import os
import scipy.sparse as sparse
from six.moves import zip
import struct

from . import _common as common


class repr_writer():
    def __init__(self, filename, matr, count, create_file=False):
        matr = np.atleast_2d(matr)
        if matr.ndim > 2:
            raise RuntimeError('Inputs must be vectors or matrices')

        self.is_sparse = sparse.issparse(matr)
        self.key_type = np.dtype('<u8')
        self.value_type = matr.dtype
        self.count = count
        self.rows = matr.shape[0]
        self.cols = matr.shape[1]
        self.curr_matr = 0

        # open file
        self.file = open(filename, 'wb')
        if create_file:
            # write header
            self.file.write(common.REPR_SIGNATURE)
            self.file.write(struct.pack('<B', self.is_sparse))
            self.file.write(struct.pack('<B',
                            common.element_type_for_dtype(self.key_type)))
            self.file.write(struct.pack('<B',
                            common.element_type_for_dtype(self.value_type)))
            self.file.write(struct.pack('<Q', self.count))
            self.file.write(struct.pack('<Q', self.rows))
            self.file.write(struct.pack('<Q', self.cols))

            # blank sizes table
            if self.is_sparse:
                self.file.write(np.zeros(self.count, dtype=np.dtype('<u8'))
                                  .tobytes())
        else:
            self.file.seek(0, os.SEEK_END)

    def write_matrix(self, matr):
        matr = np.atleast_2d(matr)

        if matr.dtype != self.value_type:
            raise RuntimeError("The given matrix's value type must match the "
                               "header")
        if matr.shape != (self.rows, self.cols):
            raise RuntimeError('The size of given matrix must match the size '
                               'given in the header')
        if self.curr_matr >= self.count:
            raise RuntimeError('All matrices have already been written')

        if not sparse.issparse(matr):
            if self.is_sparse:
                raise RuntimeError('The given matrix must not be sparse '
                                   'because the header is not sparse')

            self.file.seek(0, os.SEEK_END)
            self.file.write(matr.tobytes())
        else:
            if not self.is_sparse:
                raise RuntimeError('The given matrix must be sparse because '
                                   'the header is sparse')

            # size, to sizes table
            self.file.seek(common.REPR_HEADER_SIZE + (8 * self.curr_matr))
            self.file.write(struct.pack('<Q', matr.nnz))

            # data, to the end
            self.file.seek(0, os.SEEK_END)
            matr_coo = matr.tocoo()
            for row, col, val in zip(matr_coo.row, matr_coo.col,
                                     matr_coo.data):
                self.file.write(struct.pack('<Q', (row * self.cols) + col))
                self.file.write(np.array(val, dtype=self.value_type).tobytes())

        self.curr_matr += 1
        self.file.flush()
