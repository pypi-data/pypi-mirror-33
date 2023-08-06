#!/usr/bin/env python
# -*- coding: utf-8 -*-
import doit

from doit.doit_cmd import DoitMain
from doit.cmd_base import TaskLoader
from doit.task import clean_targets, dict_to_task

# def task_example():
#     return {
#         'actions': ['myscript'],
#         'file_dep': ['my_input_file'],
#         'targets': ['result_file'],
#     }


def run_tasks(tasks, args, config={'verbosity': 0}):
    '''Given a list of `Task` objects, a list of arguments,
    and a config dictionary, execute the tasks.
    Those task will be SPAdes and overlap layout
    '''

    if type(tasks) is not list:
        raise TypeError('tasks must be of type list.')

    class Loader(TaskLoader):
        @staticmethod
        def load_tasks(cmd, opt_values, pos_args):
            return tasks, config

    return DoitMain(Loader()).run(args)


def make_task(task_dict_func):
    '''Wrapper to decorate functions returning pydoit
    `Task` dictionaries and have them return pydoit `Task`
    objects
    '''
    def d_to_t(*args, **kwargs):
        ret_dict = task_dict_func(*args, **kwargs)
        return dict_to_task(ret_dict)
    return d_to_t


@make_task
def task_spades(num, type_r, output, mem, thread):

    if type_r == "pe":
        cmd = f"""spades.py -1 {output}/subsample_forward{num}.fastq \
        -2 {output}/subsample_reverse{num}.fastq -t {thread} -m {mem} \
        -o {output}/spades{num} """
        file_input1 = f"{output}/subsample_forward{num}.fastq"
        file_input2 = f"{output}/subsample_reverse{num}.fastq"
        output_dir = f"{output}/spades{num}"
        return {
                'name': f"spades {num}",
                'file_dep': [file_input1, file_input2],
                'targets': [output_dir],
                'actions': [cmd],
            }
    elif type_r == "uniq":
        cmd = f"""spades.py -s {output}/subsample_uniq{num}.fastq \
         -t {thread} -m {mem} -o {output}/spades{num} """
        file_input1 = f"{output}/subsample_uniq{num}.fastq"
        output_dir = f"{output}/spades{num}"
        return {
                'name': f"spades {num}",
                'file_dep': [file_input1],
                'targets': [output_dir],
                'actions': [cmd],
            }
    elif type_r == "bam":
        cmd = f"""spades.py --only-assembler --iontorrent \
        -s {output}/subsample_{num}.bam \
        -t {thread} -m {mem} -o {output}/spades{num}"""
        file_input1 = f"{output}/subsample_{num}.bam"
        output_dir = f"{output}/spades{num}"
        return {
                'name': f"spades {num}",
                'file_dep': [file_input1],
                'targets': [output_dir],
                'actions': [cmd],
            }
    elif type_r == "test":
        cmd = f"""spades.py -1  data/ecoli_1K_1.fq.gz\
        -2 data/ecoli_1K_2.fq.gz/ \
         -t {thread} -m {mem} -o {output} """
        file_input1 = "data/20_reads_R1.fastq"
        file_input2 = "data/20_reads_R2.fastq"
        output_dir = f"{output}"
        return {
                'name': f"spades {num}",
                'file_dep': [file_input1, file_input2],
                'targets': [output_dir],
                'actions': [cmd],
            }


@make_task
def task_canu(output, mem, thread, genome_size):
    contig_dir = f"{output}/temp"
    output_dir = f"{output}/temp/canu_out"
    contig = f"{contig_dir}/all_contigs.fasta"
    memory_per_thread = mem // thread
    cmd = f""" canu -assemble \
        -p canu_assembly -d {output_dir} \
        genomeSize={genome_size} \
        -pacbio-corrected \
        {contig} \
        -maxMemory={mem} -maxThreads={thread}
        """
    return {
            'name': "Canu",
            'file_dep': [contig],
            'targets': [output_dir],
            'actions': [cmd],
        }
