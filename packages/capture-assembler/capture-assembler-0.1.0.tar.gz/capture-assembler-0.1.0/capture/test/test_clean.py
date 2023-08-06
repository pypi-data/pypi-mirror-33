#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from capture import clean


def test_clean_spades():
    output = "testing_clean_spades"
    output_temp = output + "/temp"
    os.makedirs(output)
    os.makedirs(output_temp)
    num_sub = 3
    c = 1
    while c <= num_sub:
        output_spades = output_temp + f"/spades{c}"
        os.makedirs(output_spades)
        open(f"{output_spades}/contigs.fasta", 'a').close()
        c += 1
    clean.clean_spades(output, num_sub)
    number_file = len(os.listdir(f"{output}/spades_contigs"))
    assert number_file == 3
