#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil


def clean_spades(output, num_sub):
    """  save the contigs from each spades run and
    remove all the tmp files
    """
    output_temp = output + "/temp"
    output_spades_contig = output + "/spades_contigs"
    os.makedirs(output_spades_contig)
    c = 1
    while c <= num_sub:
        shutil.copy(
            f"{output_temp}/spades{c}/contigs.fasta",
            f"{output_spades_contig}/contig_subsample_{c}.fasta"
            )
        c += 1
    try:
        shutil.rmtree(output_temp)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    os.makedirs(output_temp)
