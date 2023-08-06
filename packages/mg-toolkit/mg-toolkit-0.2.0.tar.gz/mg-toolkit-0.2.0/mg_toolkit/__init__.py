#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import argparse
import textwrap
import mg_toolkit

from .metadata import original_metadata  # noqa
from .search import sequence_search  # noqa

__version__ = '0.2.0'
__all__ = [
    'original_metadata',
    'sequence_search',
]


def is_file(filename):
    if not os.path.isfile(filename):
        msg = "{0} is not a directory".format(filename)
        raise argparse.ArgumentTypeError(msg)
    else:
        return filename


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Metagenomics toolkit
            --------------------''')
    )
    parser.add_argument(
        '-V', '--version', action='version', version=__version__,
        help='print version information'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='print debugging information'
    )

    subparsers = parser.add_subparsers(dest='tool')

    original_metadata_parser = subparsers.add_parser(
        'original_metadata', help='Download original metadata'
    )
    original_metadata_parser.add_argument(
        '-a', '--accession', required=True, nargs='+',
        help='provide study accession, e.g. PRJEB1787 or ERP001736'
    )

    sequence_search_parser = subparsers.add_parser(
        'sequence_search', help='Search sequence'
    )
    sequence_search_parser.add_argument(
        '-s', '--sequence', required=True, type=is_file, nargs='+',
        help='provide path to fasta file'
    )

    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARN

    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    return getattr(mg_toolkit, args.tool)(args)


if __name__ == '__main__':
    main()
