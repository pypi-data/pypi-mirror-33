from __future__ import absolute_import, division, unicode_literals

import os
import struct

from . import _common as common


class dist_writer():
    def __init__(self, filename, matr, create_file=False):
        if matr.ndim != 2 or matr.shape[0] != matr.shape[1]:
            raise RuntimeError('Distance matrices must be square matrices')
        self.matr_size = matr.shape[0]
        self.value_type = matr.dtype
        self.curr_row = 0

        # open file
        self.file = open(filename, 'wb')
        if create_file:
            # write header
            self.file.write(common.DIST_SIGNATURE)
            self.file.write(struct.pack('<B',
                            common.element_type_for_dtype(self.value_type)))
            self.file.write(struct.pack('<Q', self.matr_size))
        else:
            self.file.seek(0, os.SEEK_END)

    def write_next_row(self, matr, flush_file=True):
        if matr.dtype != self.value_type:
            raise RuntimeError("The given matrix's value type must match the "
                               "header")
        if matr.shape != (self.matr_size, self.matr_size):
            raise RuntimeError('The size of given matrix must match the size '
                               'given in the header')
        if self.curr_row >= self.matr_size:
            raise RuntimeError('The whole matrix has already been written')

        self.file.write(matr[self.curr_row,
                             self.curr_row+1:self.matr_size].tobytes())

        self.curr_row += 1
        if flush_file:
            self.file.flush()

    def write_whole_matrix(self, matr):
        for _ in range(self.matr_size):
            self.write_next_row(matr, flush_file=False)

        self.file.flush()
