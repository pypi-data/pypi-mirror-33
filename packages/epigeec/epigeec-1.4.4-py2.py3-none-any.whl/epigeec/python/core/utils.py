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

#supress h5py warning
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import h5py
import os
import tempfile

def tmp_name():
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    os.remove(temp_path)
    return temp_path

def make_all_filter(tmp, chrom):
    for line in chrom:
       line = line.strip()
       if line:
           line = line.split()
           tmp.write("{0}\t{1}\t{2}\n".format(line[0], "0", line[1]))

def read_compatibility_data(hdf5_path, chrom_path):
    compatibility_data = {}
    f = h5py.File(hdf5_path, "r")
    compatibility_data["bin"] = f.attrs["bin"][0]
    name = f.attrs["signal_filename"]
    for chrom in read_chrom_sizes(chrom_path).keys():
        chrom_data = f[name].get(chrom, 0)
        if chrom_data:
            size = chrom_data.shape[0]
            compatibility_data[chrom] = size
    return compatibility_data

def read_chrom_sizes(chrom_path):
    chroms = {}
    for line in open(chrom_path):
        line.strip()
        if line:
            line = line.split()
            chroms[line[0]] = line[1]
    return chroms
