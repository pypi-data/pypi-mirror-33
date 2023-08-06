#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pysam


from capture import bam


def test_count_bam():
    count = bam.count_bam("data/20_reads.bam")
    assert count == 20
