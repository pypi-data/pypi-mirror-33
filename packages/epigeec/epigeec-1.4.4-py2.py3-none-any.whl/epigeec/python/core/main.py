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

import os
import os.path
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import input_parser
import config

os.environ['LD_LIBRARY_PATH'] = config.LIB_DIR

def main(argv):
    args = input_parser.parse_args(argv)
    args.func(args)

def cli():
    main(sys.argv[1:])

if __name__ == "__main__":
     cli()
