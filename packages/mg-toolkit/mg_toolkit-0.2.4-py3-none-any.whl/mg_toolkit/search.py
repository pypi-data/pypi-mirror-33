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

import logging
import requests
import html
from pandas import DataFrame

from .utils import (
    MG_SEQ_URL,
    MG_SAMPLE_URL,
    MG_RUN_URL,
)


logger = logging.getLogger(__name__)


def sequence_search(args):

    """
    Process given fasta file
    """
    database = args.database
    for s in args.sequence:
        with open(s) as f:
            sequence = f.read()
            logger.debug("Sequence %s" % sequence)
            seq = SequenceSearch(sequence, database=database)
            seq.save_to_csv(seq.fetch_results())


class SequenceSearch(object):

    """
    Helper tool allowing to download original metadata for the given accession.
    """

    sequence = None
    database = "full"

    def __init__(self, sequence, *args, **kwargs):
        self.sequence = sequence
        self.database = kwargs.get("database", "full")

    def analyse_sequence(self):
        data = {
            "seqdb": self.database,
            "seq": self.sequence,
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        logger.debug(data)
        return requests.post(MG_SEQ_URL, data=data, headers=headers).json()

    def get_sample_metadata(self, accession):
        if accession is None:
            return None
        headers = {
            'Accept': 'application/vnd.api+json',
        }
        r = requests.get(
            MG_SAMPLE_URL.format(**{'accession': accession}),
            headers=headers
        )

        if r.status_code != requests.codes.ok:
            r = requests.get(
                MG_RUN_URL.format(**{'accession': accession}),
                headers=headers
            )

        r = r.json()
        _meta = {}
        try:
            metadata = r['data']['attributes']['sample-metadata']
            logger.debug(metadata)
        except KeyError:
            try:
                metadata = \
                    r['included'][0]['attributes']['sample-metadata']
                logger.debug(metadata)
            except KeyError:
                return _meta
        for m in metadata:
            unit = html.unescape(m['unit']) if m['unit'] else ""
            _meta[m['key'].replace(" ", "_")] = "{value} {unit}".format(value=m['value'], unit=unit)  # noqa

        return _meta

    def fetch_results(self):
        csv_rows = dict()
        for h in self.analyse_sequence()['results']['hits']:
            acc2 = h.get('acc2', None)
            if acc2 is not None:
                for accession in acc2.split(","):
                    accession = accession.strip("...")
                    logger.debug("Accession %s" % accession)
                    uuid = "{n} {a}".format(
                        **{'n': h['name'], 'a': accession})
                    csv_rows[uuid] = dict()
                    csv_rows[uuid]['accessions'] = accession
                    csv_rows[uuid]['kg'] = h.get('kg', '')
                    csv_rows[uuid]['taxid'] = h.get('taxid', '')
                    csv_rows[uuid]['name'] = h.get('name', '')
                    csv_rows[uuid]['desc'] = h.get('desc', '')
                    csv_rows[uuid]['pvalue'] = h.get('pvalue', '')
                    csv_rows[uuid]['species'] = h.get('species', '')
                    csv_rows[uuid]['score'] = h.get('score', '')
                    csv_rows[uuid]['evalue'] = h.get('evalue', '')
                    csv_rows[uuid]['nreported'] = h.get('nreported', '')
                    csv_rows[uuid]['uniprot'] = ",".join(
                        [i[0] for i in h.get('uniprot_link', [])])

                    _meta = self.get_sample_metadata(accession=accession)
                    csv_rows[uuid].update(_meta)
        return csv_rows

    def save_to_csv(self, csv_rows, filename=None):
        df = DataFrame(csv_rows).T
        df.index.name = 'name'
        if filename is None:
            filename = "{}.csv".format('search_metadata')
        df.to_csv(filename)
