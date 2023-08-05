#!/usr/bin/env python2
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
from builtins import range, zip

import json
import numpy as np
import sys

"""
18cd442ee1fa03df74517335ed2ed92d:a0f380a52e792f65b96c41ad5fdfd8e8   chr1,-0.091218  chr10,-0.120059 chr11,-0.085029 chr12,0.962397  chr13,0.038357  chr14,0.908901  chr15,-0.060206 chr16,-0.109638 chr17,-0.091413 chr18,0.03692chr19,-0.113141    chr2,0.999374   chr3,-0.076656  chr4,-0.194520  chr5,-0.087904  chr6,0.821275   chr7,-0.099522  chr8,-0.004072  chr9,0.997895   chrX,0.172631   chrY,0.712472
"""

class InputFile(object):
    def __init__(self, file_path):
        self.nameset = set()
        self.files = []
        self.parse_file(file_path)

    def parse_file(self, file_path):
        try:
            with open(file_path) as list_file:
                for line in list_file:
                    line = line.strip()
                    if line:
                        if line not in self.nameset:
                            self.nameset.add(line)
                            self.files.append(line)
        except IOError:
            pass

    def __getitem__(self, index):
        return self.files[index]


class Matrix(object):
    def __init__(self, labels):
        self.index = dict(zip(labels, range(len(labels))))
        self.labels = labels
        self.size = len(labels)
        self.matrix = np.zeros((self.size, self.size))

    def __getitem__(self, labels):
        x_label, y_label = labels
        x = self.index.get(x_label)
        y = self.index.get(y_label)
        return self.matrix[x, y]

    def __setitem__(self, labels, value):
        x_label, y_label = labels
        x = self.index.get(x_label)
        y = self.index.get(y_label)
        self.matrix[x, y] = value
        self.matrix[y, x] = value

    def convert_labels(self, meta):
        for i in range(len(self.labels)):
            token = meta.get("datasets", {}).get(self.labels[i], {})
            if token:
                self.labels[i] = "{0}".format(token.get("file_name", ""))


    def __str__(self):
        s = ""
        s += '\t' + '\t'.join(self.labels) + '\n'
        for i in range(self.size):
            s += self.labels[i] + '\t' + '\t'.join(["{0:.4f}".format(v) for v in self.matrix[i]]) + '\n'
        return s

     
class CorrFileParser(object):
    def __init__(self, corr_file_path):
        self.path = corr_file_path

    def make_matrix(self, labels):
        matrix = Matrix(labels)
        try:
            with open(self.path) as corr_file:
                header = corr_file.readline()
                header = header.strip().split()
                weights = {}
                for chrom in header:
                    chrom = chrom.split(":")
                    weights[chrom[0]] = float(chrom[1])
                for line in corr_file:
                    line = line.split()
                    file1, file2 = line[0].split(':')
                    average = weighted_average(line[1:], weights)
                    matrix[file1, file2] = average
        except IOError:
            pass
        return matrix

def weighted_average(line, weights):
    w_sum = 0.0
    total = 0.0
    for element in line:
        chrom, value = element.split(',')
        total += weights[chrom]
        w_sum += float(value) * weights[chrom]
    return w_sum / total

def main(list_path, corr_path, output_path, meta = {}):

    input_file = InputFile(list_path)
    matrix = CorrFileParser(corr_path).make_matrix(input_file.files)
    matrix.convert_labels(meta)
    with open(output_path, 'w') as output_file:
        output_file.write(str(matrix))

def listjson2dictjson(old_json):
    new_json = {"datasets":{}}
    for token in old_json.get("datasets", []):
        new_json["datasets"][token["md5sum"]] = token
    return new_json

if __name__ == '__main__':
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("usage: python make_matrix.py {list_path} {corr_path} {output_path}")
        exit()
    LIST_PATH = sys.argv[1]
    CORR_PATH = sys.argv[2]
    OUTPUT_PATH = sys.argv[3]
    if len(sys.argv) == 4:
        META = {}
    elif len(sys.argv) == 5:
        META = listjson2dictjson(json.load(open(sys.argv[4])))
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
