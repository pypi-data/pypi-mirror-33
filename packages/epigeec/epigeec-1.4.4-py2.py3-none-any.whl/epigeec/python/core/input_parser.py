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

import launcher
import config

def parse_args(args):
    parser = argparse.ArgumentParser(prog='epiGeEC', description = "EpiGeEC - Tools for fast NxN correlation of deep sequencing signal data")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(config.VERSION))
    subparsers = parser.add_subparsers(help = "Sub-command help.")

    parser_hdf5 = subparsers.add_parser("to_hdf5", description="Average the singla in non-overlapping bins." ,help="Convert a signal file format to a more efficient hdf5 format for use with other epiGeEC tools.")
    parser_hdf5.set_defaults(func=launcher.to_hdf5)
    group = parser_hdf5.add_mutually_exclusive_group(required=True)
    group.add_argument("-bw", "--bigwig", action='store_true', help="Indicate that the signal file is in bigWig format.")
    group.add_argument("-bg", "--bedgraph", action='store_true', help="Indicate that the signal file is in bedGraph format.")
    parser_hdf5.add_argument("signalFile", help="The signal file, bigWig or bedGraph. (TEXT)")
    parser_hdf5.add_argument("chromSizes", help="Chromosome sizes of the assembly, chromosomes not in this file are ignored. (TEXT)")
    parser_hdf5.add_argument("resolution", type=int, help="The resolution of the binning in base pair (1kb suggested for human). (INTEGER)")
    parser_hdf5.add_argument("outHdf5", help="The output file. (TEXT)")

    parser_filter = subparsers.add_parser("filter", description="Select or remove bins of a HDF5 file." ,help="Select regions to be kept or removed from a HDF5 file (this step is optional).")
    parser_filter.set_defaults(func=launcher.hdf5_filter)
    parser_filter.add_argument("hdf5", help="The HDF5 file to be filtered. (TEXT)")
    parser_filter.add_argument("chromSizes", help="Chromosome sizes of the assembly, chromosomes not in this file are ignored. (TEXT)")
    parser_filter.add_argument("outHdf5", help="The output file. (TEXT)")
    parser_filter.add_argument("--select", "-s", help="The file in BED format containing the regions to select, others are ignored. In case a region is both selected and excluded, the exclusion dominates. (TEXT)")
    parser_filter.add_argument("--exclude", "-e", help="The file in BED format containing the regions to exclude.")

    parser_corr = subparsers.add_parser("correlate", description="Compute a Pearson correlation coefficient for each pair of hdf5 from a list.", help="Perform N by N Pearson correlation of HDF5 files generated with the same chrom sizes, filters and resolution.")
    parser_corr.set_defaults(func=launcher.corr)
    parser_corr.add_argument('--concat', '-c', dest="single_chrom", action='store_true', help="Use to correlate all chromosomes as if they were one single large chromosome")
    parser_corr.add_argument("hdf5List", help="The list of HDF5 files to correlate, one file per line. (TEXT)")
    parser_corr.add_argument("chromSizes", help="Chromosome sizes of the assembly, chromosomes not in this file are ignored. (TEXT)")
    parser_corr.add_argument("outMatrix", help="The final tab-delimited matrix file. (TEXT)")
    parser_corr.add_argument('--desc', type=str, default="")
    
    return parser.parse_args(args)