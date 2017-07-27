import random
import math
import winsound
import numpy

from StrongholdMatchSegmenter import StrongholdMatchSegmenter
import Algorithm as al
#from SegmentMatch import SegmentMatch
#from Category import Category
#from MatchPhase import MatchPhase
from utils import SegmentMatch, Category, MatchPhase

def segmenter_test():
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = al.get_segmented_competition(event, segmenter)
    teleop_low_goal_category = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    result = segmented[teleop_low_goal_category]
    print(len(result))
    print(result)

#def stacking_indiv_target_finder_test(competition):
#    segmenter = StrongholdMatchSegmenter()
#    event = "2016mihow"
#    segmented = al.get_segmented_competition(event, segmenter)
#    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
#    low_goal = segmented[teleop_low_goal]
#    #high_goal = segment

def collab_scouting_only_test(chance_scouted):
    pass

def get_competition(chance_scouted, category, get_match, fill_scouting, get_contr = random.random):
    teams = []
    probs = {}
    for i in range(1, 41):  #40 teams   41
        team = 'frc' + i.__str__()
        teams.append(team)
        probs[team] = get_contr()
    
    segmented = []
    scouting = {}
    temp_teams = []
    temp_teams.extend(teams)
    for i in range(1, 161): #80 two-way matches   161
        match_teams = random.sample(temp_teams, 3)
        for team in match_teams:
            temp_teams.remove(team)
        if len(temp_teams) < 3:
            temp_teams = []
            temp_teams.extend(teams)

        add_match = get_match(i, category, chance_scouted, match_teams, probs)
        #if not add_match is SegmentMatch:
        #print(add_match[0].__str__())
        segmented.append(add_match[0])
        scouting[i] = add_match[1]  

    fill_scouting(scouting, segmented)

    return segmented, scouting, probs

def get_normal_no_outliers():
    result = numpy.random.normal()
    while abs(result) >= 2:
        result = numpy.random.normal()
    return result

def get_pos_normal_no_outliers(mean, stdev):
    result = mean + get_normal_no_outliers() * stdev
    while result < 0:
        result = mean + get_normal_no_outliers() * stdev
    return result

#indiv stack
def get_stacking_indiv_match(number, category, chance_scouted, teams, contrs):
    total = 0
    match_scouting = {}
    for team in teams:
        contr = contrs[team][0]
        stdev = contrs[team][1]
        score = max(0, round(contr + get_normal_no_outliers() * stdev))
        total += score

        minimum = 0
        min_cert = 0
        if random.random() < chance_scouted:
            min_prop = 0.7 + random.random() / 10 #70%-80%
            minimum = math.floor(min_prop * score)
            min_cert = 1
            
        maximum = 0
        max_cert = 0
        if random.random() < chance_scouted:
            max_prop = 1.2 + random.random() / 10 #120%-130%
            maximum = math.ceil(max_prop * score)
            max_cert = 0
            
        match_scouting[team] = ( (minimum, min_cert), (maximum, max_cert), 1.0)

    return SegmentMatch(number, category, total, teams), match_scouting
def get_stack_indiv_contr():
    MAX = 5
    
    average = 0
    while random.random() < 2/3 and average < MAX: #exponential distribution
        average += 1

    stdev = min(average / 2, 1.0 + get_normal_no_outliers() / 4)

    return (average, stdev)

def get_stack_indiv_competition(chance_scouted):
    category = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, "indiv stacking")
    get_match = get_stacking_indiv_match
    get_contr = get_stack_indiv_contr
    fill_scouting = al.fill_in_stacking_indiv_scouting
    return get_competition(chance_scouted, category, get_match, fill_scouting, get_contr)

def get_stack_indiv_error(contrs, guessed_contrs):
    average_squared_diffs = []
    stdev_squared_diffs = []
    for team in contrs:
        average_squared_diffs.append((contrs[team][0] - guessed_contrs[team][0]) ** 2)
        stdev_squared_diffs.append((contrs[team][1] - guessed_contrs[team][1]) ** 2)
    return (numpy.mean(average_squared_diffs), numpy.mean(stdev_squared_diffs))

