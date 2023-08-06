#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pysam
import logging

from Bio import SeqIO
from capture import parse


def test_is_gzip():
    gzipped = "data/20_reads_R1.fastq.gz"
    not_gzipped = "data/20_reads_R1.fastq"
    assert parse.is_gzip(gzipped) is True
    assert parse.is_gzip(not_gzipped) is False


def test_count_record():
    count = parse.count_record("data/20_reads_R1.fastq.gz")
    assert count == 20


def test_parse_fq():
    logger = logging.getLogger(__name__)
    output = "testing_fq"
    os.makedirs(output)
    file = "data/20_reads_R1.fastq"
    type_f = "forward"
    num_sub = 2
    number_records = 7
    with open(file, "rt") as handle:
        parse.parse_fq(output, file, type_f, num_sub, number_records, handle)
    subfile = f"{output}/subsample_{type_f}1.fastq"
    with open(subfile, "rt") as handle:
            file_record = SeqIO.parse(handle, "fastq")
            tot_records = sum(1 for line in file_record)
            assert tot_records == 7
    with open(f"{output}/subsample_extra.fastq", "rt") as handle:
            file_record = SeqIO.parse(handle, "fastq")
            tot_records = sum(1 for line in file_record)
            assert tot_records == 6
    # try:
    #     os.remove(f"{output}/subsample_{type_f}1.fastq")
    #     os.remove(f"{output}/subsample_{type_f}2.fastq")
    #     os.remove(f"{output}/subsample_extra.fastq")
    #     os.rmdir(output)
    # except OSError as e:
    #     logger.error("Couldn't remove the testing_fq. Exiting")
    #     sys.exit(1)


def test_parse_bam():
    logger = logging.getLogger(__name__)
    output = "testing_bam"
    os.makedirs(output)
    file = "data/20_reads.bam"
    type_f = "bam"
    num_sub = 2
    number_records = 7
    parse.parse_bam(output, file, type_f, num_sub, number_records)
    subfile = f"{output}/subsample_1.bam"
    number_records_subfile = int(pysam.view("-c", subfile))
    assert number_records_subfile == 7
    extra = f"{output}/subsample_extra.bam"
    number_records_extra = int(pysam.view("-c", extra))
    assert number_records_extra == 6
    # try:
    #     os.remove(f"{output}/subsample_1.bam")
    #     os.remove(f"{output}/subsample_1.bam.bai")
    #     os.remove(f"{output}/subsample_2.bam")
    #     os.remove(f"{output}/subsample_extra.bam")
    #     os.remove(f"{output}/subsample_extra.bam.bai")
    #     os.rmdir(output)
    # except OSError as e:
    #     logger.error("Couldn't remove the testing_bam. Exiting")
    #     sys.exit(1)
