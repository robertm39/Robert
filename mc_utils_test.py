# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 14:23:07 2017

@author: rober
"""

import mc_utils as mcut

team1 = 'frc1'
team2 = 'frc2'

cat1 = 'stuff'
cat2 = 'things'

dct = {}

dct[team1] = {cat1:{1:.25, 2:.5, 3:.25}, cat2:{0:.5, 1:.5}}
dct[team2] = {cat1:{2:.2, 3:.5, 4:.3}, cat2:{0:.3, 1:.7}} #36 total

outcomes = mcut.outcome_iterator(dct)
outcomes = list(outcomes)
prev_outcomes = []
for outcome in outcomes:
    if outcome in prev_outcomes:
        print('copy:')
    print(outcome)
    prev_outcomes.append(outcome)
print('')
print(len(outcomes))