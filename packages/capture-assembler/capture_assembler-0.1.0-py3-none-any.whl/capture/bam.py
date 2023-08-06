#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pysam


def count_bam(file):
    """ count the number of reads present in the file
        bam_file = pysam.AlignmentFile(file, "rb")
        Needs the bam file and bam index file to work
    """
    # map_seq = 0
    # unmap_seq = 0
    # # use the idxstats command of samtools to get the number of reads
    # for l in pysam.idxstats(file).split("\n")[:-1]:
    #     map_seq += int(l.split()[2])
    #     unmap_seq += int(l.split()[3])
    tot_records = int(pysam.view("-c", file))
    # there's a other way to do that (add on end list)
    # tot_records = map_seq + unmap_seq
    return(tot_records)


def write(reads, output, c_sub, file_record):
    """ Will be add if need of only paired reads in bam
        if args.paired:
            for read in reads:
                if read.is_paired:
                    pairedreads.write(read)
                pairedreads.close()
        else:
    """
    allreads = pysam.AlignmentFile(
        f"{output}/subsample_{c_sub}.bam",
        "wb",
        template=file_record)
    for read in reads:
        allreads.write(read)
    allreads.close()
