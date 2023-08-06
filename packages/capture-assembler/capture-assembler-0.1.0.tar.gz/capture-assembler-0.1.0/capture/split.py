#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
import logging

from Bio import SeqIO
from capture import bam
from capture import parse


def split(
        genome_size, mean_size, output,
        file, type_f, subsample,
        wanted_cov=100
        ):
    """ calcul the number of reads needed in each subsample then
        parse the file and make the subsample
    """
    logger = logging.getLogger(__name__)
    # caclul the number of reads in each subsample for a coverage
    number_records = int((wanted_cov * genome_size) // mean_size)
    # the subsampling is the same for fastq gzip and not gzip
    # as we can have more than one file, we use the name for subsample

    if subsample == 0:
        if type_f == "bam":
            tot_records = bam.count_bam(file)
            num_sub = tot_records // number_records
            parse.parse_bam(output, file, type_f, num_sub, number_records)
            return num_sub

        else:
            tot_records = parse.count_record(file)
            num_sub = tot_records // number_records
            if parse.is_gzip(file):
                with gzip.open(file, "rt") as handle:
                    parse.parse_fq(
                        output, file, type_f, num_sub, number_records,
                        handle
                        )

            else:
                with open(file, "rt") as handle:  # can we do like that?
                    parse.parse_fq(
                        output, file, type_f, num_sub, number_records,
                        handle
                        )

            return num_sub

    else:
        num_sub = int(subsample)
        if type_f == "bam":
            tot_records = bam.count_bam(file)
            if float((number_records / tot_records)) >= float(1):
                logger.error(
                    "Invalid Genome and Mean Size parameter. Aborting"
                    )
                sys.exit(1)
            fraction = str((number_records / tot_records)).split(".")[1][:4]
            parse.parse_bam_rnd(
                            output, file, type_f, num_sub, fraction,
                            )
            return num_sub

        else:
            tot_records = parse.count_record(file)
            if parse.is_gzip(file):
                with gzip.open(file, "rt") as handle:
                    parse.parse_fq_rnd(
                                    output, file, type_f,
                                    num_sub, number_records,
                                    handle, tot_records,
                                    )

            else:
                with open(file, "rt") as handle:  # can we do like that?
                    parse.parse_fq_rnd(
                                    output, file, type_f,
                                    num_sub, number_records,
                                    handle
                                    )

            return num_sub
