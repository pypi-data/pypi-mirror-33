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

class EpigeecTest(unittest.TestCase):
    def test_e2e(self):
        parser = argparse.ArgumentParser(description='A test script for epigeec')
        parser.add_argument("-v", "--verbose", help="enable debug logs", action="store_true")

        args = parser.parse_args()
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)

        files_dir = os.path.join(config.TEST_DIR, "files")
        sig_dir = os.path.join(files_dir, "signal")
        hdf5_dir = os.path.join(files_dir, "hdf5")
        filtered_dir = os.path.join(files_dir, "filtered")
        chrom_dir = os.path.join(config.RES_DIR, "chrom_sizes")
        epigeec_path = os.path.join(config.PY_DIR, "main.py")
        list_path = os.path.join(config.TEST_DIR, "test_list.txt")
        sig_path = [os.path.join(sig_dir, "d9f18e91644bacfee3669d577b661d15"),
                    os.path.join(sig_dir, "fd85fe6672c629a116a9b6131883a60b")]
        hdf5_path = [os.path.join(hdf5_dir, "d9f18e91644bacfee3669d577b661d15"),
                    os.path.join(hdf5_dir, "fd85fe6672c629a116a9b6131883a60b")]
        filtered_path = [os.path.join(filtered_dir, "d9f18e91644bacfee3669d577b661d15"),
                        os.path.join(filtered_dir, "fd85fe6672c629a116a9b6131883a60b")]
        mat_path = os.path.join(files_dir, "test.mat")
        chrom_path = os.path.join(chrom_dir, "saccer3.can.chrom.sizes")
        resolution = "10000"

        with open(list_path, 'w') as test_list:
            test_list.write("{0}\n{1}".format(filtered_path[0], filtered_path[1]))

        launch_to_hdf5(sig_path[0], chrom_path, resolution, hdf5_path[0])
        launch_to_hdf5(sig_path[1], chrom_path, resolution, hdf5_path[1])
        launch_filter(hdf5_path[0], chrom_path, filtered_path[0])
        launch_filter(hdf5_path[1], chrom_path, filtered_path[1])

        launch_corr(list_path, chrom_path, mat_path)

        result = os.path.join(files_dir, "test.mat")
        expected = os.path.join(files_dir, "expected")
        #self.assertEqual(get_corr_vals(open(result)), get_corr_vals(open(expected)))
        self.assertEqual(open(result).read(), open(expected).read())

        launch_corr_w(list_path, chrom_path, mat_path)

        result = os.path.join(files_dir, "test.mat")
        expected = os.path.join(files_dir, "expected_w")
        #self.assertEqual(get_corr_vals(open(result)), get_corr_vals(open(expected)))
        self.assertEqual(open(result).read(), open(expected).read())

        os.remove(hdf5_path[0])
        os.remove(hdf5_path[1])
        os.remove(filtered_path[0])
        os.remove(filtered_path[1])
        os.remove(list_path)
        os.remove(mat_path)

        sig_path = [os.path.join(sig_dir, "001f63cdf00286183e32c1bb0fd6d85f"),
                    os.path.join(sig_dir, "002f4247fadb6c6e4000a6fc12e5b93a")]
        chrom_path = os.path.join(chrom_dir, "hg19.noy.chrom.sizes")
        hdf5_path = [os.path.join(hdf5_dir, "001f63cdf00286183e32c1bb0fd6d85f"),
                     os.path.join(hdf5_dir, "002f4247fadb6c6e4000a6fc12e5b93a")]
        launch_to_hdf5(sig_path[0], chrom_path, resolution, hdf5_path[0])
        launch_to_hdf5(sig_path[1], chrom_path, resolution, hdf5_path[1])
        with open(list_path, 'w') as test_list:
            test_list.write("{0}\n{1}".format(hdf5_path[0], hdf5_path[1]))
        launch_corr(list_path, chrom_path, mat_path)
        expected = os.path.join(files_dir, "expected_hg19")
        self.assertEqual(open(result).read(), open(expected).read())

        os.remove(hdf5_path[0])
        os.remove(hdf5_path[1])
        os.remove(list_path)
        os.remove(mat_path)

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
