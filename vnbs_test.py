# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 15:53:49 2017

@author: rober
"""

import var_n_binomial_si as vnbs

class M:
    pass

team1 = 'frc1' #5
team2 = 'frc2' #10
team3 = 'frc3' #15

category = M()
category.tba_name = 'cat'

match1 = M()
match1.amount = 13
match1.teams = [team1, team2]
match1.number = 1
match1.category = category

match2 = M()
match2.amount = 26
match2.teams = [team2, team3]
match2.number = 2
match2.category = category

match3 = M()
match3.amount = 22
match3.teams = [team1, team3]
match3.number = 3
match3.category = category

matches = [match1, match2, match3]

#p*m, m, u

#first try: 1.0 4.1 0.1 1.0 6.0 0.1  ratio_stdev = 0.1


#params = [1, 5, 1, 1, 5, 1] #p m u
#optimal: around 1 4 0 1 6 0
all_teams = [team1, team2, team3]
ratio_stdev = 0.1
scouting = {}

#print(vnbs.get_negative_likelihood(matches, scouting, all_teams, [1, 4, 0.01, 1, 6, 0.01], ratio_stdev))
params = vnbs.get_team_prob_distrs(matches, scouting, ratio_stdev)
print('')
for value in params:
    print(value)