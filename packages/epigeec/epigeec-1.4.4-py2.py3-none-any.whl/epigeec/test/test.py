#!/usr/bin/env python
# Copyright (C) 2015 Jonathan Laperle. All Rights Reserved.
# 
# This program is free software: you can redistribute it and/or modify
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
# =============================================================================

from __future__ import absolute_import, division, print_function

import argparse
import logging
import os
import os.path
import sys
import unittest
import warnings

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import python.core.config as config
sys.path.append(config.CORE_DIR)
import python.core.main as epimain
import python.core.make_matrix as make_matrix
import python.core.launcher as launcher

def get_corr_vals(mat):
    mat.readline()
    vals = []
    for line in mat:
        vals += line.split()[1:]
    return vals

def launch_to_hdf5(sig_path, chrom_path, resolution, hdf5_path):
    args = ["to_hdf5", "-bw", sig_path, chrom_path, resolution, hdf5_path]
    logging.debug(args)
    epimain.main(args)

def launch_filter(hdf5_path, chrom_path, filtered_path, include_path=None, exclude_path=None):
    args = ["filter", hdf5_path, chrom_path, filtered_path]
    logging.debug(args)
    epimain.main(args)

def launch_corr(list_path, chrom_path, mat_path):
    args = ["correlate", list_path, chrom_path, mat_path]
    logging.debug(args)
    epimain.main(args)

def launch_corr_w(list_path, chrom_path, mat_path):
    args = ["correlate", "-A", list_path, chrom_path, mat_path]
    logging.debug(args)
    epimain.main(args)

def launch_corr_nm(list_path1, list_path2, chrom_path, mat_path):
    launcher.corr_nm(False, list_path1, list_path2, chrom_path, mat_path)

def launch_make_matrix(mat_nn, mat_nm, mat_mm, mat_path):
    args = ["-nm", mat_nm, "-mm", mat_mm, mat_nn, mat_path]
    logging.debug(args)
    make_matrix.main(args)

