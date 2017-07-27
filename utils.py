# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 17:20:22 2017

@author: Robert Morton
"""

import math
from enum import Enum

import numpy as np
import scipy as sp

#import stacking_indiv as si

def get_segment_match_map(number, score_breakdown, teams, categories):
    result = {}
    for category in categories:
        result[category] = SegmentMatch(number, category, score_breakdown[category.tba_name], teams)
    return result

def norm_a_to_b(mean, stdev, a, b):
    if a > b:
        raise RuntimeError("a: " + a.__str__() + " b: " + b.__str__())
    
    if stdev == 0:
        if a <= mean <= b:
            return 1
        return 0
        
    a = (a-mean) / stdev
    b = (b-mean) / stdev
    return 0.5 * (math.erf(b) - math.erf(a))

def get_normal_distr(mean, stdev, lower_limit=None, upper_limit=None):
    if stdev == 0:
        return {mean: 1.0}
    
    maximum = mean + 1 * stdev
    if upper_limit != None:
        maximum = min(maximum, upper_limit)
        
    minimum = 0#mean - 2 * stdev
    if lower_limit != None:
        minimum = max(minimum, lower_limit)
    
    minimum = max(-0.5, minimum)
    scores = []
    for i in range(0, math.ceil(maximum) + 1):
        scores.append(i)
    result = {}
    probs = []
    
    for score in scores:
        min_amount = max(minimum, score - 0.5)
        max_amount = min(maximum, score + 0.5)
        if min_amount < max_amount:
            prob = norm_a_to_b(mean, stdev, min_amount, max_amount)
            probs.append(prob)
            result[score] = prob
    total = math.fsum(probs)
    for prob in result:
        result[prob] = result[prob] / total

    return result

def amount_histo_from_contrs(contrs):
    """Return a histogram of the amounts scored."""
    
    amount_histo = {}
    for contr in contrs:
        floored = math.floor(contr)
        ceilinged = math.ceil(contr)
        
        proportion = contr - floored
        if not floored in amount_histo:
            amount_histo[floored] = 0
        if not ceilinged in amount_histo:
            amount_histo[ceilinged] = 0
        
        amount_histo[floored] += 1 - proportion
        amount_histo[ceilinged] += proportion
    for amount in amount_histo:
        amount_histo[amount] /= len(contrs)
        
    return amount_histo

def fit_truncated_normal_distr(contrs, upper_limit = False, verbose=False):
#    def negative_likelihood(params):
#        u = params[0]
#        o = params[1]
#        
#        distr = si.get_normal_distr(u, o)
#        
#        likelihood = 1
#        for contr in contrs:
#            likelihood *= distr.get(contr, 0)
#            
#        return -likelihood

#    real_u = np.mean(np.array(contrs, dtype=np.float64))
#    real_o = np.std(np.array(contrs, dtype=np.float64))

#    amount_histo = {}
#    for contr in contrs:
#        floored = math.floor(contr)
#        ceilinged = math.ceil(contr)
#        
#        proportion = contr - floored
#        if not floored in amount_histo:
#            amount_histo[floored] = 0
#        if not ceilinged in amount_histo:
#            amount_histo[ceilinged] = 0
#        
#        amount_histo[floored] += 1 - proportion
#        amount_histo[ceilinged] += proportion
#    for amount in amount_histo:
#        amount_histo[amount] /= len(contrs)

    amount_histo = amount_histo_from_contrs(contrs)

    def cost(params):
        u = params[0]
        o = params[1]
        m = None
        if upper_limit:
            m = params[2]
            print('m:', m)
        
        if u<0  or o<0:
            return math.inf
        
        if upper_limit:
            distr = get_normal_distr(u, o, upper_limit=m)
        else:
            distr = get_normal_distr(u, o)
        
        all_amounts = []
        all_amounts.extend(amount_histo.keys())
        all_amounts.extend(distr.keys())
        
        squared_error = 0
        
        for amount in all_amounts:
            observed_prob = amount_histo.get(amount, 0)
            predicted_prob = distr.get(amount, 0)
            
            squared_error += (observed_prob - predicted_prob) ** 2
            
        return squared_error
    
#        mean = 0
#        for amount in distr:
#            mean += amount*distr[amount]
#        
#        stdev = 0
#        for amount in distr:
#            stdev += ((amount-mean)**2)*distr[amount]
#        stdev = math.sqrt(stdev)
#        
#        return (mean - real_u)**2 + (stdev - real_o)**2
    
    u = np.mean(np.array(contrs, dtype=np.float64))
    o = max(contrs) - min(contrs)
    m = u + 2*o
    if upper_limit:
        params = (u, o, m)
    else:
        params = (u, o)
    params = sp.optimize.minimize(cost, params, method='bfgs').x
    
    if verbose:
        print('params: ' + params.__str__())
    return get_normal_distr(params[0], params[1])

def fit_bernoulli(contrs, rtm=False, verbose=False):
    num = sum(contrs) + 1 if rtm else sum(contrs)
    den = len(contrs) + 2 if rtm else len(contrs)
    return {0: (den - num)/den, 1: num/den}

def mult_mean_and_stdev(m0, s0, m1, s1):
    is_s0 = s0**-2
    is_s1 = s1**-2
    m = (is_s0*m0 + is_s1*m1)/(is_s0 + is_s1)
    v0 = s0**2
    v1 = s1**2
    s = math.sqrt(v0*v1 / (v0 + v1))
    
    return m, s

def prop_const(m0, s0, m1, s1):
    num = math.e ** -((m0 - m1)**2 / (s0**2 + s1**2))
    den = math.sqrt(math.pi)*s0*s1*math.sqrt(s0**-2 + s1**-2)
    return num / den
    
def positive_end_integral(m, s):
    return (s + s*math.erf(m/s))/(2*s)

def get_sum_possibilities_and_probs(norms, total):
    all_allocs = get_all_allocations(total, len(norms))
    probs = {}
    for i in range(0, len(norms)):
        c, s = norms[i]
        prop = positive_end_integral(c, s)
        n_map = {}
        for contr in range(0, total+1):
            prob = norm_a_to_b(math.max(0, contr-0.5), contr+0.5)/prop
            n_map[contr] = prob
        probs[i] = n_map
    result = {}
    for alloc in all_allocs:
        prob = 1
        for i in range(0, len(alloc)):
            num = alloc[i]
            prob *= probs[i][num]
        result[tuple(alloc)] = prob
    return result
    
def get_all_allocations(points, bins, __cache = {}):
    if (points, bins) in __cache:
        return __cache[points, bins]
    
    if bins == 0:
        if points == 0:
            return [[]]
        return []
    
    result = []
    do_print = lambda bins, i: print(" "*(10-bins) + i.__str__()) if bins >= 5 else lambda bins, i: 1
    for i in range(0, points + 1):
        #if verby:
            #print(" "*(10-bins) + i.__str__())
        do_print(bins, i)
        rest = points - i
        one_less_alls = get_all_allocations(rest, bins - 1)
        for allo in one_less_alls:
            result.append([i] + allo)
            
    __cache[points, bins] = result
            
    return result

class Category:

    CATEGORIES_FROM_TBA_NAMES = {}
    PRETTY_FROM_TBA = {}
    TBA_FROM_PRETTY = {}
    
    def __init__(self, match_phase, pretty_name, tba_name):
        
        if tba_name in Category.CATEGORIES_FROM_TBA_NAMES:
            raise RuntimeError("tba_name already taken: " + Category.CATEGORIES_FROM_TBA_NAMES[tba_name].__str__())
        Category.CATEGORIES_FROM_TBA_NAMES[tba_name] = self
        Category.PRETTY_FROM_TBA[tba_name] = pretty_name
        Category.TBA_FROM_PRETTY[pretty_name] = tba_name
        
        self.match_phase = match_phase
        self.pretty_name = pretty_name
        self.tba_name = tba_name
        

    def __eq__ (self, other):
        if type(other) !=  type(self):
            return False
        return self.tba_name == other.tba_name
        
    def __neq__ (self, other):
        return not self == other

    def __hash__ (self):
        return hash((self.tba_name))

    def __repr__(self):
        return self.tba_name
        
    def __str__(self):
        return self.tba_name

class MatchPhase(Enum):
    AUTON = 0
    TELEOP = 1
    BOTH = 2

class SegmentMatch:

    def __init__(self, number, category, amount, teams, minimum=None, maximum=None):
        self.number = number
        self.category = category
        if amount != None:
            self.amount = amount
        self.teams = teams
        if minimum != None:
            self.minimum = minimum
        if maximum != None:
            self.maximum = maximum

    def __eq__(self, other):
        if other == None:
            return False
        
        attrs = set(self.__dict__.keys())
        other_attrs = set(other.__dict__.keys())
        
        if attrs != other_attrs:
            return False
        
        for attr in attrs:
            if self.__dict__[attr] != other.__dict__[attr]:
                return False
        
        return True
#        return self.number == other.number and self.category == other.category and self.amount == other.amount and self.teams == other.teams

    def __neq__(self, other):
        return not self == other

    def __repr__(self):
        return "(#" + self.number.__repr__() + " " + self.teams.__repr__() + " " + self.category.__repr__() + " " + self.amount.__repr__() + ")"

    def __str__(self):
        return self.__repr__()
