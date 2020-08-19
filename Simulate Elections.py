from sys import exit
from sqlite3 import connect
from random import randint
from restrictedSquare import makeRestrictedSquare
from unrestrictedSquare import makeUnrestrictedSquare
from compileResults import *


def main(restriction : bool = False ,number_of_elections : int = 100, district_magnitude : int = 1, *number_of_candidates):
    # Create elections database and connect cursor.
    electionsDatabase = connect("SimulatedElections.db")
    db = electionsDatabase.cursor()

    # Create election tables in database.
    createElectionTables(db, number_of_elections, district_magnitude, number_of_candidates, restriction)

    # Create results table in database.
    if district_magnitude == 1:
        compileSingleWinnerResults(db)
    else:
        if len(number_of_candidates) == 1:
            compileMultipleWinnerResults(db, district_magnitude, number_of_candidates[0])
        else:
            compileMultipleWinnerResults(db, district_magnitude)

    # Commit data and close the database.
    electionsDatabase.commit()
    electionsDatabase.close()

    print("Main    : Success")
    exit()


#Create election tables in database.
def createElectionTables(db, num_elections, district_magnitude, num_candidates, restriction):

    # Delete all election tables in database.
    db.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='contents'")
    if db.fetchone()[0] == 1:
        db.execute("SELECT election_name FROM contents")
        for election in db.fetchall():
            db.execute("DROP TABLE IF EXISTS {table_name}".format(table_name = election[0]))
    
    # Create a table of contents in which to store the name of every election and their number of candidates.
    db.execute("DROP TABLE IF EXISTS contents")
    db.execute("CREATE TABLE contents (election_name TEXT, number_of_candidates INTEGER)")
    
    for i in range(num_elections):
        election_name = "election" + str(i+1)

        # Determine number of candidates depending on user input (no input = random number, 1 input = fixed number, 2 inputs = random number from a determined range).
        if num_candidates:
            if len(num_candidates) == 1:
                number_of_candidates = num_candidates[0]
            else:
                number_of_candidates = randint(num_candidates[0], num_candidates[1])
        else:
            number_of_candidates = randint(2, 6)

        # Insert election information into the contents table in the database.
        db.execute("INSERT INTO contents VALUES ('{name}', {num})".format(name = election_name, num = number_of_candidates) )

        # Create election table in the database.
        table_columns = generateColumnsString(number_of_candidates, restriction)
        db.execute("CREATE TABLE {table_name} ({columns})".format(table_name = election_name, columns = table_columns) )

        # Generate values for an election table for a given number of candidates, taking into consideration the restriction.
        if restriction == True:
            votes_array = makeRestrictedSquare(number_of_candidates)
        else:
            votes_array = makeUnrestrictedSquare(number_of_candidates,district_magnitude)

        # Insert candidate names and vote data into election tables in database.
        for j in range(number_of_candidates):
            db.execute("INSERT INTO {table_name} VALUES (\"{candidate_name}\", {votes})".format(table_name = election_name, 
                                                        candidate_name = "Candidate_" + chr(randint(65, 90)), votes = ", ".join(str(round(x,4)) for x in votes_array[j]) ) )
# Generate string of table columns.
def generateColumnsString(n, restriction):
    columns = "candidates TEXT, "
    for i in range(n):
        columns += ("rank_" + str(i+1) + "_votes REAL, ")
    if restriction == False:
        columns += "total_votes REAL, "
    columns += "points REAL"
    return columns


# Usage: main(restriction (whether voters have to rank all candidates or not) = False, number_of_elections = 1000, district_magnitude = 1, number_of_candidates = randint(2,6)).
main(False,100,3,7)