class EpigeecTest(unittest.TestCase):
    def e2e(self):
        self.files_dir = os.path.join(config.TEST_DIR, "files")
        self.sig_dir = os.path.join(self.files_dir, "signal")
        self.hdf5_dir = os.path.join(self.files_dir, "hdf5")
        self.filtered_dir = os.path.join(self.files_dir, "filtered")
        self.chrom_dir = os.path.join(config.RES_DIR, "chrom_sizes")
        self.epigeec_path = os.path.join(config.PY_DIR, "main.py")
        self.list_path = os.path.join(config.TEST_DIR, "test_list.txt")
        self.mat_path = os.path.join(self.files_dir, "test.mat")

    def test_e2e_nm(self):
        self.e2e()
        sig_path = [os.path.join(self.sig_dir, "d9f18e91644bacfee3669d577b661d15"),
                    os.path.join(self.sig_dir, "fd85fe6672c629a116a9b6131883a60b"),
                    os.path.join(self.sig_dir, "70ac0e9e6b4dbdf5d6b5cbf54a8989e3")]
        hdf5_path1 = [os.path.join(self.hdf5_dir, "d9f18e91644bacfee3669d577b661d15"),
                    os.path.join(self.hdf5_dir, "fd85fe6672c629a116a9b6131883a60b")]
        hdf5_path2 = [os.path.join(self.hdf5_dir, "70ac0e9e6b4dbdf5d6b5cbf54a8989e3")]
        list_path2 = os.path.join(config.TEST_DIR, "test_list2.txt")
        mat_path1 = os.path.join(self.files_dir, "test1.mat")
        mat_path2 = os.path.join(self.files_dir, "test2.mat")
        mat_path3 = os.path.join(self.files_dir, "test3.mat")
        chrom_path = os.path.join(self.chrom_dir, "saccer3.can.chrom.sizes")
        resolution = "10000"

        with open(self.list_path, 'w') as test_list:
            test_list.write("{0}\n{1}".format(hdf5_path1[0], hdf5_path1[1]))
        with open(list_path2, 'w') as test_list:
            test_list.write("{0}".format(hdf5_path2[0]))

        launch_to_hdf5(sig_path[0], chrom_path, resolution, hdf5_path1[0])
        launch_to_hdf5(sig_path[1], chrom_path, resolution, hdf5_path1[1])
        launch_to_hdf5(sig_path[2], chrom_path, resolution, hdf5_path2[0])

        launch_corr(self.list_path, chrom_path, mat_path1)
        launch_corr(list_path2, chrom_path, mat_path2)
        launch_corr_nm(self.list_path, list_path2, chrom_path, mat_path3)

        launch_make_matrix(mat_path1, mat_path3, mat_path2, self.mat_path)

        result = os.path.join(self.files_dir, "test.mat")
        expected = os.path.join(self.files_dir, "expected_nm")
        self.assertEqual(open(result).read(), open(expected).read())

        os.remove(hdf5_path1[0])
        os.remove(hdf5_path1[1])
        os.remove(hdf5_path2[0])
        os.remove(self.list_path)
        os.remove(list_path2)
        os.remove(mat_path1)
        os.remove(mat_path2)
        os.remove(mat_path3)
        os.remove(self.mat_path)

    def test_e2e_hg19(self):
        self.e2e()
        sig_path = [os.path.join(self.sig_dir, "001f63cdf00286183e32c1bb0fd6d85f"),
                    os.path.join(self.sig_dir, "002f4247fadb6c6e4000a6fc12e5b93a")]
        hdf5_path = [os.path.join(self.hdf5_dir, "001f63cdf00286183e32c1bb0fd6d85f"),
                     os.path.join(self.hdf5_dir, "002f4247fadb6c6e4000a6fc12e5b93a")]
        chrom_path = os.path.join(self.chrom_dir, "hg19.noy.chrom.sizes")
        resolution = "10000"
        launch_to_hdf5(sig_path[0], chrom_path, resolution, hdf5_path[0])
        launch_to_hdf5(sig_path[1], chrom_path, resolution, hdf5_path[1])
        with open(self.list_path, 'w') as test_list:
            test_list.write("{0}\n{1}".format(hdf5_path[0], hdf5_path[1]))
        launch_corr(self.list_path, chrom_path, self.mat_path)
        expected = os.path.join(self.files_dir, "expected_hg19")
        result = os.path.join(self.files_dir, "test.mat")
        self.assertEqual(open(result).read(), open(expected).read())
        os.remove(hdf5_path[0])
        os.remove(hdf5_path[1])
        os.remove(self.list_path)
        os.remove(self.mat_path)

    def test_e2e_kent(self):
        self.e2e()
        sig_path = [os.path.join(self.sig_dir, "d9f18e91644bacfee3669d577b661d15"),
                    os.path.join(self.sig_dir, "fd85fe6672c629a116a9b6131883a60b")]
        hdf5_path = [os.path.join(self.hdf5_dir, "d9f18e91644bacfee3669d577b661d15"),
                    os.path.join(self.hdf5_dir, "fd85fe6672c629a116a9b6131883a60b")]
        chrom_path = os.path.join(self.chrom_dir, "saccer3.can.chrom.sizes")
        resolution = "10000"
        launch_to_hdf5(sig_path[0], chrom_path, resolution, hdf5_path[0])
        launch_to_hdf5(sig_path[1], chrom_path, resolution, hdf5_path[1])
        with open(self.list_path, 'w') as test_list:
            test_list.write("{0}\n{1}".format(hdf5_path[0], hdf5_path[1]))
        launch_corr_w(self.list_path, chrom_path, self.mat_path)

        result = os.path.join(self.files_dir, "test.mat")
        expected = os.path.join(self.files_dir, "expected_w")
        #self.assertEqual(get_corr_vals(open(result)), get_corr_vals(open(expected)))
        self.assertEqual(open(result).read(), open(expected).read())

        os.remove(hdf5_path[0])
        os.remove(hdf5_path[1])
        os.remove(self.list_path)
        os.remove(self.mat_path)

    def test_e2e_saccer(self):
        self.e2e()
        sig_path = [os.path.join(self.sig_dir, "d9f18e91644bacfee3669d577b661d15"),
                    os.path.join(self.sig_dir, "fd85fe6672c629a116a9b6131883a60b")]
        hdf5_path = [os.path.join(self.hdf5_dir, "d9f18e91644bacfee3669d577b661d15"),
                    os.path.join(self.hdf5_dir, "fd85fe6672c629a116a9b6131883a60b")]
        filtered_path = [os.path.join(self.filtered_dir, "d9f18e91644bacfee3669d577b661d15"),
                        os.path.join(self.filtered_dir, "fd85fe6672c629a116a9b6131883a60b")]
        mat_path = os.path.join(self.files_dir, "test.mat")
        chrom_path = os.path.join(self.chrom_dir, "saccer3.can.chrom.sizes")
        resolution = "10000"

        with open(self.list_path, 'w') as test_list:
            test_list.write("{0}\n{1}".format(filtered_path[0], filtered_path[1]))

        launch_to_hdf5(sig_path[0], chrom_path, resolution, hdf5_path[0])
        launch_to_hdf5(sig_path[1], chrom_path, resolution, hdf5_path[1])
        launch_filter(hdf5_path[0], chrom_path, filtered_path[0])
        launch_filter(hdf5_path[1], chrom_path, filtered_path[1])

        launch_corr(self.list_path, chrom_path, mat_path)

        result = os.path.join(self.files_dir, "test.mat")
        expected = os.path.join(self.files_dir, "expected")
        self.assertEqual(open(result).read(), open(expected).read())
        os.remove(hdf5_path[0])
        os.remove(hdf5_path[1])
        os.remove(self.list_path)
        os.remove(self.mat_path)

def main():
    parser = argparse.ArgumentParser(description='A test script for epigeec')
    parser.add_argument("-v", "--verbose", help="enable debug logs", action="store_true")

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    py_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "python", "core")
    loader = unittest.TestLoader()
    suites = []
    suites.append(loader.discover(py_dir, pattern = "*_test.py"))
    suites.append(loader.loadTestsFromTestCase(EpigeecTest))
    suite = unittest.TestSuite(suites)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    main()
