#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Bio import SeqIO


def contig(num_sub, output):
    location_contigs = output + "/spades_contigs"
    output_temp = output + "/temp"
    list_contigs = []
    c = 1
    while c <= num_sub:
        input_file = f"{location_contigs}/contig_subsample_{c}.fasta"
        fasta_sequences = SeqIO.parse(open(input_file), "fasta")
        for fasta in fasta_sequences:
            if len(str(fasta.seq)) >= 1000:
                list_contigs.append(fasta)
        c += 1
    SeqIO.write(list_contigs, f"{output_temp}/all_contigs.fasta", "fasta")
