
import math

#from ScoreReq import ScoreReq
import utils as ut
import stacking_indiv as si
import scaled_scouting_si as sssi
import nonstacking_collab as nc
import nonstack_one as no
#from SegmentMatch import SegmentMatch

CLOSE_TO_ZERO = 0.001
VERY_CLOSE_TO_ZERO = 0.01
ULTRA_CLOSE_TO_ZERO = 0.000001

def get_team_prob_distrs(segment_matches, scouting, full_scouted=False): #for stacking indivs, scouting is a dict from numbers to dicts from team-strings to scouted contrs, certainties and durations
#    category = segment_matches[0].category
#    if category.score_req == ut.ScoreReq.INDIVIDUAL:
#        if category.stacking:
    return sssi.get_stack_indiv_distrs(segment_matches, scouting) if full_scouted else si.get_stack_indiv_distrs(segment_matches, scouting)
#        else:
#            pass
#    elif category.score_req == ut.ScoreReq.ONE:
#        return probs_to_distrs(no.get_non_stack_one_probs(segment_matches, scouting))
#    elif not category.stacking and category.score_req == ut.ScoreReq.ALL:
#        return probs_to_distrs(nc.get_non_stacking_collab_probs(segment_matches, scouting))

def apply_rtm(prob, num_of_matches):
    return (prob*num_of_matches + 1)/(num_of_matches + 2)

def null_fill_scouting(category, scouting, segmented):
    pass

def filter_match_scouting(match_scouting, teams):
    result = {}
    for team in teams:
        if team in match_scouting:
            result[team] = match_scouting[team]
    return result

def follow_target(start, segment_matches, target, scouting, min_move): #target is a function that returns the target
    result = start.copy()
    going = 1
    while going:
        prev = result.copy()
        for team in result:
            result[team] = target(team, segment_matches, scouting, result)
        if distance(prev, result) <= min_move:
            going = 0
    return result

def fill_scouting(category, scouting, segmented):
    #if category.score_req == ut.ScoreReq.INDIVIDUAL:
    #    if category.stacking:
    si.fill_in_stacking_indiv_scouting(scouting, segmented)
    #    else:
    #        pass
    #elif not category.stacking and category.score_req == ut.ScoreReq.ALL:
    #    nc.fill_non_stacking_collab_scouting(scouting, segmented)

def probs_to_distrs(probs, name):
    distrs = {}
    for team in probs:
        prob = probs[team]
        distrs[team] = {name: {0.0:(1 - prob), 1.0:prob}}#{{name:0.0}:(1 - prob), {name:1.0}:prob}
    return distrs
    
def distance(map_one, map_two):
    squared_diffs = 0
    for key in map_one:
        squared_diffs += (map_one[key] - map_two[key]) ** 2
    return math.sqrt(squared_diffs / len(map_one))

def all_teams(segment_matches, scouting = {}):
    result = []
    for segment in segment_matches:
        for team in segment.teams:
            if not team in result:
               result.append(team)
               
    for match_num in scouting:
        m_scouting = scouting[match_num]
        for team in m_scouting:
            if not team in result:
                result.append(team)
                
    return result
    
def add_category_to_distrs(pre_distrs, category):
    name = category.tba_name
    distrs = {}
    for team in pre_distrs:
        team_distrs = {}
        for value in pre_distrs[team]:
            prob = pre_distrs[team][value]
            team_distrs[value] = prob
        sub_distrs = {}
        sub_distrs[name] = team_distrs
        #if name == "auton low goal":
        #    print(team_distrs)
        distrs[team] = sub_distrs
    return distrs

def get_stdevs(segment_matches, averages, scouting):#averages is a dict from team-strings to decimal numbers
    #define
    pass
