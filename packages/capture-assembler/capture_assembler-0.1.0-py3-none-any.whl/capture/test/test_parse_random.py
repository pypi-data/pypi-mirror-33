#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import pysam
import logging
import itertools

from Bio import SeqIO
from capture import parse


def test_parse_bam_rnd():
    logger = logging.getLogger(__name__)
    output = "testing_bam_rnd"
    os.makedirs(output)
    file = "data/20_reads.bam"
    type_f = "bam"
    num_sub = 2
    fraction = 8  # 45% of our sample will go in our subsample
    parse.parse_bam_rnd(output, file, type_f, num_sub, fraction)
    subfile = f"{output}/subsample_1.bam"
    pysam.index(subfile)
    file_record = pysam.AlignmentFile(subfile, "rb")
    counter = 0
    for record in file_record.fetch():
        counter += 1
    assert counter == 16
    file_record.close()


def test_reservoir():
    logger = logging.getLogger(__name__)
    output = "testing_reservoir"
    os.makedirs(output)
    total_record = 20
    file = "data/20_reads_R1.fastq"
    wanted_record = 17
    with open(file, "rt") as handle:
        file_record = SeqIO.parse(handle, "fastq")
        record_gen = parse.reservoir(total_record, wanted_record, file_record)
        subsample = itertools.islice(record_gen, 17)
        SeqIO.write(subsample,
                    f"{output}/reservoir.fastq",
                    "fastq"
                    )
    testfile = f"{output}/reservoir.fastq"
    with open(testfile, "rt") as handle:
        file_record = SeqIO.parse(handle, "fastq")
        tot_records = sum(1 for line in file_record)
        assert tot_records == 17


def test_parse_fq_rnd():
    logger = logging.getLogger(__name__)
    output = "testing_fq_rnd"
    os.makedirs(output)
    file = "data/20_reads_R1.fastq"
    type_f = "forward"
    tot_records = 20
    num_sub = 2
    number_records = 5
    with open(file, "rt") as handle:
        parse.parse_fq_rnd(
                            output, file, type_f, num_sub,
                            number_records, handle, tot_records
                            )
    subfile = f"{output}/subsample_{type_f}1.fastq"
    with open(subfile, "rt") as handle:
        file_record = SeqIO.parse(handle, "fastq")
        tot_records = sum(1 for line in file_record)
        assert tot_records == 5
        number_files = len(glob.glob(f"{output}/*.fastq"))
        print(number_files)
        assert number_files == 2
