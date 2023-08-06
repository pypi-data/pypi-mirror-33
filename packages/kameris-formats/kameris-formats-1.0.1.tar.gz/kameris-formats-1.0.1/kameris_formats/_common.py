from __future__ import absolute_import, division, unicode_literals

import numpy as np
from six import iteritems


# 0 at the end is the version number
REPR_SIGNATURE = b'MMREPR\0'
DIST_SIGNATURE = b'MMDIST\0'

REPR_HEADER_SIZE = 34


dtype_for_element_type = {
    0: np.dtype('<u1'),
    1: np.dtype('<u2'),
    2: np.dtype('<u4'),
    3: np.dtype('<u8'),
    4: np.dtype('<f4'),
    5: np.dtype('<f8')
}


def element_type_for_dtype(dtype):
    return next(et for et, dt in iteritems(dtype_for_element_type) if
                dt == dtype)
