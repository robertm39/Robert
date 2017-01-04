import requests
import json
import math
import random

import numpy

from ScoreReq import *
from SegmentMatch import *

CLOSE_TO_ZERO = 0.01
VERY_CLOSE_TO_ZERO = 0.01

def get_segmented_competition(event, match_segmenter):
    URL_BASE = "https://www.thebluealliance.com/api/v2/event/%s/matches"
    HEADER = {"X-TBA-App-Id":"FRC830:z_scout:test"}
    source = URL_BASE % event
    r = requests.get(source, headers = HEADER)
    data = r.json()
    result = {}
    for match in data:
        if(match['comp_level'] == 'qm'):
            segments = match_segmenter.segment(match)
            for segment_match in segments:
                for key in segment_match:
                    if not (key in result):
                        result[key] = []
                    add = segment_match[key]
                    if(not add in result[key]):
                        result[key].append(add)
    return result

def get_team_prob_distrs(segment_matches, scouting): #for stacking indivs, scouting is a dict from numbers to dicts from team-strings to scouted contrs, certainties and durations
    #averages = get_averages(segment_matches, scouting)
    #stdevs = get_stdevs(averages, segment_matches)
    category = segment_matches[0].category
    #if category.stacking and category.score_req == ScoreReq.INDIVIDUAL:
    #    return get_stack_indiv_distrs(segment_matches, scouting)
    if category.score_req == ScoreReq.INDIVIDUAL:
        if category.stacking:
            return get_stack_indiv_distrs(segment_matches, scouting)
        else:
            return get_non_stack_one_probs(segment_matches, scouting)
    elif not category.stacking and category.score_req == ScoreReq.ALL:
        return get_non_stacking_collab_probs(segment_matches, scouting)

def get_stack_indiv_distrs(segment_matches, scouting):
    averages = get_stack_indiv_averages(segment_matches, scouting)
    stdevs = get_stdevs(averages, segment_matches)

#get_stack_indiv_averages and sub-functions
def get_stack_indiv_averages(segment_matches, scouting):
    result = {}
    average = get_average_contr(segment_matches)
    for team in all_teams(segment_matches):
        result[team] = average

    #going = 1
    #while going:
    #    prev = result.copy()
    #    for team in result:
    #        result[team] = target(team, segment_matches, scouting)
    #    if(distance(prev, result) <= CLOSE_TO_ZERO)
    #        going = 0
    return follow_target(result, segment_matches, stacking_indiv_target, scouting, CLOSE_TO_ZERO)

def stacking_indiv_target(team, segment_matches, scouting, curr_contrs):
    
    def match_target(team, segment, match_scouting, curr_contrs): #returns a tuple of a target-number and a weight-number.
        not_acc_for = not_accounted_for(team, segment, match_scouting, curr_contrs)
        team_scouting = match_scouting[team]
        scouted = team_scouting[0]
        certainty = team_scouting[1]
        duration = team_scouting[2]
        return (scouted * certainty + (1 - certainty) * not_acc_for / duration, duration)

    def not_accounted_for(team, segment, match_scouting, curr_contrs):
        accounted_for = 0
        for other_team in segment.teams:
            if other_team != team:
                other_team_scouting = match_scouting[other_team]
                scouted = other_team_scouting[0]
                certainty = other_team_scouting[1]
                duration = other_team_scouting[2]
                contr = curr_contrs[other_team]
                accounted_for += certainty * scouted + (1 - certainty) * duration * contr
        return segment.amount - accounted_for
    
    match_targets = []
    for segment in segment_matches:
        if team in segment.teams:
            match_targets.append(match_target(team, segment, scouting[segment.number], curr_contrs))
    total_weight = 0
    total_targets = 0
    for match_target in match_targets:
        total_targets += match_target[0]
        total_weight += match_target[1]
    return total_targets / total_weight



