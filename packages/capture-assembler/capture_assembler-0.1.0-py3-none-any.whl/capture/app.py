#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import logging
import argparse
import random as rnd

from capture import run
from capture import join
from capture import clean
from capture import split
from capture.version import __version__


def assemble(args):
    """
    main function for the capture software

    Arguments:
    args (object): the argument dictionary from argparse
    """
    logger = logging.getLogger(__name__)
    genome_size = args.genome_size
    mean_size = args.mean
    output = args.output
    mem = args.memory
    thread = args.thread
    subsample = args.subsample
    try:
        os.makedirs(args.output)
        output_temp = args.output + "/temp"
        os.makedirs(output_temp)
        if args.forward and args.reverse:
            rnd.seed(1)
            type_f = "forward"
            num_sub = split.split(
                genome_size, mean_size, output_temp,
                args.forward, type_f, subsample
                )
            type_f = "reverse"
            num_sub = split.split(
                genome_size, mean_size, output_temp,
                args.reverse, type_f, subsample
                )
            type_r = "pe"
            run.spades(num_sub, output_temp, type_r, mem, thread)
            if args.clean is True:
                clean.clean_spades(output, num_sub)
            join.contig(num_sub, output)
            run.canu(output, mem, thread, genome_size)
        elif args.uniq:
            type_f = "uniq"
            num_sub = split.split(
                genome_size, mean_size, output_temp,
                args.uniq, type_f, subsample
                )
            type_r = "uniq"
            run.spades(num_sub, output_temp, type_r, mem, thread)
            if args.clean is True:
                clean.clean_spades(output, num_sub)
            join.contig(num_sub, output)
            run.canu(output, mem, thread, genome_size)
        elif args.bam:
            type_f = "bam"
            num_sub = split.split(
                genome_size, mean_size, output_temp,
                args.bam, type_f, subsample
                )
            type_r = "bam"
            run.spades(num_sub, output_temp, type_r, mem, thread)
            if args.clean is True:
                clean.clean_spades(output, num_sub)
            join.contig(num_sub, output)
            run.canu(output, mem, thread, genome_size)
        else:
            logger.error("Invalid combination of input files. Aborting")
            sys.exit(1)
    except OSError as e:
        logger.error(f"{args.output} already exists. Aborting.")
        sys.exit(1)
    else:
        pass


def main():
    parser = argparse.ArgumentParser(
        prog="capture",
        usage="capture [arguments]",
        description="the capture-seq assembler"
    )
    file_group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="print version and exit"
    )
    file_group.add_argument(
        "-u",
        "--uniq",
        help="Input reads file in format fastq fastq.gz",
        type=str
    )
    file_group.add_argument(
        "-f",
        "--forward",
        help="Input forward file in format fastq fastq.gz",
        type=str
    )
    parser.add_argument(
        "-r",
        "--reverse",
        help="Input reverse file in format fastq fastq.gz",
        type=str
    )
    file_group.add_argument(
        "-b",
        "--bam",
        help="""Input the reads file in bam format.
        It will be considerate as Ion Torrent data in Spades"""
    )
    parser.add_argument(
        "-g",
        "--genome_size",
        help="The size of the genome specific to your reads in numeric value",
        type=int
    )
    parser.add_argument(
        "-m",
        "--mean",
        help="The mean size of the reads present in the input file",
        type=float
    )
    parser.add_argument(
        "-o",
        "--output",
        help="The output directory"
    )
    parser.add_argument(
        "-s",
        "--subsample",
        default=0,
        help="The number of subsample to produce. Default: the maximum",
        type=int
    )
    parser.add_argument(
        "-t",
        "--thread",
        default=4,
        help="The number of threads available. Default: 4",
        type=int
    )
    parser.add_argument(
        "-M",
        "--memory",
        default=16,
        help="The memory available in Gigs. Default: 16G",
        type=int
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_false",
        default=True,  # Normaly True but while testing it stays False
        help="Clean the temporary files. Default: True"
    )
    parser.set_defaults(func=assemble)
    args = parser.parse_args()

    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        if args.version:
            logger.info(f"capture version {__version__}")
            sys.exit(0)
        args.func(args)
    except AttributeError as e:
        logger.debug(e)
        parser.print_help()
        raise
