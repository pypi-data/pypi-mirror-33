#!/usr/bin/env python
# crate_anon/anonymise/test_anonymisation.py

"""
===============================================================================

    Copyright (C) 2015-2018 Rudolf Cardinal (rudolf@pobox.com).

    This file is part of CRATE.

    CRATE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CRATE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CRATE. If not, see <http://www.gnu.org/licenses/>.

===============================================================================

Test the anonymisation for specific databases.

From the output, we have:
    n_replacements (POSITIVE)
    word_count (N)
    true_positive_confidential_masked (TP)
    false_positive_banal_masked (FP)
    false_negative_confidential_visible_known_to_source (FN)
    confidential_visible_but_unknown_to_source

Therefore, having summed across documents:
    TP + FP = POSITIVE
    NEGATIVE = N - POSITIVE
    TN = NEGATIVE - FN

and then we have everything we need. For all identifiers, we make FN equal to
    false_negative_confidential_visible_known_to_source
        + not_false_negative_confidential_visible_but_unknown_to_source
instead.
"""

# =============================================================================
# Imports
# =============================================================================

# from __future__ import print_function
import argparse
import collections
import csv
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from cardinal_pythonlib.fileops import mkdir_p
from cardinal_pythonlib.logs import configure_logger_for_colour

from crate_anon.anonymise.config_singleton import config
from crate_anon.anonymise.patient import Patient

log = logging.getLogger(__name__)


# =============================================================================
# Specific tests
# =============================================================================

class FieldInfo(object):
    def __init__(self, table: str, field: str) -> None:
        """
        Fetches useful subsets from the data dictionary.
        """
        ddrows = config.dd.get_rows_for_dest_table(table)
        if not ddrows:
            raise ValueError("No data dictionary rows for destination table "
                             "{}".format(table))
        try:
            textrow = next(x for x in ddrows if x.dest_field == field)
        except StopIteration:
            raise ValueError("No destination field: {}".format(field))
        try:
            pkrow = next(x for x in ddrows if x.pk)
        except StopIteration:
            raise ValueError("No PK field found")
        try:
            pidrow = next(x for x in ddrows if x.primary_pid)
        except StopIteration:
            raise ValueError("No PID field found")

        self.pk_ddrow = pkrow
        self.pid_ddrow = pidrow
        self.text_ddrow = textrow
        log.info("Using fields: pk={}, pid={}, text={}".format(
            self.pk_ddrow.get_dest_signature(),
            self.pid_ddrow.get_dest_signature(),
            self.text_ddrow.get_dest_signature()))


def get_patientnum_rawtext(docid: int,
                           fieldinfo: FieldInfo) -> Tuple[Optional[int],
                                                          Optional[str]]:
    """
    Fetches the original text for a given document PK, plus the associated
    patient ID.
    """
    db = config.sources[fieldinfo.text_ddrow.src_db]
    table = fieldinfo.text_ddrow.src_table
    textfield = fieldinfo.text_ddrow.src_field
    sourcedbname = fieldinfo.text_ddrow.src_db
    pidfield = fieldinfo.pid_ddrow.src_field
    pkfield = fieldinfo.pk_ddrow.src_field
    src_ddrows = config.dd.get_rows_for_src_table(sourcedbname, table)
    sourcefields = []
    idx_pidfield = None
    idx_textfield = None
    for i, ddr in enumerate(src_ddrows):
        sourcefields.append(ddr.src_field)
        if ddr.src_field == pidfield:
            idx_pidfield = i
        if ddr.src_field == textfield:
            idx_textfield = i
    if idx_pidfield is None:
        raise ValueError("Unknown idx_pidfield")
    if idx_textfield is None:
        raise ValueError("Unknown idx_textfield")
    query = """
        SELECT {fields}
        FROM {table}
        WHERE {pkfield} = ?
    """.format(
        fields=",".join(sourcefields),
        textfield=textfield,
        table=table,
        pkfield=pkfield,
    )
    # log.debug("RAW: {}, {}".format(query, docid))
    row = db.fetchone(query, docid)
    if not row:
        return None, None
    pid = row[idx_pidfield]
    text = row[idx_textfield]
    ddr = src_ddrows[idx_textfield]
    for altermethod in fieldinfo.text_ddrow.get_extracting_text_altermethods():
        text, _ = altermethod.alter(config, text, ddr, row, src_ddrows)
    return pid, text


