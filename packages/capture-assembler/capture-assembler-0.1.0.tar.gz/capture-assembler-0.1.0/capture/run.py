#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from capture.jobs import *


def spades(num_sub, output, type_r, mem, thread):  # more parameter later
    num = 1
    tasks = []
    while num <= num_sub:
        tasks.append(task_spades(
                               num, type_r, output, mem, thread
                               ))  # add args later
        num += 1
    run_tasks(tasks, ['run'])


def canu(output, mem, thread, genome_size):
    os.makedirs(f"{output}/temp/canu")
    tasks = []
    tasks.append(task_canu(output, mem, thread, genome_size))
    run_tasks(tasks, ['run'])
