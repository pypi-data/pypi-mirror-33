#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

from Bio import SeqIO
from capture import join


def test_contig():
    output = "testing_join_contigs"
    output_temp = output + "/temp"
    output_spades_contig = output + "/spades_contigs"
    os.makedirs(output)
    os.makedirs(output_temp)
    os.makedirs(output_spades_contig)
    num_sub = 3
    c = 1
    while c <= num_sub:
        shutil.copy(
            f"data/contigs_test_{c}.fasta",
            f"{output_spades_contig}/contig_subsample_{c}.fasta"
            )
        c += 1
    join.contig(num_sub, output)
    fasta_sequences = SeqIO.parse(
        open(f"{output_temp}/all_contigs.fasta"),
        "fasta"
        )
    number_seq = 0
    for fasta in fasta_sequences:
        number_seq += 1
    print(number_seq)
    assert number_seq == 3
    # the 3 contigs example are from a random subsampling of dog10.bam
