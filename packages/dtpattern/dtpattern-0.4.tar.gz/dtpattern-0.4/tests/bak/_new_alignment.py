from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

# Create sequences to be aligned.
a = Sequence('1 1'.split())
b = Sequence('1 2 2 2'.split())

# Create a vocabulary and encode the sequences.
v = Vocabulary()
aEncoded = v.encodeSequence(a)
bEncoded = v.encodeSequence(b)

# Create a scoring and align the sequences using global aligner.
scoring = SimpleScoring(2, -1)
aligner = GlobalSequenceAligner(scoring, -2)
score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)

# Iterate over optimal alignments and print them.
for encoded in encodeds:
    alignment = v.decodeSequenceAlignment(encoded)
    print(alignment)
    print('Alignment score:', alignment.score)
    print('Percent identity:', alignment.percentIdentity())
    print()



from dtpattern.alignment.align3 import Needleman, Hirschberg
seqa = list('1112')
seqb = list('1222')

# Align using Needleman-Wunsch algorithm.
n = Needleman()
a,b = n.align(seqa, seqb)
print(a)
print(b)
print
