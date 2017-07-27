# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 13:40:16 2017

@author: rober
"""

import Algorithm as al
import stacking_indiv as si
import utils as ut
import castle as cs

SMALL = 0.01

def get_stack_indiv_distrs(matches, scouting, ratio_stdev):
    '''
    scouting: match_num -> team -> score
    '''
    
    c_s = si.get_stack_indiv_averages_and_stdevs(matches, {})
    n_p = c_s_to_n_p(c_s)
    new_n_p = get_after_iteration(n_p, matches, scouting, ratio_stdev)
    while difference(n_p, new_n_p) >= SMALL:
        n_p = new_n_p.copy()
        new_n_p = get_after_iteration(new_n_p, matches_scouting, ratio_stdev)
      
N_CHANGES = [-0.01, 0.01]
P_CHANGES = [-0.01, 0.01]

def get_after_iteration(n_p, matches, scouting, ratio_stdev):
    n_p = n_p.copy()
    for team in n_p:
        n = c_s[0]
        p = c_s[1]
        
        new_n_p = n_p
        likelihood = get_likelihood(new_n_p, matches, scouting, ratio_stdev)
        for n_change in N_CHANGES:
            new_n = n + n_change
            possible_n_p = new_n_p
            possible_n_p[team] = [new_n, p]
            possible_likelihood = get_likelihood(possible_c_s, matches, scouting, ratio_stdev)
            if possible_likelihood > likelihood:
                likelihood = possible_likelihood
                n_c_s = possible_c_s
        
        likelihood = get_likelihood(new_n_p, matches, scouting, ratio_stdev)
        
        n = new_n_p[0]
        
        for p_change in P_CHANGES:
            new_p = p + p_change
            possible_n_p = new_n_p
            possible_n_p[team] = [c, new_p]
            possible_likelihood = get_likelihood(possible_n_p, matches, scouting, ratio_stdev)
            if possible_likelihood > likelihood:
                likelihood = possible_likelihood
                new_n_p = possible_n_p
                
        p = new_n_p[1]
        n_p[team] = [n, p]
        
    return n_p

def get_likelihood(c_s, matches, scouting, ratio_stdev):
    result = 1
    scouting_not_accounted_for = scouting.copy()
    for match in matches:
        score = match.amount
        
        m_scouting = al.filter_match_scouting(scouting[match.number], match.teams)
        
#        tot_c = 0
#        tot_s = 0
#        for team in match.teams:
#            c, s = c_s[team]
#            tot_c += c
#            tot_s += s
#            
#        likelihood_for_total = si.norm_a_to_b(tot_c, tot_s, score-0.5, score+0.5)
#        

#        prop = 1
#        for team in match.teams:
#            c, s = c_s[team]
#            if team in m_scouting:
#                scouting_not_accounted_for[match.number].pop(team, None)
#                scouted = m_scouting[team]
#                s_c, s_s = scouted, scouted * ratio_stdev
#                prop *= ut.prop_const(c, s, s_c, s_s)
#                c, s = ut.mult_mean_and_stdev(c, s, s_c, s_s)

        possibilities = cs.all_allocations(score, len(match.teams))
        tot_prob = 0
        for poss in possibilities:
            
def c_s_to_n_p(c_s):
    result = {}
    for team in c_s:
        c = c_s[team][0]
        s = c_s[team][1]
        n = c + 3*s
        p = c / n
        result[team] = n, p
              
    return result