def not_accounted_for(team, segment, match_scouting, curr_contrs):
    accounted_for = 0
    for other_team in segment.teams:
        if other_team != team:
            other_team_scouting = match_scouting[other_team]
            scouted = other_team_scouting[0]
            certainty = other_team_scouting[1]
            duration = other_team_scouting[2]
            contr = curr_contrs[other_team]
            accounted_for += certainty * scouted + (1 - certainty) * duration * contr
    return segment.amount - accounted_for
            

def get_average_contr(segment_matches):
    total = 0.0
    for segment in segment_matches:
        total += segment.amount
    return total / 3.0 / len(segment_matches)
#end get_stack_indiv_averages and sub-functions

#get_non_stack_collab_probs and sub-functions
def get_non_stacking_collab_probs(segment_matches, scouting): #scouting is a map from match numbers to maps from team-strings to tuples of whether the team did the task and the certainty
    result = {}
    for team in all_teams(segment_matches):
        result[team] = 0.5

    #return result
    return follow_target(result, segment_matches, non_stacking_collab_target, scouting, VERY_CLOSE_TO_ZERO)

#TODO add support for certainties in between 0.0 and 1.0
def non_stacking_collab_target(team, segment_matches, scouting, curr_contrs): #scouting is a map from match numbers to maps from team-strings to tuples of whether the team did the task and the certainty
    successful_team_scouted = 0.0
    total_team_scouted = 0.0

    numerator = 0.0
    denominator = 0.0

    total = 0
    for segment in segment_matches:
        if team in segment.teams:
            total += 1

            segment_scouting = scouting[segment.number]

            if segment_scouting[team][1] > 0:
                #if segment_scouting[team][0] == 1.0:
                #   successful_team_scouted += 1
                successful_team_scouted += segment_scouting[team][0]
                total_team_scouted += 1
            else:
                add_to_den = 1.0
                add_to_num = segment.amount
                for other_team in segment.teams:
                   if other_team != team:
                       #print(other_team + " " + team)
                       other_team_scouting = segment_scouting[other_team]
                       scouted_contr = other_team_scouting[0]
                       certainty = other_team_scouting[1]
                       contr = curr_contrs[other_team]
                       total_contr = certainty * scouted_contr + (1 - certainty) * contr

                       add_to_num *= total_contr
                       add_to_den *= total_contr * total_contr
                numerator += add_to_num
                denominator += add_to_den
                #print("add to num: " + add_to_num.__str__())
                #print("add to den: " + add_to_den.__str__())

    #print("numerator: " + numerator.__str__() + " denominator: " + denominator.__str__())

    total_segments = total

    team_scouted_prob = 0
    if total_team_scouted != 0:
        team_scouted_prob = successful_team_scouted / total_team_scouted

    if denominator == 0:
        if total_team_scouted == 0:
            return curr_contrs[team]
        return team_scouted_prob
        
    non_team_scouted_prob = numerator / denominator
    
    if non_team_scouted_prob < 0:
        non_team_scouted_prob = 0
    elif non_team_scouted_prob > 1:
        non_team_scouted_prob = 1
        
    scouted_proportion = total_team_scouted / total_segments

    #print(total_team_scouted.__str__())
    
    return scouted_proportion * team_scouted_prob + (1 - scouted_proportion) * non_team_scouted_prob

def fill_non_stacking_collab_scouting(scouting, segment_matches):
    for segment in segment_matches:
        if not segment.number in scouting:
            scouting[segment.number] = {}
        match_scouting = scouting[segment.number]
        for team in segment.teams:
            if not team in match_scouting:
                match_scouting[team] = (0.0, 0.0)
    
#end get_non_stack_collab_probs and sub-functions

