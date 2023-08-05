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
import itertools
import struct

from error import ValidationError, MultiValidationError
import utils


def valid_to_hdf5(args):
    """
    args.signalFile
    args.chromSizes
    """
    if args.bigwig:
        valid_bw(args.signalFile)
    elif args.bedgraph:
        valid_bg(args.signalFile)
    else:
        raise AssertionError("Parser failed to enforce mentatory -bw -bg")
    valid_chromsizes(args.chromSizes)
    valid_resolution(args.resolution)

def valid_filter(args):
    """
    args.hdf5
    args.chromSizes
    args.select
    args.exclude
    """
    valid_hdf5(args.hdf5)
    valid_chromsizes(args.chromSizes)
    if args.select:
        valid_bed(args.select)
    if args.exclude:
        valid_bed(args.exclude)

def valid_corr(args):
    """
    args.hdf5List
    args.chromSizes
    """
    valid_hdf5_list(args.hdf5List)
    valid_chromsizes(args.chromSizes)

def valid_file(path, file_type, validator):
    try: 
        if not validator(path):
            #invalid content
            raise ValidationError("{0} is not a valid {1} file.".format(path, file_type))
    except IOError as e:
        if e.errno == 2:
            #file doesn't exist
            raise IOError("{0} doesn't exist.".format(path))
        if e.errno == 13:
            #permission denied
            raise IOError("{0}: Permission denied.".format(path))
    return True

def valid_hdf5_list(path):
    return valid_file(path, "HDF5 list" , is_hdf5_list)

def valid_bed(path):
    return valid_file(path, "BED" , is_bed)
    
def valid_bg(path):
    return valid_file(path, "bedGraph" , is_bg)

def valid_bw(path):
    return valid_file(path, "bigWig" , is_bw)

def valid_hdf5(path):
    return valid_file(path, "HDF5" , is_hdf5)

def valid_chromsizes(path):
    return valid_file(path, "chrom.sizes" , is_chromsizes)

def valid_resolution(res):
    if not res > 0:
        raise ValidationError("Resolution must be a strictly positive integer.")

def is_hdf5_list(path):
    errors = []
    compat_data = {}
    with open(path) as hdf5_list:
        for line in hdf5_list:
            line = line.strip()
            if line:
                try:
                    valid_hdf5(line)
                except (IOError, ValidationError) as e:
                    errors.append(e)
    if errors:
        raise MultiValidationError(errors)
    return True

def is_bed(path):
    with open(path) as bed:
        max_lines = 10 #number of lines to validate
        for line in itertools.islice(bed, max_lines):
            line = line.strip()
            if line:
                line = line.split()
                if not len(line) >= 3: return False
                if not is_int(line[1]): return False
                if not is_int(line[2]): return False
    return True

def is_bg(path):
    with open(path) as bg:
        max_lines = 10 #number of lines to validate
        for line in itertools.islice(bg, max_lines):
            line = bg.next().strip()
            if line:
                line = line.split()
                if not len(line) >= 4: return False
                if not is_int(line[1]): return False
                if not is_int(line[2]): return False
                if not is_float(line[3]): return False
    return True
            
def is_chromsizes(path):
    with open(path) as chroms:
        for line in chroms:
            line = line.strip()
            if line:
                line = line.split()
                if not len(line) >= 2: return False
                if not is_int(line[1]): return False
    return True

def is_bw(path):
    bw_magic = 0x888FFC26
    with open(path, "rb") as bw:
        magic = struct.unpack("I", bw.read(4))[0] 
        if magic != bw_magic:
            return False
    return True

def is_hdf5(path):
    return h5py.is_hdf5(path)

def is_int(i):
    try: int(i)
    except ValueError:
        return False
    return True

def is_float(f):
    try: float(f)
    except ValueError:
        return False
    return True
