import itertools
import os
import re

import click
import pandas as pd

from aligner import needleman_wunsch, smith_waterman


@click.group()
def action():
    pass


@action.command()
@click.option('-o', '--output_dir', help='Path to output folder', required=True)
@click.option('-p', '--proteins_dir', help='Path to folder with protein files', required=True)
def prepare(output_dir, proteins_dir):
    _prepare(output_dir, proteins_dir)


def _prepare(proteins_dir, output_dir):
    list_files = os.listdir(path=proteins_dir)
    list_fasta = [file for file in list_files if re.match('.*\.fasta', file)]
    fasta_combinations = list(itertools.combinations(list_fasta, 2))
    protein_combinations_path = os.path.join(output_dir, 'protein_combinations.csv')
    pd.DataFrame(fasta_combinations).to_csv(protein_combinations_path)


@action.command()
@click.option('-a', '--alignment_method', help='Alignment method: smith_waterman or needleman_wunsch', required=True)
@click.option('-i', '--iterative_method', help='If true iterative method will be used', is_flag=True, required=False)
@click.option('-o', '--output_dir', help='Path to output folder', required=True)
@click.option('-p', '--proteins_dir', help='Path to folder with protein files', required=True)
def run(alignment_method, iterative_method, output_dir, proteins_dir):
    _run(alignment_method, iterative_method, output_dir, proteins_dir)


def _run(alignment_method, iterative_method, output_dir, proteins_dir):
    if alignment_method == 'needleman_wunsch':
        align = needleman_wunsch
    elif alignment_method == 'smith_waterman':
        align = smith_waterman
    else:
        raise ValueError('Wrong alignment method!')

    protein_combinations_path = os.path.join(output_dir, 'protein_combinations.csv')
    fasta_combinations = pd.read_csv(protein_combinations_path)
    fasta_combinations.apply(lambda x: align(x, iterative_method, output_dir, proteins_dir), axis=1)


@action.command()
@click.option('-a', '--alignment_method', help='Alignment method: smith_waterman or needleman_wunsch', required=True)
@click.option('-i', '--iterative_method', help='If true iterative method will be used', is_flag=True, required=False)
@click.option('-o', '--output_dir', help='Path to output folder', required=True)
@click.option('-p', '--proteins_dir', help='Path to folder with protein files', required=True)
def prepare_run(alignment_method, iterative_method, output_dir, proteins_dir):
    _prepare(output_dir, proteins_dir)
    _run(alignment_method, iterative_method, output_dir, proteins_dir)


if __name__ == "__main__":
    action()
