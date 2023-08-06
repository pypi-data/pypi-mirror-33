#!/usr/bin/env python3
"""
get_taxonomy_rank_with_ete3.py

Copyright (c) 2017-2018 Guanliang Meng <mengguanliang@foxmail.com>.

This file is part of MitoZ.

MitoZ is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MitoZ is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MitoZ.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import re
from ete3 import NCBITaxa


def get_rank_dict(taxa_name=None):
    ncbi = NCBITaxa()
    if re.match(r'^\d+$', taxa_name):
        # the input is NCBI taxid
        try:
            lineage_taxid_list = ncbi.get_lineage(taxa_name)
        except ValueError:
            print("the taxid {0} not found!".format(taxa_name), file=sys.stderr)
            return None
        if lineage_taxid_list is None:
            print("the taxid {0} not found!".format(taxa_name), file=sys.stderr)
            return None
    else:
        # the input is a species name or rank name
        name_dict = ncbi.get_name_translator([taxa_name])
        if not name_dict:
            ## try only the first word (which may be a genus name?)
            print("can not find taxid for", taxa_name, file=sys.stderr)
            taxa_name = taxa_name.split()
            if len(taxa_name) > 1:
                taxa_name = taxa_name[0]
                print("try to search %s instead..." % taxa_name, file=sys.stderr)
                name_dict = ncbi.get_name_translator([taxa_name])

            if not name_dict:
                print("can not find taxid for %s, maybe it's a misspelling.\n" % taxa_name , file=sys.stderr)
                return None

        lineage_taxid_list = ncbi.get_lineage(name_dict[taxa_name][0])

    rank_dict = dict()
    for rank in ['superkingdom', 'kingdom', 'superphylum', 'phylum', 'subphylum', 'superclass', 'class', 'subclass', 'superorder', 'order', 'suborder', 'superfamily', 'family', 'subfamily', 'genus', 'subgenus', 'species']:
        rank_dict[rank] = 'NA'

    for j in lineage_taxid_list:
        rank = ncbi.get_rank([j])[j]
        taxa = ncbi.get_taxid_translator([j])[j]
        #print(rank)
        if rank == 'superkingdom':
            rank_dict['superkingdom'] = taxa

        if rank == 'kingdom':
            rank_dict['kingdom'] = taxa

        elif rank == 'superphylum':
            rank_dict['superphylum'] = taxa

        elif rank == 'phylum':
            rank_dict['phylum'] = taxa

        elif rank == 'subphylum':
            rank_dict['subphylum'] = taxa

        elif rank == 'superclass':
            rank_dict['superclass'] = taxa

        elif rank == 'calss':
            rank_dict['class'] = taxa

        elif rank == 'subclass':
            rank_dict['subclass'] = taxa

        elif rank == 'superorder':
            rank_dict['superorder'] = taxa

        elif rank == 'order':
            rank_dict['order'] = taxa

        elif rank == 'suborder':
            rank_dict['suborder'] = taxa

        elif rank == 'superfamily':
            rank_dict['superfamily'] = taxa

        elif rank == 'family':
            rank_dict['family'] = taxa

        elif rank == 'subfamily':
            rank_dict['subfamily'] = taxa

        elif rank == 'genus':
            rank_dict['genus'] = taxa

        elif rank == 'subgenus':
            rank_dict['subgenus'] = taxa

        elif rank == 'species':
            rank_dict['species'] = taxa

        else:
            pass

    return rank_dict


def main():
    usage = """
python3 {0} <taxonomy_list> <outfile>

The 'taxonomy_list' file can be a list of ncbi taxa id or species names (or higher ranks, e.g. Family, Order), or a mixture of them.

""".format(sys.argv[0])

    if len(sys.argv) != 3:
        sys.exit(usage)

    taxonomy_list, outfile = sys.argv[1:3]

    ranks = ['superkingdom', 'kingdom', 'superphylum', 'phylum', 'subphylum', 'superclass', 'class', 'subclass', 'superorder', 'order', 'suborder', 'superfamily', 'family', 'subfamily', 'genus', 'subgenus', 'species']

    with open(taxonomy_list, 'r') as fh, open(outfile, 'w') as fhout:
        print('\t'.join(ranks), file=fhout)
        for taxa_name in fh:
            taxa_name = taxa_name.strip()
            if not taxa_name:
                continue

            rank_dict = get_rank_dict(taxa_name=taxa_name)

            if rank_dict is None:
                print(taxa_name, file=fhout)
                continue

            line = "\t".join([rank_dict[rank] for rank in ranks])
            print(line, file=fhout)
                

if __name__ == '__main__':
    main()