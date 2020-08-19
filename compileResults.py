from sqlite3 import connect

def compileSingleWinnerResults(db):
    #Delete existing results tables.
    db.execute("DROP TABLE IF EXISTS single_winner_results")
    db.execute("DROP TABLE IF EXISTS multiple_winner_results")
    
    #Create new results tables.
    db.execute("""CREATE TABLE single_winner_results (election TEXT, number_of_candidates INTEGER, total_points REAL,
                winner TEXT, winner_points REAL, winner_points_percentage REAL, winner_rank_1_votes REAL, winner_total_votes REAL,
                runner_up TEXT, runner_up_points REAL, runner_up_points_percentage REAL, runner_up_rank_1_votes REAL, runner_up_total_votes REAL,
                rank_1_majority_reversals INTEGER, total_votes_majority_reversals INTEGER, absolute_majority_reversals INTEGER)""")

    #Query contents table for election data.
    db.execute("SELECT * FROM contents")
    contents = db.fetchall()

    #Scan each election for relevant data and insert it into results tables.
    for r in contents:
        #Set the variables name to the election name and num to the number of candidates in the election.
        name = r[0]
        num = r[1]

        #Obtain all the data from the election table.
        db.execute("SELECT * FROM {table_name}".format(table_name = name))

        #Initialize empty lists to store each candidate and their points, rank 1 votes, and total votes in separate lists.
        candidates = []
        points = []
        r1_votes = []
        total_votes = []

        #Scan through each candidate in the election table to fill the lists initialized in the previous step.
        for c in db.fetchall():
            candidates.append(c[0])
            r1_votes.append(c[1])

            p = 0
            v = 0
            for rank in range(num):
                p += (1/(rank+1))*c[rank+1]
                v += c[rank+1]

            points.append(round(p,2))
            total_votes.append(v)

        #Determine total number of points.
        total_points = sum(points)
        
        #Determine data for the winner.
        w_points = max(points)
        winner = candidates[points.index(w_points)]
        w_points_pct = w_points/total_points
        w_r1_votes = r1_votes[candidates.index(winner)]
        w_total_votes = total_votes[candidates.index(winner)]

        #Determine data for the runner_up.
        runner_up = candidates[1]
        ru_points = points[1]
        ru_points_pct = ru_points/total_points
        ru_r1_votes = r1_votes[1]
        ru_total_votes = total_votes[1]

        #Determine number of rank 1 and total vote majority reversals.
        r1_majority_reversals = 0
        totv_majority_reversals = 0
        for i in range(num):
            if r1_votes[i] > w_r1_votes:
                r1_majority_reversals += 1
            if total_votes[i] > w_total_votes:
                totv_majority_reversals += 1

        #Determine number of absolute majority reversals.
        abs_majority_reversals = 0
        for i in range(num):
            if r1_votes[i] > w_r1_votes:
                if total_votes[i] > w_total_votes:
                    abs_majority_reversals += 1

        db.execute("INSERT INTO single_winner_results VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (name,num,total_points,
                    winner,w_points,w_points_pct,w_r1_votes,w_total_votes,
                    runner_up,ru_points,ru_points_pct,ru_r1_votes,ru_total_votes,
                    r1_majority_reversals,totv_majority_reversals,abs_majority_reversals))

    print("Results : Success")

