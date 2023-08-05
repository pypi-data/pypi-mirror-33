import os

import numpy as np

import config as cfg
from utils import count_similarity, find_next_blosum, load_matrix, match_score, read_sequence, save_alignment


def needleman_wunsch(x, iterative_method, output_dir, proteins_dir):
    _, protein1, protein2 = x
    protein1_header, protein1_seq = read_sequence(protein1, proteins_dir)
    protein2_header, protein2_seq = read_sequence(protein2, proteins_dir)
    output_name = [protein1_header[1:5], protein2_header[1:5], 'global']

    if iterative_method:
        output_name.append('iterative')
        protein1_align, protein2_align, similarity = _needleman_wunsch_iterative(protein1_seq, protein2_seq)
    else:
        protein1_align, protein2_align, similarity = _needleman_wunsch(protein1_seq, protein2_seq)

    output = os.path.join(output_dir, '_'.join(output_name))
    save_alignment(protein1_align, protein2_align, similarity, output)


def smith_waterman(x, iterative_method, output_dir, proteins_dir):
    _, protein1, protein2 = x
    protein1_header, protein1_seq = read_sequence(protein1, proteins_dir)
    protein2_header, protein2_seq = read_sequence(protein2, proteins_dir)
    output_name = [protein1_header[1:5], protein2_header[1:5], 'local']

    if iterative_method:
        output_name.append('iterative')
        protein1_align, protein2_align, similarity = _smith_waterman_iterative(protein1_seq, protein2_seq)
    else:
        protein1_align, protein2_align, similarity = _smith_waterman(protein1_seq, protein2_seq)

    output = os.path.join(output_dir, '_'.join(output_name))
    save_alignment(protein1_align, protein2_align, similarity, output)


def _needleman_wunsch(seq1, seq2, matrix_filename="similarity_matrix/BLOSUM_62"):
    rows, columns = len(seq1), len(seq2)
    score_matrix = np.zeros((rows + 1, columns + 1))
    similarity_matrix = load_matrix(matrix_filename)

    for i in range(rows + 1):
        score_matrix[i][0] = cfg.gap_penalty * i
    for j in range(columns + 1):
        score_matrix[0][j] = cfg.gap_penalty * j
    for i in range(1, rows + 1):
        for j in range(1, columns + 1):
            match = score_matrix[i - 1][j - 1] + match_score(seq1[i - 1], seq2[j - 1], similarity_matrix)
            delete = score_matrix[i - 1][j] + cfg.gap_penalty
            insert = score_matrix[i][j - 1] + cfg.gap_penalty
            score_matrix[i][j] = max(match, delete, insert)

    align1, align2 = '', ''
    i, j = rows, columns
    while i > 0 and j > 0:
        score_current = score_matrix[i][j]
        score_diagonal = score_matrix[i - 1][j - 1]
        score_up = score_matrix[i][j - 1]
        score_left = score_matrix[i - 1][j]

        if score_current == score_diagonal + match_score(seq1[i - 1], seq2[j - 1], similarity_matrix):
            align1 += seq1[i - 1]
            align2 += seq2[j - 1]
            i -= 1
            j -= 1
        elif score_current == score_left + cfg.gap_penalty:
            align1 += seq1[i - 1]
            align2 += '-'
            i -= 1
        elif score_current == score_up + cfg.gap_penalty:
            align1 += '-'
            align2 += seq2[j - 1]
            j -= 1

    while i > 0:
        align1 += seq1[i - 1]
        align2 += '-'
        i -= 1
    while j > 0:
        align1 += '-'
        align2 += seq2[j - 1]
        j -= 1

    return align1, align2, count_similarity(align1, align2, min(len(seq1), len(seq2)))


def _smith_waterman(seq1, seq2, matrix_filename="similarity_matrix/BLOSUM_62"):
    rows, columns = len(seq1), len(seq2)
    score_matrix = np.zeros((rows + 1, columns + 1))
    pointer = np.zeros((rows + 1, columns + 1))
    similarity_matrix = load_matrix(matrix_filename)

    max_score = 0
    for i in range(1, rows + 1):
        for j in range(1, columns + 1):
            score_diagonal = score_matrix[i - 1][j - 1] + match_score(seq1[i - 1], seq2[j - 1], similarity_matrix)
            score_up = score_matrix[i][j - 1] + cfg.gap_penalty
            score_left = score_matrix[i - 1][j] + cfg.gap_penalty
            score_matrix[i][j] = max(0, score_left, score_up, score_diagonal)
            if score_matrix[i][j] == 0:
                pointer[i][j] = 0  # 0 means end of the path
            if score_matrix[i][j] == score_left:
                pointer[i][j] = 1  # 1 means trace up
            if score_matrix[i][j] == score_up:
                pointer[i][j] = 2  # 2 means trace left
            if score_matrix[i][j] == score_diagonal:
                pointer[i][j] = 3  # 3 means trace diagonal
            if score_matrix[i][j] >= max_score:
                max_i = i
                max_j = j
                max_score = score_matrix[i][j]

    align1, align2 = '', ''

    i, j = max_i, max_j

    while pointer[i][j] != 0:
        if pointer[i][j] == 3:
            align1 += seq1[i - 1]
            align2 += seq2[j - 1]
            i -= 1
            j -= 1
        elif pointer[i][j] == 2:
            align1 += '-'
            align2 += seq2[j - 1]
            j -= 1
        elif pointer[i][j] == 1:
            align1 += seq1[i - 1]
            align2 += '-'
            i -= 1

    return align1, align2, count_similarity(align1, align2, min(len(seq1), len(seq2)))


def _needleman_wunsch_iterative(seq1, seq2):
    current_blosum = 'Blosum62'
    used = [current_blosum]
    while True:
        matrix_filename = 'similarity_matrix/{}'.format(current_blosum)
        protein1_align, protein2_align, similarity = _needleman_wunsch(seq1, seq2, matrix_filename)
        next_blosum = find_next_blosum(similarity)
        if next_blosum in used:
            break
        used.append(next_blosum)
        current_blosum = next_blosum
    return protein1_align, protein2_align, similarity


def _smith_waterman_iterative(seq1, seq2):
    current_blosum = 'Blosum62'
    used = [current_blosum]
    while True:
        matrix_filename = 'similarity_matrix/{}'.format(current_blosum)
        protein1_align, protein2_align, similarity = _smith_waterman(seq1, seq2, matrix_filename)
        next_blosum = find_next_blosum(similarity)
        if next_blosum in used:
            break
        used.append(next_blosum)
        current_blosum = next_blosum
    return protein1_align, protein2_align, similarity
