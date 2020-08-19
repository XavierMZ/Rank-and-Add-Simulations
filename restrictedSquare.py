from itertools import permutations
import numpy as np
import random

def makeRestrictedSquare(n):
    #n is the number of candidates (the size of the square).
    #n = 3
    p = []
    num_permutations = 14

    #Generate random permutations to construct matrixes with equal row/column sum.
    for i in range(num_permutations):
        p.append(np.random.permutation(range(1,n+1)))

    #Initialize election matrix with zeros.
    square = []
    for i in range(n):
        row = []
        for j in range(n+1):
            row.append(0)
        square.append(row)

    #Generate the election matrix by adding together many matrixes.
    for i in range(num_permutations):
        for j in range(num_permutations-i):
            for c in range(n):
                square[c][p[i][c]-1] += 1

    #Divide each row by the row/column sum to make each value a percentage.
    for i in range(n):
        for j in range(n):
            square[i][j] /= num_permutations*(num_permutations+1)/200 #num_permutations

    #Calculate the number of points of each candidate.
    for i in range(n):
        points = 0
        for j in range(n):
            points += square[i][j]*(1/(j+1))
        square[i][n] = points

    #Rearrange the candidates by number of points (from greatest to smallest).
    for i in range(n):
        for i in range(n-1):
            if square[i+1][n] > square[i][n]:
                square[i+1],square[i] = square[i],square[i+1]

    return square




#Code to print a square.s
'''n = 5
s = makeSquare(n)
for i in range(n):
    for j in range(n):
        print("%.4f" % (s[i][j]), end = ' ')
    print("| %.4f" % (s[i][n]))'''
