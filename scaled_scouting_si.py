# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:13:22 2017

@author: rober
"""

#import math

#import numpy as np

import utils as ut
#import stacking_indiv as si
import Algorithm as al

START_MATCH = 20

def get_bernoulli_stack_indiv_distrs(matches, scouting):
    return get_stack_indiv_distrs(matches, scouting, fit=ut.fit_bernoulli, one_each=True)

#def one_each_bound(one_each):
#    return lambda m, s, f=ut.fit_truncated_normal_distr: get_stack_indiv_distrs(m, s, f, one_each)

fit_with_upper = lambda c, verbose=False: ut.fit_truncated_normal_distr(c, verbose=verbose, upper_limit=True)
fit = ut.fit_truncated_normal_distr

def get_stack_indiv_distrs(matches, scouting, fit=fit, one_each=False):
#    check_team = 'frc6002'
#    
    contrs_from_teams = {}
    all_teams = []
    
    in_matches = {}
    for match in matches:
        if match.number >= START_MATCH:
            if one_each:
                if hasattr(match, 'amount') and match.amount == len(match.teams):
                    for team in match.teams:
                        if not team in contrs_from_teams:
                            contrs_from_teams[team] = []
                        contrs_from_teams[team].append(1)
                else:
                    if match.number in scouting:
                        match_scouting = al.filter_match_scouting(scouting[match.number], match.teams)
                        for team in match_scouting:
                            if not team in contrs_from_teams:
                                contrs_from_teams[team] = []
                            contrs_from_teams[team].append(match_scouting[team])
            else:
                #print('match.teams: ' + match.teams.__str__())
                if match.number in scouting:
                    s_total = 0
                    match_scouting = al.filter_match_scouting(scouting[match.number], match.teams)
    #                if check_team in match.teams:
    #                    print(match.number.__str__() + ' ' + match_scouting.__str__())
                    all_scouted = True
                    for team in match.teams:
                        if not team in in_matches:
                            in_matches[team] = []
                        #in_matches[team].append(match.number)
                        
                        if not team in all_teams:
                            all_teams.append(team)
                        if team in match_scouting:
                            s_total += match_scouting[team]
                        else:
                            all_scouted = False
                    if all_scouted:
                        for team in match.teams:
                            in_matches[team].append(match.number)
                            if not team in contrs_from_teams:
                                contrs_from_teams[team] = []
                                
                            amount = match.amount if hasattr(match, 'amount') else s_total
                            
                            if hasattr(match, 'minimum'):
                                if s_total < match.minimum:
                                    amount = match.minimum
                            if hasattr(match, 'maximum'):
                                if s_total > match.maximum:
                                    amount = match.maximum
                            
                            if s_total == 0:
                                if amount == 0:
                                    contrs_from_teams[team].append(0)
                            else:
                                contrs_from_teams[team].append(match_scouting[team] * amount / s_total)
    
    for match_num in scouting:
        if match_num >= START_MATCH:
            match_scouting = scouting[match_num]
            for team in match_scouting:
                if not team in all_teams:
                    all_teams.append(team)
                if (not team in in_matches) or not match_num in in_matches[team]: 
                    if not team in contrs_from_teams:
                        contrs_from_teams[team] = []
                    contrs_from_teams[team].append(match_scouting[team])
    
    distrs_from_team = {}
    for team in all_teams:
        contrs = contrs_from_teams.get(team, [0])
#        if team == check_team:
#            print(contrs)
#            print('')
        distrs_from_team[team] = fit(contrs, verbose=False)
#        if team == check_team:
#            print(distrs_from_team[team])
        
    return distrs_from_team