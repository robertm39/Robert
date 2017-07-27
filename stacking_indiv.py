# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 19:37:05 2017

This module contains the OPR distribution getter.

@author: Robert Morton
"""
import math
import numpy

import Algorithm as al
import utils as ut

def get_stack_indiv_distrs(matches, scouting): #distrs is a map from teams to maps from maps from names to outcomes to probs
    """Return a map from teams to probability distributions.
    
    Arguments:
        matches -- the matches
        scouting -- a dict from match numbers to dicts from teams to tuples of minimums, maximums and certainties.
    """    
    averages = get_stack_indiv_means(matches, scouting)
    fill_in_stacking_indiv_scouting(scouting, matches)
    
    stdevs = get_stack_indiv_stdevs(averages, matches, scouting)
    pre_distrs = get_normal_distrs(averages, stdevs)
    return pre_distrs

def get_stack_indiv_means_and_stdevs(segment_matches, scouting): #for testing algorithms
    """Return a map from teams to tuples of means and stdevs."""
    means = get_stack_indiv_means(segment_matches, scouting)
    stdevs = get_stack_indiv_stdevs(means, segment_matches, scouting)
    result = {}
    for team in means:
        result[team] = (means[team], stdevs[team])
    return result

def get_normal_distrs(means, stdevs):
    """Return a dict from teams to a dict from amounts to probabilities.
    
    Arguments:
        means -- a dict from teams to means
        stdevs --a dict from teams to stdevs
    """
    distrs = {}
    for team in means:
        mean = means[team]
        stdev = stdevs[team]
        distrs[team] = ut.get_normal_distr(mean, stdev)
    return distrs

#get_stdevs and sub-functions
def get_stack_indiv_stdevs(means, matches, scouting):
    """Return a dict from teams to stdevs.
    
    Arguments:
        means -- a dict from teams to means
        matches -- a list of matches
        scouting -- a dict from match numbers to dicts from teams to tuples of minimums, maximums and certainties.
    """
    team_amounts = {}
    for match in matches:
        team_scores = get_team_scores(means, match, scouting)
        for team in team_scores:
            if not team in team_amounts:
                team_amounts[team] = [team_scores[team]]
            else:
                team_amounts[team].append(team_scores[team])
    team_stdevs = {}
    for team in team_amounts:
        squ_err = 0
        mean = numpy.mean(team_amounts[team])
        for amount in team_amounts[team]:
            floored = math.floor(amount)
            lower = amount - floored
            upper = 1 - lower

            squ_err += (1 - lower) * (floored - mean) ** 2
            squ_err += (1 - upper) * (floored + 1 - mean) ** 2
        team_stdevs[team] = math.sqrt(squ_err / len(team_amounts[team]))
    return team_stdevs

def get_team_scores(means, match, scouting):
    """Return a dict from teams to amounts scored.
    
    Arguments:
        means -- a dict from teams to means
        match -- the match the teams played in
        scouting -- a dict from match numbers to dicts from teams to tuples of minimums, maximums and certainties.
    """
    team_scores = {}
    total = 0
    match_scouting = scouting[match.number]

    min_score = 0
    max_score = 0
    below_min = 1
    above_max = 1
    for team in match.teams:
        team_scouting = match_scouting[team]
        minimum = team_scouting[0][0]
        min_cert = team_scouting[0][1]
        if min_cert < 1:
            below_min = 0

        maximum = team_scouting[1][0]
        max_cert = team_scouting[1][1]
        if max_cert < 1:
            above_max = 0

        min_score += minimum
        max_score += maximum

    if min_score <= match.amount:
        below_min = 0
    if match.amount <= max_score:
        above_max = 0

    if below_min or above_max:
        raise RuntimeError("below_min: " + below_min.__str__() + " above_max: " + above_max.__str__())

    total = 0
    for team in match.teams:
        team_scouting = match_scouting[team]
        contr = means[team]
        duration = team_scouting[2]
        if not duration == 0:
            team_score = apply_scouting(contr * duration, team_scouting)
            team_scores[team] = team_score
            total += team_score
            
    if total == 0:
        for team in team_scores:
            team_scores[team] = match.amount / 3
        #print(team_scores)
        return team_scores  
    
    going = 1
    while going:
        ratio = match.amount / total
        total = 0
        for team in team_scores:
            team_scouting = match_scouting[team]
            team_score = apply_scouting(team_scores[team] * ratio, team_scouting)
            team_scores[team] = team_score
            total += team_score

        if abs(total - match.amount) <= al.ULTRA_CLOSE_TO_ZERO:
            going = 0
                
    return team_scores
        
#end get_stdevs and sub-functions
def fill_in_stacking_indiv_scouting(scouting, matches): #scouting: team -> ( (min, cert), (max, cert), duration)
    """Fill in the missing scouting entries.
    
    Arguments:
        scouting -- a dict from match numbers to dicts from teams to tuples of minimums, maximums and certainties.
        matches -- the matches
    """
    for match in matches:
        number = match.number
        if not number in scouting:
            scouting[number] = {}
        segment_scouting = scouting[number]
        for team in match.teams:
            if not team in segment_scouting:
                segment_scouting[team] = ((0.0, 1.0), (0.0, 0.0), 1.0)
                #segment_scouting[team] = (0.0, 0.0, 1.0)
            #else:
            #    team_scouting = segment_scouting[team]
                    
#get_stack_indiv_averages and sub-functions
def get_stack_indiv_means(matches, scouting):
    """Return a dict from teams to means.
    
    Arguments:
        matches -- the matches
        scouting -- a dict from match numbers to dicts from teams to tuples of minimums, maximums and certainties.
    """
    
    result = {}
    average = get_average_mean(matches)
    for team in al.all_teams(matches):
        result[team] = average

    return al.follow_target(result, matches, stacking_indiv_target, scouting, al.CLOSE_TO_ZERO)

def get_target_score_and_weight(team, team_scouting, not_acc_for):
    """Return the target score for the team, and how much to weigh it.
    
    Arguments:
        team -- the team
        team_scouting -- a tuple of minimums, maximums and certainties
        not_acc_for -- how much of the score of the match isn't accounted for by other robots
    """
    duration = team_scouting[2]
    if duration == 0:
        return (0, 0)
        
    pre_target = not_acc_for / duration
    return (apply_scouting(pre_target, team_scouting), duration)

def apply_scouting(score, team_scouting):
    """Return a score based on the passed score that is consistent with the scouting.
    
    Arguments:
        score -- the score to base the return value on
        team_scouting -- a tuple of minimums, maximums and certainties
    """
    minimum = team_scouting[0][0]
    min_cert = team_scouting[0][1]
    maximum = team_scouting[1][0]
    max_cert = team_scouting[1][1]

    if score < 0:
        return 0
    if minimum <= score <= maximum:
        return score
    elif score < minimum:
        #print("minimum: " + minimum.__str__() + " min_cert: " + min_cert.__str__() + " score: " + score.__str__())
        return min_cert * minimum + (1 - min_cert) * score
    elif maximum < score:
        return max_cert * maximum + (1 - max_cert) * score

def predict_team_score(team, team_scouting, mean):
    """Return a predicted team score.
    
    Arguments:
        team -- the team to predict the score of
        team_scouting -- a tuple of minimums, maximums and certainties
        mean -- the team's mean score
    """
    duration = team_scouting[2]
    pre_score = mean * duration
    return apply_scouting(pre_score, team_scouting)
    
def not_accounted_for(team, match, match_scouting, means):
    """Return how much of the score of the match isn't accounted for by the team.
    
    Arguments:
        team -- the team
        match -- the match
        match_scouting --  a dict from teams to tuples of minimums, maximums and certainties
        means --  a map from teams to means
    """
    accounted_for = 0
    for other_team in match.teams:
        if other_team != team:
            other_team_scouting = match_scouting[other_team]
            accounted_for += predict_team_score(other_team, other_team_scouting, means[other_team])
    return match.amount - accounted_for

def stacking_indiv_target(team, matches, scouting, means):#scouting: team -> ( (min, cert), (max, cert), duration)
    """Return the mean to change the team's mean to.
    
    Arguments:
        team -- the team to return the new mean on
        matches -- the matches
        scouting -- a dict from match numbers to dicts from teams to tuples of minimums, maximums and certainties.
        means -- a map from teams to means
    """    

    def match_target(team, match, match_scouting, means): #returns a tuple of a target-number and a weight-number.
        """Return the target for one match.
        
        Arguments:
            team -- the team to return the target of
            match -- the match
            match_scouting -- a dict from teams to tuples of minimums, maximums and certainties.
            means -- a map from teams to means
        """    
        not_acc_for = not_accounted_for(team, match, match_scouting, means)
        team_scouting = match_scouting[team]
        return get_target_score_and_weight(team, team_scouting, not_acc_for)
    
    match_targets = []
    for match in matches:
        if team in match.teams:
            match_targets.append(match_target(team, match, scouting[match.number], means))
    total_weight = 0
    total_targets = 0
    for match_target in match_targets:
        total_targets += match_target[0]
        total_weight += match_target[1]
    return total_targets / total_weight            

def get_max_score(matches):
    """Return the highest amount in the passed matches."""
    result = 0
    for match in matches:
        result =  max((result, match.amount))
    return result

def get_average_mean(matches):
    """Return the average mean for all the matches."""
    total = 0.0
    for match in matches:
        total += match.amount
    return total / 3.0 / len(matches)
#end get_stack_indiv_averages and sub-functions
