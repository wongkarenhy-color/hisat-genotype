#!/usr/bin/env python
#
# Copyright 2019, Christopher Bennett <christopher@bennett-tech.dev>
#
# This file is part of HISAT-genotype.
#
# HISAT-genotype is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HISAT-genotype is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HISAT-genotype.  If not, see <http://www.gnu.org/licenses/>.
#

import os, sys, glob
from argparse import ArgumentParser
import hisatgenotype_typing_common as typing_common
import hisatgenotype_args as hg_args

def flatten(tree, prev_key = '', sep = '*'):
    items = []
    for key, value in tree.items():
        new_key = prev_key + sep + key if prev_key else key
        try:
            items.extend(flatten(value['children'], new_key, ':').items())
            items.append((new_key + ' - Frag', value['score']))
        except:
            items.append((new_key, value['score']))

    if sep == ":":
        return dict(items)
    else:
        return sorted(items, key=lambda tup : (tup[1], len(tup[0].split()[0])), reverse = True)

if __name__ == '__main__':
    parser = ArgumentParser(
        description='Script for simplifying HISAT-genotype results')

    hg_args.args_input_output(parser)
    args = parser.parse_args()

    if args.read_dir:
        indir = args.read_dir
    else:
        indir = '.'

    reports = glob.glob('%s/*.report' % indir)

    report_results = {}
    for report in reports:
        report_results[report] = typing_common.call_nuance_results(report)

    scores = []
    for file_ in report_results:
        print('File: %s' % file_)

        for type_ in report_results[file_]:
            print("\tAnalysis - %s" % type_)
            if type_ == 'Allele splitting':
                tree = report_results[file_]['Allele splitting']
                for gene in tree:
                    print('\t\tGene: %s (score: %.2f)' % (gene, tree[gene]['score']))
                    
                    flattened_tree = flatten(tree[gene]['children'], gene)
                    pastv, pastn = 0, ''
                    for tup in flattened_tree:
                        if tup[1] < 0.2 or (pastv == tup[1] and "Frag" in tup[0]):
                            continue
                        print('\t\t\t%s (score: %.4f)' % (tup[0], tup[1]))
                        pastn, pastv = tup

            else:
                for gene, data in report_results[file_][type_].items():
                    print('\t\tGene: %s' % gene)
                    if isinstance(data, list):
                        for line in data:
                            print('\t\t\t%s' % line)
                    else:
                        print('\t\t\t%s' % data)

                