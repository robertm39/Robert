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

def eq_test():
    teleop_low_goal_category_one = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    teleop_low_goal_category_two = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    print(teleop_low_goal_category_one ==  teleop_low_goal_category_two)

    number = 1
    category = teleop_low_goal_category_one
    amount = 2
    teams = ['frc830', 'frc3880', 'frc123']

    seg_one = SegmentMatch(number, category, amount, teams)
    seg_two = SegmentMatch(number, category, amount, teams)
    print(seg_one == seg_two)

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

def one_test(chance_scouted):
    teams = []
    probs = {}
    for i in range(1, 41):#40 teams
        team = 'frc' + i.__str__()
        teams.append(team)
        probs[team] = random.random()

    category = Category(0, ScoreReq.ALL, MatchPhase.TELEOP, 'collab')
    segmented = []
    scouting = {}
    temp_teams = []
    temp_teams.extend(teams)
    for i in range(1, 161):#80 two-way matches    161
        scouting[i] = {}
        match_scouting = scouting[i]
        
        match_teams = random.sample(temp_teams, 3)
        for team in match_teams:
            temp_teams.remove(team)
        if len(temp_teams) < 3:
            temp_teams = []
            temp_teams.extend(teams)
        
        #amount = 1
        #for team in match_teams:
        #    team_did = 0.0
        #    if random.random() <= probs[team]:
        #        team_did = 1.0
        #    else:
        #        amount = 0
        #    if random.random() <= chance_scouted:
        #        match_scouting[team] = (team_did, 1.0)   
        max_team = match_teams[0]
        max_prob = probs[max_team]
        for team in match_teams:
            if probs[team] > max_prob:
                max_team = team
                max_prob = probs[team]

        amount = 0
        if random.random() <= max_prob:
            amount = 1

        if random.random() <= chance_scouted:
            match_scouting[max_team] = amount
        
        segmented.append(SegmentMatch(i, category, amount, match_teams))  

    guessed_probs = get_non_stack_one_probs(segmented, scouting)
    tot_error = 0
    tot_squared_error = 0

    for team in teams:
        tp = probs[team]
        gp = guessed_probs[team]

        tot_error += abs(tp - gp)
        tot_squared_error += (tp - gp) ** 2
        
    return math.sqrt(tot_squared_error / len(teams))

def collab_test(chance_scouted):
    teams = []
    probs = {}
    for i in range(1, 41):#40 teams
        team = 'frc' + i.__str__()
        teams.append(team)
        probs[team] = min(random.random(), random.random(), random.random(), random.random())
    
    category = Category(0, ScoreReq.ALL, MatchPhase.TELEOP, 'collab')
    segmented = []
    scouting = {}
    temp_teams = []
    temp_teams.extend(teams)
    for i in range(1, 161):#80 two-way matches   161
        scouting[i] = {}
        match_scouting = scouting[i]
        
        match_teams = random.sample(temp_teams, 3)
        for team in match_teams:
            temp_teams.remove(team)
        if len(temp_teams) < 3:
            temp_teams = []
            temp_teams.extend(teams)
        
        #all_prob = 1.0
        #for team in match_teams:
        #    all_prob *= probs[team]
        #amount = 0
        #if random.random() <= all_prob:
        #    amount = 1
        amount = 1
        team_dids = []
        for team in match_teams:
            team_did = 0.0
            if random.random() <= probs[team]:
                team_did = 1.0
            else:
                amount = 0
            team_dids.append(team_did)
            if random.random() <= chance_scouted:
                match_scouting[team] = (team_did, 1.0)   

        #print(team_dids.__str__() + " " + amount.__str__())
        
        segmented.append(SegmentMatch(i, category, amount, match_teams))  

    fill_non_stacking_collab_scouting(scouting, segmented)
    #print(scouting.__str__())

    guessed_probs = get_non_stacking_collab_probs(segmented, scouting)
    tot_error = 0
    tot_squared_error = 0

    for team in teams:
        tp = probs[team]
        gp = guessed_probs[team]

        tot_error += abs(tp - gp)
        tot_squared_error += (tp - gp) ** 2
        
        #print(team + " prob: " + tp.__str__() + " guessed: " + gp.__str__() + " squared error: " + ((tp - gp) ** 2).__str__())

    #print("error: " + (tot_error / len(teams)).__str__() + " stdev: " + math.sqrt(tot_squared_error / len(teams)).__str__())
    #print("\a\a\a")
    return math.sqrt(tot_squared_error / len(teams))

def repeated_collab_test(times, chance_scouted):
    stdevs = []
    for i in range(0, times):
        stdevs.append(collab_test(chance_scouted))
    winsound.Beep(2500, 1000)
    return numpy.mean(stdevs)

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
