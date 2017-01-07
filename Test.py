import random
import math
import winsound
import numpy

from StrongholdMatchSegmenter import *
from Algorithm import *
from SegmentMatch import *
from Category import *
from MatchPhase import *
from ScoreReq import *

def segmenter_test():
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = get_segmented_competition(event, segmenter)
    teleop_low_goal_category = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    result = segmented[teleop_low_goal_category]
    print(len(result))
    print(result)

def stacking_indiv_target_finder_test(competition):
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = get_segmented_competition(event, segmenter)
    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    low_goal = segmented[teleop_low_goal]

def repeat_test(times, chance_scouted, test):
    stdevs = []
    for i in range(0, times):
        stdevs.append(test(chance_scouted))
    if times > 3000:
        winsound.Beep(2500, 1000)
    return numpy.mean(stdevs)

def collab_scouting_only_test(chance_scouted):
    pass

def get_competition(chance_scouted, category, get_match, fill_scouting):
    teams = []
    probs = {}
    for i in range(1, 41):#40 teams
        team = 'frc' + i.__str__()
        teams.append(team)
        probs[team] = random.random()
    
    segmented = []
    scouting = {}
    temp_teams = []
    temp_teams.extend(teams)
    for i in range(1, 161):#80 two-way matches   161
        match_teams = random.sample(temp_teams, 3)
        for team in match_teams:
            temp_teams.remove(team)
        if len(temp_teams) < 3:
            temp_teams = []
            temp_teams.extend(teams)

        add_match = get_match(i, category, chance_scouted, match_teams, probs)
        segmented.append(add_match[0])
        scouting[i] = add_match[1]  

    fill_scouting(scouting, segmented)

    return segmented, scouting, probs

def get_collab_match(number, category, chance_scouted, teams, probs):
    amount = 1
    team_dids = []

    match_scouting = {}
    for team in teams:
        team_did = 0.0
        if random.random() <= probs[team]:
            team_did = 1.0
        else:
            amount = 0
        team_dids.append(team_did)
        if random.random() < chance_scouted:
            match_scouting[team] = (team_did, 1.0)   
        
    return SegmentMatch(number, category, amount, teams), match_scouting

def get_one_match(number, category, chance_scouted, teams, probs):
    max_team = teams[0]
    max_prob = probs[max_team]
    match_scouting = {}
    for team in teams:
        if probs[team] > max_prob:
            max_team = team
            max_prob = probs[team]

    amount = 0
    if random.random() <= max_prob:
        amount = 1

    if random.random() < chance_scouted:
        match_scouting[max_team] = amount
        
    return SegmentMatch(number, category, amount, teams), match_scouting

def get_collab_competition(chance_scouted):
    category = Category(0, ScoreReq.ALL, MatchPhase.TELEOP, 'collab')
    get_match = get_collab_match
    fill_scouting = fill_non_stacking_collab_scouting
    return get_competition(chance_scouted, category, get_match, fill_scouting)

def get_individual_non_stack_competition(chance_scouted):
    category = Category(0, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'one')
    get_match = get_one_match
    fill_scouting = fill_one_scouting
    return get_competition(chance_scouted, category, get_match, fill_scouting)

def fill_one_scouting(a, b):
    pass

def get_stdev(probs, guessed_probs):
    squared_errors = []

    for team in probs:
        tp = probs[team]
        gp = guessed_probs[team]

        squared_errors.append((tp - gp) ** 2)
        
    return math.sqrt(numpy.mean(squared_errors))

def one_test(chance_scouted):
    result =  test(chance_scouted, get_individual_non_stack_competition, get_non_stack_one_probs)
    print('done' + random.random().__str__())
    return result

def collab_test(chance_scouted):
    return test(chance_scouted, get_collab_competition, get_non_stacking_collab_probs)

def test(chance_scouted, get_competition, guess_probs):
    comp = get_competition(chance_scouted)
    segmented = comp[0]
    scouting = comp[1]
    probs = comp[2]

    guessed_probs = guess_probs(segmented, scouting)

    return get_stdev(probs, guessed_probs)

def target_test():
    category = Category(0, ScoreReq.ALL, MatchPhase.TELEOP, 'collab')
    segmented = []
    scouting = {}

    probs = {'b0':0.484, 'b1':0.98, 'b2':0.919, 'c0':0.35, 'c1':0.944, 'c2':0.58}
    r0 = 0
    r1 = 1
    r2 = 0
    segmented.append(SegmentMatch(1, category, r0, ['a', 'b0', 'c0']))
    segmented.append(SegmentMatch(1, category, r1, ['a', 'b1', 'c1']))
    segmented.append(SegmentMatch(1, category, r2, ['a', 'b2', 'c2']))
    fill_non_stacking_collab_scouting(scouting, segmented)
    print(non_stacking_collab_target('a', segmented, scouting, probs))

def other_stack_indivs_test():
    segmented = []
    generic = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'generic')
    team1 = 'frc1'
    team2 = 'frc2'
    team3 = 'frc3'
    segmented.append(SegmentMatch(1, generic, 10, [team1, team2]))
    segmented.append(SegmentMatch(2, generic, 5, [team2, team3]))
    segmented.append(SegmentMatch(3, generic, 8, [team1, team3]))
    scouting = {}
    fill_in_stacking_indiv_scouting(segmented, scouting)
    contrs = get_stack_indiv_averages(segmented, scouting)
    for team in contrs:
        print(team + ": " + contrs[team].__str__())

def get_stack_indiv_averages_test():
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = get_segmented_competition(event, segmenter)
    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    teleop_high_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop high goal')
    low_goal = segmented[teleop_low_goal]
    high_goal = segmented[teleop_high_goal]
    low_goal_scouting = {}
    fill_in_stacking_indiv_scouting(low_goal, low_goal_scouting)
    low_goal_contrs = get_stack_indiv_averages(low_goal, low_goal_scouting)
    
    high_goal_scouting = {}
    fill_in_stacking_indiv_scouting(high_goal, high_goal_scouting)
    high_goal_contrs = get_stack_indiv_averages(high_goal, high_goal_scouting)

    for team in high_goal_contrs:
        print(team + " Low goal: " + low_goal_contrs[team].__str__() + " High goal: " + high_goal_contrs[team].__str__())
    
    return low_goal_contrs
    
def fill_in_scouting_stacking_indiv_test(competition):
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = get_segmented_competition(event, segmenter)
    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    low_goal = segmented[teleop_low_goal]
    scouting = {}
    fill_in_stacking_indiv_scouting(low_goal, scouting)
    print(scouting)
