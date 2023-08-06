#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import os
import sys
import unittest
from ipykernel.tests.utils import execute
from sos_notebook.test_utils import sos_kernel, get_std_output

class TestPreview(unittest.TestCase):
    def setUp(self):
        self.resource_dir = os.path.abspath(os.path.split(__file__)[0])

    @unittest.skipIf(sys.platform == 'win32', 'pysam is not installed under windows')
    def testMagicPreview(self):
        with sos_kernel() as kc:
            # preview bam file
            iopub = kc.iopub_channel
            execute(kc=kc, code='''
%preview -n {}/sim_reads_aligned.bam
'''.format(self.resource_dir))
            stdout, stderr = get_std_output(iopub)
            self.assertEqual(stderr, '')
            self.assertTrue('PG' in stdout)

            # preview sam file
            execute(kc=kc, code='''
%preview -n {}/sim_reads_aligned.sam
'''.format(self.resource_dir))
            stdout, stderr = get_std_output(iopub)
            self.assertEqual(stderr, '')
            self.assertTrue('PG' in stdout)


if __name__ == '__main__':
    unittest.main()
