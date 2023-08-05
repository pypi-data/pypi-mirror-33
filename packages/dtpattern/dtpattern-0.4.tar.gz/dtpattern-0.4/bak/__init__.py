from dtpattern.alignment.utils import translate


def zeros(shape):
    retval = []
    for x in range(shape[0]):
        retval.append([])
        for y in range(shape[1]):
            retval[-1].append(0)
    return retval


  # both for opening and extanding

gap_penalty = 'gap_penalty'
INS = 'insert'
DEL = 'delete'
match_award = 'match_award'
cset_match_award = 'cset_match_award'
mismatch_penalty = 'mismatch_penalty'
score_matrix={
    gap_penalty: -15,
    INS: -15, DEL: -1,
    match_award: 5,
    cset_match_award:3,
    mismatch_penalty: -4
}


def equals(alpha, beta):
    if isinstance(alpha, str) and isinstance(beta, str):
        if alpha == beta:
            return True
    if isinstance(alpha, list) and isinstance(beta, list):
        if set(alpha) == set(beta):
            return True
    elif isinstance(beta, list):
        sym = translate(alpha)
        if sym in beta:
            return True
    elif isinstance(alpha, list):
        sym = translate(beta)
        if sym in alpha:
            return True
    return False



def match_score2(alpha, beta, score_matrix=score_matrix):

    if alpha == '-' and beta != '-':
        return score_matrix[gap_penalty]
    if alpha != '-' and beta == '-':
        return score_matrix[gap_penalty]

    if isinstance(alpha, str) and isinstance(beta, str):
        if alpha == beta:
            return score_matrix[match_award]
    elif isinstance(alpha, list) and isinstance(beta, list):
        if set(beta) < set(alpha):
            return score_matrix[match_award]

    elif isinstance(beta, list):
        sym = translate(alpha)
        if sym in beta:
            return score_matrix[cset_match_award]
    elif isinstance(alpha, list):
        sym = translate(beta)
        if sym in alpha:
            return score_matrix[cset_match_award]

    return score_matrix[mismatch_penalty]

def finalize(align1, align2,score_matrix=score_matrix):
    align1 = align1[::-1]  # reverse sequence 1
    align2 = align2[::-1]  # reverse sequence 2

    i, j = 0, 0

    # calcuate identity, score and aligned sequeces
    symbol = []
    found = 0
    score = 0
    identity = 0

    for i in range(0, len(align1)):
        # if two AAs are the same, then output the letter
        if equals(align1[i], align2[i]):
            if align1[i] != align2[i]:
                symbol.append([align1[i], align2[i]])
            else:
                symbol.append(align1[i])
            identity = identity + 1
            score += match_score2(align1[i], align2[i],score_matrix=score_matrix)

        # if they are not identical and none of them is gap
        elif align1[i] != align2[i] and align1[i] != '-' and align2[i] != '-':
            score += match_score2(align1[i], align2[i],score_matrix=score_matrix)
            symbol.append([align1[i], align2[i]])
            found = 0

        # if one of them is a gap, output a space
        elif align1[i] == '-' or align2[i] == '-':
            symbol.append([align1[i], align2[i]])
            score += score_matrix[gap_penalty]

    identity = float(identity) / len(align1) * 100

    return identity, score, align1, symbol, align2


def needle(seq1, seq2, score_matrix=score_matrix):
    m, n = len(seq1), len(seq2)  # length of two sequences

    # Generate DP table and traceback path pointer matrix
    score = zeros((m + 1, n + 1))  # the DP table

    # Calculate DP table
    for i in range(0, m + 1):
        score[i][0] = score_matrix[INS] * i #score_matrix[gap_penalty] * i
    for j in range(0, n + 1):
        score[0][j] = score_matrix[DEL] * j #score_matrix[delete] * j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score2(seq1[i - 1], seq2[j - 1],score_matrix=score_matrix)
            delete = score[i - 1][j] + score_matrix[DEL]
            insert = score[i][j - 1] + (1*score_matrix[INS])
            score[i][j] = max(match, delete, insert)

    # Traceback and compute the alignment
    align1, align2 = [], []
    i, j = m, n  # start from the bottom right cell
    while i > 0 and j > 0:  # end toching the top or the left edge
        score_current = score[i][j]
        score_diagonal = score[i - 1][j - 1]
        score_up = score[i][j - 1]
        score_left = score[i - 1][j]

        if score_current == score_diagonal + match_score2(seq1[i - 1], seq2[j - 1],score_matrix=score_matrix):
            align1.append(seq1[i - 1])
            align2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif score_current == score_left + score_matrix[gap_penalty]:
            align1.append(seq1[i - 1])
            align2.append('-')
            i -= 1
        elif score_current == score_up + score_matrix[gap_penalty]:
            align1.append('-')
            align2.append(seq2[j - 1])
            j -= 1

    # Finish tracing up to the top left cell
    while i > 0:
        align1.append(seq1[i - 1])
        align2.append('-')
        i -= 1
    while j > 0:
        align1.append('-')
        align2.append(seq2[j - 1])
        j -= 1

    return finalize(align1, align2, score_matrix=score_matrix)


def water(seq1, seq2, score_matrix=score_matrix):
    m, n = len(seq1), len(seq2)  # length of two sequences

    # Generate DP table and traceback path pointer matrix
    score = zeros((m + 1, n + 1))  # the DP table
    pointer = zeros((m + 1, n + 1))  # to store the traceback path

    max_score = 0  # initial maximum score in DP table
    # Calculate DP table and mark pointers
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score_diagonal = score[i - 1][j - 1] + match_score2(seq1[i - 1], seq2[j - 1],score_matrix=score_matrix)
            score_up = score[i][j - 1] + score_matrix[gap_penalty]
            score_left = score[i - 1][j] + score_matrix[gap_penalty]
            score[i][j] = max(0, score_left, score_up, score_diagonal)
            if score[i][j] == 0:
                pointer[i][j] = 0  # 0 means end of the path
            if score[i][j] == score_left:
                pointer[i][j] = 1  # 1 means trace up
            if score[i][j] == score_up:
                pointer[i][j] = 2  # 2 means trace left
            if score[i][j] == score_diagonal:
                pointer[i][j] = 3  # 3 means trace diagonal
            if score[i][j] >= max_score:
                max_i = i
                max_j = j
                max_score = score[i][j];

    align1, align2 = [], []  # initial sequences

    i, j = max_i, max_j  # indices of path starting point

    # traceback, follow pointers
    while pointer[i][j] != 0:
        if pointer[i][j] == 3:
            align1.append(seq1[i - 1])
            align2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif pointer[i][j] == 2:
            align1.append('-')
            align2.append(seq2[j - 1])
            j -= 1
        elif pointer[i][j] == 1:
            align1.append(seq1[i - 1])
            align2.append('-')
            i -= 1

        return finalize(align1, align2, score_matrix=score_matrix)


class Alignment(object):

    def __init__(self, alpha, beta):
        if isinstance(alpha,str) and isinstance(beta, str):
            self.string_alignment(alpha, beta)
        #elif isinstance(alpha,Pattern) and isinstance(beta, str):
        #    self.pattern_string_alignment(alpha, beta)
        #elif isinstance(alpha,str) and isinstance(beta, Pattern):
        #    self.pattern_string_alignment( beta, alpha)
        #elif isinstance(alpha,Pattern) and isinstance(beta, Pattern):
        #    self.pattern_alignment(alpha, beta)

    def string_alignment(self, alpha, beta):
        pass
