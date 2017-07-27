# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 19:41:00 2017

@author: rober
"""

import Algorithm as al

#get_non_stack_one_probs and sub-functions
def get_non_stack_one_probs(segment_matches, scouting): #scouting is a dict from match-numbers to a dict from teams to whether the team did the task; if the team didn't get a chance to do the task, it isn't in scouting
    result = {}
    for team in al.all_teams(segment_matches):
        #result[team] = random.random()
        result[team] = 0.5

    result = al.follow_target(result, segment_matches, non_stack_one_target, scouting, al.VERY_CLOSE_TO_ZERO)
    return result

def non_stack_one_target(team, segment_matches, scouting, contrs, __cache = {}):
    def error(prob):
        o_contrs = contrs.copy()
        o_contrs[team] = prob
        
        result = 0
        for match in segment_matches:
            if team in match.teams:
                match_scouting = al.filter_match_scouting(scouting[match.number], match.teams)
                #print(len(match_scouting).__str__())
                if len(match_scouting) == 0:
                    match_probs = []
                    for other_team in match.teams:
                        match_probs.append(o_contrs[other_team])
                    max_prob = max(match_probs)
                    result += (match.amount - max_prob) ** 2
                else:
                    scout_prob = 0
                    
                    for other_team in match_scouting:
                        if other_team in match.teams:
                            scout_prob = o_contrs[other_team]
                            result += (match_scouting[other_team] - scout_prob) ** 2
                    for other_team in match.teams:
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
    for match in segment_matches:
        if team in match.teams:
            segment_scouting = scouting[match.number]
            other_contrs = []
            max_prob = 0
            #if not team in segment_scouting:
            none_scouted = 1
            for other_team in match.teams:
                if not other_team == team:
                    if other_team in segment_scouting:
                        none_scouted = 0
                        max_prob = segment_scouting[other_team]
            if none_scouted:
                for other_team in match.teams:
                    if not other_team == team:
                        other_contrs.append(contrs[other_team])
                max_prob = max(other_contrs)
            if not max_prob in partitions:
               partitions.append(max_prob)
            if not max_prob in matches_from_maximums:
                matches_from_maximums[max_prob] = []
            if team in segment_scouting:
                team_scouted_matches.append(match)
                for other_team in match.teams:
                    if not other_team == team:
                        other_prob = contrs[other_team]
                        if not other_prob in partitions:
                            partitions.append(other_prob)
                        if not other_prob in matches_from_maximums:
                            matches_from_maximums[other_prob] = []
            else:
                matches_from_maximums[max_prob].append(match)

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
            
            for match in relevant_matches: #relevant_matches
                match_scouting = al.filter_match_scouting(scouting[match.number], match.teams)
                #den += 1
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
                    #print(match.__str__())
                    none_scouted = 1
                    for other_team in match.teams:
                        if not other_team == team:
                            if other_team in match_scouting:
                                none_scouted = 0
                                if maximum <= contrs[other_team]:
                                    num += contrs[other_team]
                                    den += 1
                    if none_scouted:
                        other_probs = []
                        for other_team in match.teams:
                            if not other_team == team:
                                other_probs.append(contrs[other_team])
                        max_other_prob = max(other_probs)
                        if prev_max >= max_other_prob:
                            num += match.amount
                            den += 1
        
            #print("num: " + num.__str__() + " den: " + len(relevant_matches).__str__() + " prob:" + prob.__str__())
            #print("")
            
            #if prev_max <= prob <= maximum:
            if den > 0:
                prob = num / den
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

    this_target = al.apply_rtm(this_target, den) #remove?

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