def get_patientnum_anontext(docid: int,
                            fieldinfo: FieldInfo) -> Tuple[Optional[int],
                                                           Optional[str]]:
    """
    Fetches the anonymised text for a given document PK, plus the associated
    patient ID.
    """
    db = config.destdb
    table = fieldinfo.text_ddrow.dest_table
    textfield = fieldinfo.text_ddrow.dest_field
    pidfield = fieldinfo.pid_ddrow.dest_field
    pkfield = fieldinfo.pk_ddrow.dest_field
    query = """
        SELECT {pidfield}, {textfield}
        FROM {table}
        WHERE {pkfield} = ?
    """.format(
        pidfield=pidfield,
        textfield=textfield,
        table=table,
        pkfield=pkfield,
    )
    # log.debug("ANON: {}, {}".format(query, docid))
    result = db.fetchone(query, docid)
    if not result:
        return None, None
    pid, text = result
    return pid, text


def process_doc(docid: int,
                args: Any,
                fieldinfo: FieldInfo,
                csvwriter: Any,
                first: bool,
                scrubdict: Dict[int, Dict[str, Any]]) -> int:
    """
    Write the original and anonymised documents to disk, plus some
    counts to a CSV file.
    """
    # Get stuff
    patientnum, rawtext = get_patientnum_rawtext(docid, fieldinfo)
    patientnum2, anontext = get_patientnum_anontext(docid, fieldinfo)
    # patientnum is raw; patientnum2 is hashed

    # Get scrubbing info
    patient = Patient(patientnum)
    scrubber = patient.scrubber
    scrubdict[patientnum] = scrubber.get_raw_info()

    # Write text
    rawfilename = os.path.join(args.rawdir,
                               "{}_{}.txt".format(patientnum, docid))
    anonfilename = os.path.join(args.anondir,
                                "{}_{}.txt".format(patientnum, docid))
    with open(rawfilename, 'w') as f:
        if rawtext:
            f.write(rawtext)
    with open(anonfilename, 'w') as f:
        if anontext:
            f.write(anontext)

    wordcount = len(rawtext.split()) if rawtext else 0

    if anontext:
        n_patient = anontext.count(config.replace_patient_info_with)
        n_thirdparty = anontext.count(config.replace_third_party_info_with)
        n_nonspecific = anontext.count(config.replace_nonspecific_info_with)
    else:
        n_patient = 0
        n_thirdparty = 0
        n_nonspecific = 0
    n_replacements = n_patient + n_thirdparty + n_nonspecific

    summary = collections.OrderedDict()
    summary["src_db"] = fieldinfo.text_ddrow.src_db
    summary["src_table"] = fieldinfo.text_ddrow.src_table
    summary["src_field_pid"] = fieldinfo.pid_ddrow.src_field
    summary["pid"] = patientnum
    summary["src_field_pk"] = fieldinfo.pk_ddrow.src_field
    summary["docid"] = docid
    summary["src_field_text"] = fieldinfo.text_ddrow.src_field
    summary["dest_table"] = fieldinfo.text_ddrow.dest_table
    summary["dest_field"] = fieldinfo.text_ddrow.dest_field
    summary["n_replacements"] = n_replacements
    # summary["n_patient"] = n_patient
    # summary["n_thirdparty"] = n_thirdparty
    # summary["n_nonspecific"] = n_nonspecific
    summary["word_count"] = wordcount
    # ... use this to calculate true negatives (banal, visible) as:
    # true_negative = word_count - (true_pos + false_pos + false_neg)
    summary["true_positive_confidential_masked"] = "?"
    summary["false_positive_banal_masked"] = "?"
    summary["false_negative_confidential_visible_known_to_source"] = "?"
    summary["confidential_visible_but_unknown_to_source"] = "?"
    summary["comments"] = ""

    if first:
        csvwriter.writerow(list(summary.keys()))
    csvwriter.writerow(list(summary.values()))

    return patientnum


