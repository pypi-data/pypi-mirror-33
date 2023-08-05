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

import subprocess
import sys

import config
import make_matrix
import utils
import validators

def get_resolution(args):
    try:
        hdf5_path = args.hdf5
    except AttributeError:
        try:
            hdf5_path = open(args.hdf5List).readline().strip()
        except AttributeError:
            raise AssertionError("get_resolution called outside of filter or correlation mode")
    return str(utils.read_compatibility_data(hdf5_path, args.chromSizes)["bin"])

def get_hdf5_converter(args):
    if args.bigwig:
        return config.BW_TO_HDF5_PATH
    elif args.bedgraph:
        return config.BG_TO_HDF5_PATH
    else:
        raise AssertionError("Parser failed to enforce mentatory -bw -bg")

def to_hdf5(args):
    validators.valid_to_hdf5(args)
    exe = get_hdf5_converter(args)
    command = [exe,
               args.signalFile,
               args.chromSizes,
               str(args.resolution),
               args.outHdf5]
    subprocess.call(command)

def hdf5_filter(args):
    validators.valid_filter(args)
    if args.select:
        select = args.select
    else:
        select = utils.tmp_name()
        utils.make_all_filter(open(select, 'w'), open(args.chromSizes))
    if args.exclude:
        exclude = args.exclude
    else:
        exclude = utils.tmp_name()
        open(exclude, 'w')
    command = [config.FILTER_PATH,
               args.hdf5,
               args.chromSizes,
               get_resolution(args),
               args.outHdf5,
               select,
               exclude]
    subprocess.call(command)

def corr(args):
    validators.valid_corr(args)
    #call correlation
    if args.single_chrom:
        exec_path = config.CORRW_PATH
    else:
        exec_path = config.CORR_PATH

    command = [exec_path,
               args.hdf5List,
               args.chromSizes,
               get_resolution(args),
               args.outMatrix]
    subprocess.call(command)
