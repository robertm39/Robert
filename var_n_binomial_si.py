# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 19:24:44 2017

@author: rober
"""

import math

import scipy as sc
import numpy as np

import Algorithm as al
import stacking_indiv as si
import utils

MAX_STDEVS = 100

def bound(x, mean, stdev, max_stdevs):
    if x < 0:
        return 0
    
    if x < mean-stdev*max_stdevs:
        return mean-stdev*max_stdevs
    
    if x > mean+stdev*max_stdevs:
        return mean+stdev*max_stdevs
    
    return x

def trunc_norm_a_to_b(mean, stdev, max_stdevs, a, b):
    if stdev < 0:
        stdev = 0
    
    a = bound(a, mean, stdev, max_stdevs)
    b = bound(b, mean, stdev, max_stdevs)

    #print("a: " + a.__str__() + " b: " + b.__str__())
    
    return utils.norm_a_to_b(mean, stdev, a, b) / utils.norm_a_to_b(mean, stdev, max(0, mean-stdev*max_stdevs), mean+stdev*max_stdevs)

def index_from_team(team, all_teams):
    #print(all_teams.index(team) * 2)
    return all_teams.index(team) * 2

#def get_p(team, all_teams, params):
#    return params[index_from_team(team, all_teams)] / get_m(team, all_teams, params)

def get_m(team, all_teams, params):
#    print('getting m: ' + params.__str__())
#    print('team: ' + team.__str__())
#    print('all_teams: ' + all_teams.__str__())
    return max(0, params[index_from_team(team, all_teams)])

def get_u(team, all_teams, params):
#    print('getting u: ' + params.__str__())
#    print('team: ' + team.__str__())
#    print('all_teams: ' + all_teams.__str__())
    return max(0, params[index_from_team(team, all_teams) + 1])

def sensible_value_prior(params):
    if min(params) < 0:
        return 99999999999999999999999999
        
    return math.log(1) #0

def bound_with_ratio_stdev(ratio_stdev):
    return lambda m, s: get_team_prob_distrs(m, s, ratio_stdev)

def get_team_prob_distrs(matches, scouting, ratio_stdev, prior=sensible_value_prior):
    all_teams = al.all_teams(matches, scouting)
    all_teams.sort()
    params = []
    max_contr = si.get_max_score(matches)
    for team in all_teams:
        #params.append(max_contr)
        params.append(max_contr)
        params.append(max_contr*2)
        
    params = np.array(params, dtype=np.float)
    #params = optimize(lambda params: get_negative_likelihood(matches, scouting, all_teams, params, ratio_stdev)+prior(params), params)
    params = sc.optimize.minimize(lambda params: get_negative_likelihood(matches, scouting, all_teams, params, ratio_stdev)+prior(params), params, method='BFGS').x
    #return params #finish
    pre_distrs = {}
    print('got to here')
    for team in all_teams:
        m = get_m(team, all_teams, params)
        u = get_u(team, all_teams, params)
        print(team + ' m:' + m.__str__() + ' u:' + u.__str__())
        pre_distrs[team] = utils.get_normal_distr(m, u)
    
#    name = matches[0].category.tba_name
#    distrs = {}
#    for team in pre_distrs:
#        team_distrs = {}
#        for value in pre_distrs[team]:
#            prob = pre_distrs[team][value]
#            team_distrs[value] = prob
#        sub_distrs = {}
#        sub_distrs[name] = team_distrs
#        #if name == "auton low goal":
#        #    print(team_distrs)
#        distrs[team] = sub_distrs
    return pre_distrs
    
#optimization
def optimize(get_cost, params, intervals=(5, 1, 0.5, .1, 0.05, .01)):
    params = params.copy()
    for interval in intervals:
        print(interval)
        params = optimize_with_interval(get_cost, params, interval)
        print(params)
        print('')
    return params

def optimize_with_interval(get_cost, params, interval):
    params = params.copy()
    changed = True
    while changed:
        print(params)
        print('')
        changed = False
        for index in range(0, len(params)):
            cost = get_cost(params)
            plus_params = with_change(params, index, interval)
            minus_params = with_change(params, index, -interval)
              
            minus_cost = get_cost(minus_params)
            plus_cost = get_cost(plus_params)
            
            #print('cost: ' + cost.__str__() + ' minus_cost: ' + minus_cost.__str__() + ' plus_cost: ' + plus_cost.__str__())
            
            if minus_cost < cost:
                changed = True
                if plus_cost < minus_cost:
                    params[index] += interval
                else:
                    params[index] -= interval
            else:
                if plus_cost < cost:
                    changed = True
                    params[index] += interval
    return params
        
def with_change(params, index, change):
    result = params.copy()
    result[index] = params[index] + change
    return result
#end optimization

#likelihood and prior functions
def get_negative_likelihood(matches, scouting, all_teams, params, ratio_stdev):
    likelihood = 0
    for match in matches:
        likelihood += get_match_likelihood(match, scouting, all_teams, params, ratio_stdev)
    #print(likelihood)
    return -likelihood

def get_match_likelihood(match, scouting, all_teams, params, ratio_stdev):
    amount = match.amount
    result = 0
    m_scouting = scouting.get(match.number, {})
    
    for alloc in utils.get_all_allocations(amount, len(match.teams)):
        #print('alloc: ' + alloc.__str__())
        
        i = 0
        alloc_prob = 1
        for team in match.teams:
            team_score = alloc[i]
            #print('team_score: ' + team_score.__str__())
            
            #p = get_p(team, all_teams, params)
            m = get_m(team, all_teams, params)
            u = get_u(team, all_teams, params)
            
            #print('p: ' + p.__str__() + ' m: ' + m.__str__() + ' u: ' + u.__str__())
            
            score_prob = trunc_norm_a_to_b(m, u, MAX_STDEVS, team_score-0.5, team_score + 0.5)
            
#            minimum_n = math.floor(m - u*MAX_STDEVS)
#            maximum_n = math.ceil(m + u*MAX_STDEVS)
#            
#            score_prob = 0
#            for n in range(max(minimum_n, 0),  maximum_n + 1):
#                #print('n: ' + n.__str__())
#                n_prob = trunc_norm_a_to_b(m, u, MAX_STDEVS, n-0.5, n+0.5)
#                #print('n_prob: ' + n_prob.__str__())
#                score_prob += n_prob*di.binomial(n, p, team_score)
#                #print('score_prob: ' + score_prob.__str__())
                
            scouting_prob = 1
            if team in m_scouting:
                scouting_stdev = abs(team_score * ratio_stdev)
                
                scouted = m_scouting[team]
                scouting_prob = trunc_norm_a_to_b(team_score, scouting_stdev, 10, scouted-0.5, scouted+0.5)
                
            team_prob = score_prob * scouting_prob
            alloc_prob *= team_prob
            
            i += 1
            
        result += alloc_prob
        
    #return result
    result = max(result, 0.000000000000001)
    return math.log(result)
#end likelihood and prior functions