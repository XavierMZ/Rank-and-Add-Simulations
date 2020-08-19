from random import randint, shuffle
from math import floor

def makeUnrestrictedSquare(n,dm):
    #Make the list y, where y[i] represents the total number of people who will rank at least i candidates.
    y = generateRankVoteDistribution(n,dm)

    s = sum(y)

    #Fill the list x, where each element represents the total votes each candidate will receive.
    x = []
    for i in range(n):
        x.append(randint(0,min(int(10000/n),int(s/n))))
    while (s-sum(x)) > 0:
        l = list(range(n))
        shuffle(l)
        for i in l:
            add = randint(0,min(10000-x[i],s-sum(x)))
            x[i] += add

    #Initialize election matrix with zeros.
    square = []
    for i in range(n+1):
        row = []
        for j in range(n+2):
            row.append(0)
        square.append(row)

    #Set the sum of every row and column (total votes for each candidate and each ranking, respectively) based on x and y.
    for i in range(n):
        square[0][i] += y[i]
        square[i+1][n] += x[i]

    #Fill the election table by spreading the total votes from each ranking and candidate randomly, with the appropriate constraints.
    for c in range(n):
        for j in range(1,n+1):
            x_subtract = 0
            for r in range(c):
                x_subtract += square[j][r]
            square[j][c] = square[j][n] - x_subtract

        y_subtract = 0
        for r in range(1+c,n):
            y_subtract += square[0][r]

        while y_subtract > 0:
            for j in range(1,n+1):
                if square[j][c] < y_subtract:
                    s = randint(0,square[j][c])
                    square[j][c] -= s
                    y_subtract -= s
                else:
                    s = randint(0,y_subtract)
                    square[j][c] -= s
                    y_subtract -= s

    #Make the first row the last row in order for the election table to make sense visually.            
    square[0],square[n] = square[n],square[0]

    #Calculate the number of points of each candidate.
    for i in range(n):
        points = 0
        for j in range(n):
            points += square[i][j]*(1/(j+1))
        square[i][n+1] = round(points,2)

    # Rearrange the candidates by number of points (from greatest to smallest).
    for i in range(n):
        for r in range(n):
            if square[r+1][n+1] > square[r][n+1]:
                square[r+1],square[r] = square[r],square[r+1]

    #Divide all numbers by a constant to turn them into percentages.
    for i in range(n+1):
        for j in range(n+2):
            square[i][j] /= 100

    #Delete the final row to eliminate the vote totals for each ranking.
    del square[n]
    
    return square

#Algorithm to determine how the votes are distributed accross each ranking.
def generateRankVoteDistribution(num_candidates, district_mag):
    #Initialize list with 100% voters in rank 1.
    l = [10000]

    #Append numbers to list that remain high percentages until the number of seats is filled.
    for i in range(district_mag - 1):
        l.append(randint(5000,10000))

    #Sort current list in descending order.
    l.sort(reverse=True)

    #Append remaining numbers to list that drop slowly until the halfpoint of candidates is reached.
    for i in range(district_mag-1,num_candidates-1):
        l.append(randint(0,round(l[i])))

    #Append remaining numbers to list that drop quickly in percentages.
    '''for i in range(floor(num_candidates/2)-1,num_candidates-1):
        l.append(randint(0,round(l[i]/num_candidates)))'''

    return l

if __name__ == '__main__':
    for i in range(1):
        n = 4#randint(2,6)
        dm = 1
        
        array = makeUnrestrictedSquare(n,dm)
    
        #Print square.
        for i in range(n):
            for j in range(n+2):
                print("%6.2f" % (array[i][j]), end = ' ')
            print()
    
        print()