#get_non_stack_one_probs and sub-functions
def get_non_stack_one_probs(segment_matches, scouting): #scouting is a dict from match-numbers to a dict from teams to whether the team did the task; if the team didn't get a chance to do the task, it isn't in scouting
    result = {}
    for team in all_teams(segment_matches):
        result[team] = random.random()
        #result[team] = 0.5

    result = follow_target(result, segment_matches, non_stack_one_target, scouting, VERY_CLOSE_TO_ZERO)
    return result

def non_stack_one_target(team, segment_matches, scouting, contrs, __cache = {}):
    def error(prob):
        o_contrs = contrs.copy()
        o_contrs[team] = prob
        
        result = 0
        for segment in segment_matches:
            if team in segment.teams:
                match_scouting = scouting[segment.number]
                #print(len(match_scouting).__str__())
                if len(match_scouting) == 0:
                    match_probs = []
                    for other_team in segment.teams:
                        match_probs.append(o_contrs[other_team])
                    max_prob = max(match_probs)
                    result += (segment.amount - max_prob) ** 2
                else:
                    scout_prob = 0
                    
                    for other_team in match_scouting:
                        if other_team in segment.teams:
                            scout_prob = o_contrs[other_team]
                            result += (match_scouting[other_team] - scout_prob) ** 2
                    for other_team in segment.teams:
                        if not other_team in match_scouting:
                            o_contr = o_contrs[other_team]
                            result += (o_contr - min(o_contr, scout_prob)) ** 2
                #if team in match_scouting:
                #    result += (match_scouting[team] - prob) ** 2
                #else:
                #    none_scouted = 1
                #    max_prob = 0
                #    for other_team in segment.teams:
                #        if not other_team == team:
                #            if other_team in match_scouting:
                #                result += (o_contrs[team] - min(o_contrs[team], match_scouting[other_team])) ** 2
                #                none_scouted = 0
                #            elif o_contrs[other_team] > max_prob:
                #                max_prob = contrs[team]
                #    if none_scouted: # and prob > max_prob
                #        result += (segment.amount - max(o_contrs[team], max_prob)) ** 2
        return result

    partitions = [0.0, 1.0]
    matches_from_maximums = {}
    team_scouted_matches = []
    for segment in segment_matches:
        if team in segment.teams:
            segment_scouting = scouting[segment.number]
            other_contrs = []
            max_prob = 0
            #if not team in segment_scouting:
            none_scouted = 1
            for other_team in segment.teams:
                if not other_team == team:
                    if other_team in segment_scouting:
                        none_scouted = 0
                        max_prob = segment_scouting[other_team]
            if none_scouted:
                for other_team in segment.teams:
                    if not other_team == team:
                        other_contrs.append(contrs[other_team])
                max_prob = max(other_contrs)
            if not max_prob in partitions:
               partitions.append(max_prob)
            if not max_prob in matches_from_maximums:
                matches_from_maximums[max_prob] = []
            if team in segment_scouting:
                team_scouted_matches.append(segment)
                for other_team in segment.teams:
                    if not other_team == team:
                        other_prob = contrs[other_team]
                        if not other_prob in partitions:
                            partitions.append(other_prob)
                        if not other_prob in matches_from_maximums:
                            matches_from_maximums[other_prob] = []
            else:
                matches_from_maximums[max_prob].append(segment)

    #if not 1.0 in partitions:
    #    partitions.append(1.0)
    if not 1.0 in matches_from_maximums:
        matches_from_maximums[1.0] = []
    if not 0.0 in matches_from_maximums:
        matches_from_maximums[0.0] = []
    
    partitions.sort()

    prev_max = 0.0
    #if 0.0 in partitions:
    #    partitions.remove(0.0)

    relevant_matches = []
    relevant_matches.extend(team_scouted_matches)
    #if 0.0 in matches_from_maximums:
    #    relevant_matches.extend(matches_from_maximums[0.0])

    poss_probs = [0.0, 1.0]
    for maximum in partitions:
        if len(relevant_matches) > 0:
            num = 0
            den = 0
            #print("between " + prev_max.__str__() + " and " + maximum.__str__())
            
            for match in relevant_matches:
                match_scouting = scouting[match.number]
                den += 1
                if team in match_scouting:
                    #print("scouted")
                    num += match_scouting[team]
                    #other_probs = []
                    for other_team in match.teams:
                        if not other_team == team:
                            other_prob = contrs[other_team]
                            if maximum <= other_prob:
                                num += other_prob
                                den += 1
                            #other_probs.append(contrs[other_team])
                    #max_other_prob = max(other_probs)
                    #if(maximum <= max_other_prob):
                    #    num += max_other_prob
                    #    den += 1
                else:
                    none_scouted = 1
                    for other_team in segment.teams:
                        if not other_team == team:
                            if other_team in match_scouting:
                                none_scouted = 0
                                num += contrs[other_team]
                    if none_scouted:
                        num += match.amount
        
            prob = num / den
            #print("num: " + num.__str__() + " den: " + len(relevant_matches).__str__() + " prob:" + prob.__str__())
            #print("")
            
            #if prev_max <= prob <= maximum:
            poss_probs.append(prob)
        relevant_matches.extend(matches_from_maximums[maximum])
        prev_max = maximum

    #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    #old_poss_probs = []
    #old_poss_probs.extend(poss_probs)
    #poss_probs.extend(partitions)

    this_target = 0
    #poss_probs = []
    #for i in range(0, 101):
    #    poss_probs.append(i * 0.01)
    #for i in range(-20, 21):
    #    #print(i.__str__())
    #    poss_probs.append(contrs[team] + i * 0.001)
    
    if len(poss_probs) == 1:
        this_target = poss_probs[0]
    elif len(poss_probs) > 1:
        lowest_err_prob = poss_probs[0]
        min_err = len(segment_matches) + 1
        for poss_prob in poss_probs:
            err = error(poss_prob)
            if err < min_err:
                min_err = err
                lowest_err_prob = poss_prob
        this_target = lowest_err_prob
        
    elif len(poss_probs) == 0:
        this_target = 0

    if not team in __cache:
        __cache[team] = this_target
        return this_target
    prev = __cache[team]

    weight = 2
    return_target = (weight * prev + this_target) / (weight + 1)
    __cache[team] = return_target

    #if not this_target in old_poss_probs:
    #    print("partition target")
    #print(this_target.__str__())
    #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    
    return return_target

