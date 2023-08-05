from munkres import Munkres, print_matrix
matrix = [[5, 3,],
          [3, 3],
          [3, 3]]
m = Munkres()
indexes = m.compute(matrix)
print_matrix(matrix, msg='Lowest cost through this matrix:')
total = 0
for row, column in indexes:
    value = matrix[row][column]
    total += value
    print('(%d, %d) -> %d' % (row, column, value))
print('total cost: %d' % total)