#This function currently works only for a district magnitude of THREE (3 winners / 3 available seats).
def compileMultipleWinnerResults(db, dm, num_candidates : int = 0):
    #Delete existing results tables.
    db.execute("DROP TABLE IF EXISTS single_winner_results")
    db.execute("DROP TABLE IF EXISTS multiple_winner_results")

    #Create new results tables.
    db.execute("""CREATE TABLE multiple_winner_results ({columns})""".format(columns = generateResultsTableColumns(dm,num_candidates)))

    #Query contents table for election data.
    db.execute("SELECT * FROM contents")
    contents = db.fetchall()

    #Scan each election for relevant data and insert it into results tables.
    for r in contents:
        #Set the variables name to the election name and num to the number of candidates in the election.
        name = r[0]
        num = r[1]

        #Obtain all the data from the election table.
        db.execute("SELECT * FROM {table_name}".format(table_name = name))
        election_data = db.fetchall()

        #Initialize empty lists to store each candidate and their points, rank 1 votes, and total votes in separate lists.
        candidates = []
        points = []
        r1_votes = []
        total_votes = []

        #Scan through each candidate in the election table to fill the lists initialized in the previous step.
        for c in election_data:
            candidates.append(c[0])
            r1_votes.append(c[1])

            p = 0
            v = 0
            for rank in range(num):
                p += (1/(rank+1))*c[rank+1]
                v += c[rank+1]

            points.append(round(p,2))
            total_votes.append(v)

        #Determine the total number of points.
        total_points = sum(points)
        
        #Determine data for all winners and store it in results dictionary.
        results = {}
        for i in range(dm):
            w_points = "w" + str(i+1) + "_points"
            results[w_points] = points[i]

            w_points_pct = "w" + str(i+1) + "_points_pct"
            results[w_points_pct] = round(results[w_points]/total_points,4)*100

            w_r1_votes = "w" + str(i+1) + "_r1_votes"
            results[w_r1_votes] = r1_votes[i]

            w_tot_votes = "w" + str(i+1) + "_tot_votes"
            results[w_tot_votes] = total_votes[i]

            w_block_points = "w" + str(i+1) + "_block_points"
            results[w_block_points] = 0
            for j in range(dm):
                results[w_block_points] += election_data[i][j+1]

        #Determine data for all the runner-up candidates if possible.
        if num_candidates != 0:
            for i in range(num - dm):
                ru_points = "ru" + str(i+1) + "_points"
                results[ru_points] = points[dm+i]

                ru_points_pct = "ru" + str(i+1) + "_points_pct"
                results[ru_points_pct] = round(results[ru_points]/total_points,4)*100

                ru_r1_votes = "ru" + str(i+1) + "_r1_votes"
                results[ru_r1_votes] = r1_votes[dm+i]

                ru_tot_votes = "ru" + str(i+1) + "_tot_votes"
                results[ru_tot_votes] = total_votes[dm+i]

                ru_block_points = "ru" + str(i+1) + "_block_points"
                results[ru_block_points] = 0
                for j in range(dm):
                    results[ru_block_points] += election_data[dm+i][j+1]

        #Determine the least amount of rank 1 votes and total votes among the winners.
        winners_r1_votes = []
        for i in range(dm):
               winners_r1_votes.append(results["w"+str(i+1)+"_r1_votes"])
        least_r1_votes = min(winners_r1_votes)
               
        winners_tot_votes = []
        for i in range(dm):
               winners_tot_votes.append(results["w"+str(i+1)+"_tot_votes"])
        least_total_votes = min(winners_tot_votes)

        #Determine number of rank 1  and total vote majority reversals.
        r1_majority_reversals = 0
        totv_majority_reversals = 0
        for i in range(dm,num):
            if r1_votes[i] > least_r1_votes:
                r1_majority_reversals += 1
            if total_votes[i] > least_total_votes:
                totv_majority_reversals += 1

        #Determine number of absolute majority reversals.
        abs_majority_reversals = 0
        for c in range(dm,num):
            for w in range(dm):
                if r1_votes[c] > winners_r1_votes[w]:
                    if total_votes[c] > winners_tot_votes[w]:
                        abs_majority_reversals += 1

        #Insert obtained data into multiple winners results table.
        l = []
        for i in range(dm):
            l.extend(["w"+str(i+1)+"_points", "w"+str(i+1)+"_points_pct", "w"+str(i+1)+"_r1_votes", "w"+str(i+1)+"_tot_votes", "w"+str(i+1)+"_block_points"])
        if num_candidates != 0:
            for i in range(num-dm):
                l.extend(["ru"+str(i+1)+"_points", "ru"+str(i+1)+"_points_pct", "ru"+str(i+1)+"_r1_votes", "ru"+str(i+1)+"_tot_votes", "ru"+str(i+1)+"_block_points"])
        
        db.execute("""INSERT INTO multiple_winner_results VALUES (?,?,?,{data},?,?,?)""".format(data = ",".join(str(results[str(x)]) for x in l)),
                    (name,num,total_points,
                     r1_majority_reversals,totv_majority_reversals,abs_majority_reversals))
    
    print("Results : Success")


def generateResultsTableColumns(district_magnitude, number_of_candidates):
    columns = "election TEXT, number_of_candidates INTEGER, total_points REAL, "
    for i in range(district_magnitude):
        columns += "winner"+str(i+1)+"_points REAL, winner"+str(i+1)+"_points_percentage REAL, winner"+str(i+1)+"_rank_1_votes REAL, winner"+str(i+1)+"_total_votes REAL, winner"+str(i+1)+"_block_points REAL, "
    if number_of_candidates != 0:
        for i in range(number_of_candidates - district_magnitude):
            columns += "runner_up"+str(i+1)+"_points REAL, runner_up"+str(i+1)+"_points_percentage REAL, runner_up"+str(i+1)+"_rank_1_votes REAL, runner_up"+str(i+1)+"_total_votes REAL, runner_up"+str(i+1)+"_block_points REAL, "
    columns += "rank_1_majority_reversals INTEGER, total_votes_majority_reversals INTEGER, absolute_majority_reversals INTEGER"
    return columns
