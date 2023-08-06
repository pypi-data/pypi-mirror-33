from __future__ import print_function
import os
import unittest
from numpy import array_equal, allclose

import pyNastran
from pyNastran.converters.dev.code_aster.nastran_to_code_aster import CodeAsterConverter

PKG_PATH = pyNastran.__path__[0]
model_path = os.path.join(PKG_PATH, '..', 'models')
test_path = os.path.join(PKG_PATH, 'converters', 'dev', 'code_aster')
test_path = os.path.join(PKG_PATH, 'converters', 'dev', 'code_aster')

class TestCodeAster(unittest.TestCase):

    def test_code_aster_io_01(self):
        bdf_filename = os.path.join(model_path, 'solid_bending', 'solid_bending.bdf')

        #bdf_filename = data['BDF_FILENAME']
        fname_base = os.path.basename(os.path.splitext(bdf_filename)[0])

        ca = CodeAsterConverter()
        ca.read_bdf(bdf_filename, encoding='ascii')
        ca.write_as_code_aster(fname_base)  # comm, py


if __name__ == '__main__':  # pragma: no cover
    import time
    time0 = time.time()
    unittest.main()
    print("dt = %s" % (time.time() - time0))
