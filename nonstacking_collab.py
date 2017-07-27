# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 19:39:42 2017

@author: rober
"""

import Algorithm as al

#get_non_stack_collab_probs and sub-functions
def get_non_stacking_collab_probs(segment_matches, scouting): #scouting is a map from match numbers to maps from team-strings to tuples of whether the team did the task and the certainty
    result = {}
    for team in al.all_teams(segment_matches):
        result[team] = 0.5

    #return result
    return al.follow_target(result, segment_matches, non_stacking_collab_target, scouting, al.VERY_CLOSE_TO_ZERO)

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

            if segment_scouting[team][1] > 0 or segment.amount == 1:
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
    
    return al.apply_rtm(scouted_proportion * team_scouted_prob + (1 - scouted_proportion) * non_team_scouted_prob, denominator)

def fill_non_stacking_collab_scouting(scouting, segment_matches):
    for segment in segment_matches:
        if not segment.number in scouting:
            scouting[segment.number] = {}
        match_scouting = scouting[segment.number]
        for team in segment.teams:
            if not team in match_scouting:
                match_scouting[team] = (0.0, 0.0)
    
#end get_non_stack_collab_probs and sub-functions