def get_stack_indiv_average(stdevs):
    av_stdevs = []
    stdev_stdevs = []
    for stdev  in stdevs:
        av_stdevs.append(stdev[0])
        stdev_stdevs.append(stdev[1])
    #print(av_stdevs)
    for stdev_stdev in stdev_stdevs:
        if stdev_stdev >= 5:
            print(stdev_stdev)
        
    return (numpy.mean(av_stdevs), numpy.mean(stdev_stdevs))

def stack_indiv_test(chance_scouted):
    return test(chance_scouted, get_stack_indiv_competition, al.get_stack_indiv_averages_and_stdevs, get_stack_indiv_error)

def repeat_stack_indiv_test(times, chance_scouted):
    #GLOBAl_COUNT = 0
    return repeat_test(times, chance_scouted, stack_indiv_test, get_stack_indiv_average)
    
#end indiv_stack

#collab
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

def get_collab_competition(chance_scouted):
    category = Category(0, ScoreReq.ALL, MatchPhase.TELEOP, 'collab')
    get_match = get_collab_match
    fill_scouting = al.fill_non_stacking_collab_scouting
    return get_competition(chance_scouted, category, get_match, fill_scouting)

def collab_test(chance_scouted):
    return test(chance_scouted, get_collab_competition, al.get_non_stacking_collab_probs)
#end collab

#indiv non-stack
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

def get_individual_non_stack_competition(chance_scouted):
    category = Category(0, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'one')
    get_match = get_one_match
    fill_scouting = fill_one_scouting
    return get_competition(chance_scouted, category, get_match, fill_scouting)

def one_test(chance_scouted):
    result =  test(chance_scouted, get_individual_non_stack_competition, al.get_non_stack_one_probs)
    print('done' + random.random().__str__())
    return result

def fill_one_scouting(a, b):
    pass
#end indiv non-stack

def get_stdev(probs, guessed_probs):
    squared_errors = []

    for team in probs:
        tp = probs[team]
        gp = guessed_probs[team]

        squared_errors.append((tp - gp) ** 2)
        
    return math.sqrt(numpy.mean(squared_errors))

def test(chance_scouted, get_competition, guess_probs, get_error=get_stdev):
    comp = get_competition(chance_scouted)
    segmented = comp[0]
    scouting = comp[1]
    probs = comp[2]

    guessed_probs = guess_probs(segmented, scouting)

    return get_error(probs, guessed_probs)

def repeat_test(times, chance_scouted, test, average=numpy.mean):
    stdevs = []
    for i in range(0, times):
        stdevs.append(test(chance_scouted))
    if times > 3000:
        winsound.Beep(2500, 1000)
    return average(stdevs)

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
    al.fill_non_stacking_collab_scouting(scouting, segmented)
    print(al.non_stacking_collab_target('a', segmented, scouting, probs))

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
    al.fill_in_stacking_indiv_scouting(segmented, scouting)
    contrs = al.get_stack_indiv_averages(segmented, scouting)
    for team in contrs:
        print(team + ": " + contrs[team].__str__())

def get_stack_indiv_averages_test():
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = al.get_segmented_competition(event, segmenter)
    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    teleop_high_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop high goal')
    low_goal = segmented[teleop_low_goal]
    high_goal = segmented[teleop_high_goal]
    low_goal_scouting = {}
    al.fill_in_stacking_indiv_scouting(low_goal_scouting, low_goal)
    low_goal_contrs = al.get_stack_indiv_averages(low_goal, low_goal_scouting)
    
    high_goal_scouting = {}
    al.fill_in_stacking_indiv_scouting(high_goal_scouting, high_goal)
    high_goal_contrs = al.get_stack_indiv_averages(high_goal, high_goal_scouting)

    for team in high_goal_contrs:
        print(team + " Low goal: " + low_goal_contrs[team].__str__() + " High goal: " + high_goal_contrs[team].__str__())
    
    #return low_goal_contrs
    
def fill_in_scouting_stacking_indiv_test(competition):
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = al.get_segmented_competition(event, segmenter)
    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    low_goal = segmented[teleop_low_goal]
    scouting = {}
    al.fill_in_stacking_indiv_scouting(low_goal, scouting)
    print(scouting)
    
