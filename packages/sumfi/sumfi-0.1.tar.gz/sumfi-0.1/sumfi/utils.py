import os

import config as cfg


def count_similarity(align1, align2, length):
    identity = 0
    for i in range(0, len(align1)):
        if align1[i] == align2[i]:
            identity = identity + 1

    return float(identity) / length * 100


def find_next_blosum(similarity):
    blosum = cfg.blosum
    for b in blosum:
        blosum[b] = abs(blosum[b] - similarity)
    return min(blosum, key=blosum.get)


def load_matrix(matrix_filename):
    with open(matrix_filename) as matrix_file:
        matrix = matrix_file.read()
    lines = matrix.strip().split('\n')

    header = lines.pop(0)
    columns = header.split()
    matrix = {}

    for row in lines:
        entries = row.split()
        row_name = entries.pop(0)
        matrix[row_name] = {}

        if len(entries) != len(columns):
            raise Exception('Improper entry number in row')
        for column_name in columns:
            matrix[row_name][column_name] = entries.pop(0)

    return matrix


def match_score(a, b, similarity_matrix):
    if a == '-' or b == '-':
        return cfg.gap_penalty
    return int(similarity_matrix[a][b])


def read_sequence(protein_name, proteins_dir):
    filepath = os.path.join(proteins_dir, protein_name)
    with open(filepath, 'r') as f:
        seq = ''
        header = f.readline().strip()
        if not header.startswith('>'):
            raise ValueError('Not a FASTA file!')
        for line in f:
            if line[0] == '>':
                break
            seq += line.strip()

        return header, seq


def save_alignment(align1, align2, similarity, output):
    with open(output, 'w') as f:
        f.write('Similarity = {:.2f} %\n'.format(similarity))
        f.write('{}\n'.format(align1))
        f.write('{}\n'.format(align2))