def get_docids(args: Any,
               fieldinfo: FieldInfo,
               from_src: bool = True) -> List[int]:
    """
    Generate a limited set of PKs for the documents.
    """
    if from_src:
        db = config.sources[fieldinfo.text_ddrow.src_db]
        table = fieldinfo.pk_ddrow.src_table
        pkfield = fieldinfo.pk_ddrow.src_field
        pidfield = fieldinfo.pid_ddrow.src_field
    else:
        db = config.destdb
        table = fieldinfo.pk_ddrow.dest_table
        pkfield = fieldinfo.pk_ddrow.dest_field
        pidfield = fieldinfo.pid_ddrow.dest_field
    if args.uniquepatients:
        query = """
            SELECT MIN({pkfield}), {pidfield}
            FROM {table}
            GROUP BY {pidfield}
            ORDER BY {pidfield}
            LIMIT {limit}
        """.format(
            pkfield=pkfield,
            pidfield=pidfield,
            table=table,
            limit=args.limit,
        )
        return db.fetchallfirstvalues(query)
    else:
        query = """
            SELECT {pkfield}
            FROM {table}
            ORDER BY {pkfield}
            LIMIT {limit}
        """.format(
            pkfield=pkfield,
            table=table,
            limit=args.limit,
        )
        return db.fetchallfirstvalues(query)


def test_anon(args: Any) -> None:
    """
    Fetch raw and anonymised documents and store them in files for
    comparison, along with some summary information.
    """
    fieldinfo = FieldInfo(args.dsttable, args.dstfield)
    docids = get_docids(args, fieldinfo, args.from_src)
    mkdir_p(args.rawdir)
    mkdir_p(args.anondir)
    scrubdict = {}
    pidset = set()
    with open(args.resultsfile, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='\t')
        first = True
        for docid in docids:
            # noinspection PyTypeChecker
            pid = process_doc(docid, args, fieldinfo, csvwriter, first,
                              scrubdict)
            first = False
            pidset.add(pid)
    with open(args.scrubfile, 'w') as f:
        f.write(json.dumps(scrubdict, indent=4))
    log.info("Finished. See {} for a summary.".format(args.resultsfile))
    log.info(
        "Use meld to compare directories {} and {}".format(
            args.rawdir,
            args.anondir,
        )
    )
    log.info("To install meld on Debian/Ubuntu: sudo apt-get install meld")
    log.info("{} documents, {} patients".format(len(docids), len(pidset)))


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    """
    Command-line entry point.
    """
    parser = argparse.ArgumentParser(
        description='Test anonymisation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', required=True,
                        help='Configuration file name (input)')
    parser.add_argument('--dsttable', required=True,
                        help='Destination table')
    parser.add_argument('--dstfield', required=True,
                        help='Destination column')
    parser.add_argument('--limit', type=int, default=100,
                        help='Limit on number of documents')
    parser.add_argument('--rawdir', default='raw',
                        help='Directory for raw output text files')
    parser.add_argument('--anondir', default='anon',
                        help='Directory for anonymised output text files')
    parser.add_argument('--resultsfile', default='testanon_results.csv',
                        help='Results output CSV file name')
    parser.add_argument('--scrubfile', default='testanon_scrubber.txt',
                        help='Scrubbing information text file name')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Be verbose")

    pkgroup = parser.add_mutually_exclusive_group(required=False)
    pkgroup.add_argument('--pkfromsrc', dest='from_src', action='store_true',
                         help='Fetch PKs (document IDs) from source (default)')
    pkgroup.add_argument('--pkfromdest', dest='from_src', action='store_false',
                         help='Fetch PKs (document IDs) from destination')
    parser.set_defaults(from_src=True)

    uniquegroup = parser.add_mutually_exclusive_group(required=False)
    uniquegroup.add_argument(
        '--uniquepatients', dest='uniquepatients', action='store_true',
        help='Only one document per patient (the first by PK) (default)')
    uniquegroup.add_argument(
        '--nonuniquepatients', dest='uniquepatients', action='store_false',
        help='Documents in sequence, with potentially >1 document/patient')
    parser.set_defaults(uniquepatients=True)

    args = parser.parse_args()

    loglevel = logging.DEBUG if args.verbose else logging.INFO
    rootlogger = logging.getLogger()
    configure_logger_for_colour(rootlogger, loglevel)

    log.info("Arguments: " + str(args))

    # Load/validate config
    log.info("Loading config...")
    config.set(filename=args.config, load_destfields=False)
    log.info("... config loaded")

    # Do it
    test_anon(args)


if __name__ == '__main__':
    main()
