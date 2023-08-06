#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import doit
import logging
import filecmp
import unittest

from capture.jobs import *
from shutil import copyfile
from doit.doit_cmd import DoitMain
from doit.cmd_base import TaskLoader
from doit.task import clean_targets, dict_to_task


@unittest.skipIf(
    "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
    "Skipping this test on Travis CI.")
def test_doit_spades():
    type_r = "test"
    output = "testing_spades"
    mem = 24
    thread = 6
    num = "test"
    tasks = []
    logger = logging.getLogger(__name__)
    tasks.append(task_spades(
                               num, type_r, output, mem, thread
                               ))  # add args later
    run_tasks(tasks, ['run'])
    assert os.path.isfile(f"{output}/contigs.fasta")


@unittest.skipIf(
    "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
    "Skipping this test on Travis CI.")
def test_doit_canu():
    output = "testing_canu"
    output_temp = f"{output}/temp"
    os.makedirs(output)
    os.makedirs(output_temp)
    copyfile("data/test_canu_in.fasta", f"{output_temp}/all_contigs.fasta")
    mem = 24
    thread = 6
    tasks = []
    genome_size = 180000  # African Swine Fever Virus genome size 180kb
    tasks.append(task_canu(output, mem, thread, genome_size))
    run_tasks(tasks, ['run'])
    comparison = filecmp.cmp(
        "data/test_canu_out.fasta",
        f"{output_temp}/canu_out/canu_assembly.contigs.fasta"
        )
    assert comparison is True