#end get_non_stack_one_probs and sub-functions

def follow_target(start, segment_matches, target, scouting, min_move): #target is a function that returns the target
    result = start.copy()
    going = 1
    while going:
        prev = result.copy()
        #new_result = {}
        for team in result:
            result[team] = target(team, segment_matches, scouting, result)

        #display = ""
        #for team in result:
        #    display += team + " " + result[team].__str__() + "\t"
        #print(display)
        #if error != None:
        #    print(error(result, scouting))
        if distance(prev, result) <= min_move:
            going = 0
        #result = new_result.copy()
    return result

def fill_in_stacking_indiv_scouting(segmented, scouting): #scouting is a dict from match-numbers to dicts from team-strings to scouted contrs, certainties and durations
    for segment in segmented:
        number = segment.number
        if not number in scouting:
            scouting[number] = {}
        segment_scouting = scouting[number]
        for team in segment.teams:
            if not team in segment_scouting:
                segment_scouting[team] = (0.0, 0.0, 1.0)
    
def distance(map_one, map_two):
    squared_diffs = 0
    for key in map_one:
        squared_diffs += (map_one[key] - map_two[key]) ** 2
    return math.sqrt(squared_diffs / len(map_one))

def all_teams(segment_matches):
    result = []
    for segment in segment_matches:
        for team in segment.teams:
            if not team in result:
               result.append(team)
    return result
    
def get_stdevs(segment_matches, averages, scouting):#averages is a dict from team-strings to decimal numbers
    #define
    pass
