# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 20:51:03 2017

@author: rober
"""

import heapq
import bisect
import time

import blist
#from skiplist import IndexableSkiplist

def combine_cats_and_teams(distrs_from_cats_from_teams): #tested
    result = {}
    for team in distrs_from_cats_from_teams:
        distrs_from_cats = distrs_from_cats_from_teams[team]
        for cat in distrs_from_cats:
            result[(team, cat)] = distrs_from_cats[cat]
    return result

def zip_dict(dictionary, keys):
    result = []
    for key in keys:
        result.append((key, tuple(dictionary[key])))
    return tuple(result)

def get_prob(index_outcome, prob_lists_from_teams_and_cats, teams_and_cats, _cache={}):
    key = (tuple(index_outcome), zip_dict(prob_lists_from_teams_and_cats, teams_and_cats), tuple(teams_and_cats))
    if key in _cache:
        return _cache[key]
    
    result = 1
    
    team_and_cat_index = 0
    #teams_and_cats = list(prob_lists_from_teams_and_cats.keys())
    for index in index_outcome:
        probs = prob_lists_from_teams_and_cats[teams_and_cats[team_and_cat_index]]
        result *= probs[index]
        team_and_cat_index += 1
        
    _cache[key] = result
    return result

def get_outcome_from_index_outcome(index_outcome, amount_lists_from_teams_and_cats, teams_and_cats):
    result = {}
    
    team_and_cat_index = 0
    #teams_and_cats = list(amount_lists_from_teams_and_cats.keys())
    for index in index_outcome:
        team_and_cat = teams_and_cats[team_and_cat_index]
        result[team_and_cat] = amount_lists_from_teams_and_cats[team_and_cat][index]
        team_and_cat_index += 1
    
    return result

def unpack_team_and_cat_outcome(distrs_from_teams_and_cats):
    result = {}
    for team_and_cat in distrs_from_teams_and_cats:
        team, cat = team_and_cat
        if not team in result:
            result[team] = {}
        result[team][cat] = distrs_from_teams_and_cats[team_and_cat]
    return result

def get_one_less_index_outcomes(index_outcome, prob_lists_from_teams_and_cats, teams_and_cats):
    result = []

#    print(index_outcome)
    
    list_index = 0
    for index, team_and_cat in zip(index_outcome, teams_and_cats):
        prob_list = prob_lists_from_teams_and_cats[team_and_cat]
        if index < len(prob_list) - 1:
            add = list(index_outcome)
            add[list_index] += 1
            result.append(tuple(add))
            
        list_index += 1
       
#    print('one less:')
#    for outcome in result:
#        print(outcome)
#    print('')
        
    return result

def get_amount_and_prob_lists(distrs_from_teams_and_cats, teams_and_cats):
    amount_lists_from_teams_and_cats = {}
    prob_lists_from_teams_and_cats = {}
    
    #print(distrs_from_teams_and_cats)
    
    for team_and_cat in teams_and_cats:
        distrs = distrs_from_teams_and_cats[team_and_cat]
        amounts = list(distrs.keys())
        amounts.sort(key=lambda k: -distrs[k])
        amounts = tuple(amounts)
        prob_list = tuple([distrs[a] for a in amounts])
        amount_lists_from_teams_and_cats[team_and_cat] = amounts
        prob_lists_from_teams_and_cats[team_and_cat] = prob_list
        
    return amount_lists_from_teams_and_cats, prob_lists_from_teams_and_cats

def dominates(index_outcome_1, index_outcome_2, _cache={}):
    key = (tuple(index_outcome_1), tuple(index_outcome_2))
    if key in _cache:
        return _cache[key]
    
    for index_1, index_2 in zip(index_outcome_1, index_outcome_2):
        if index_2 < index_1:
            _cache[key] = False
            return False
        
    _cache[key] = True
    return True


def in_list_dominates(index_outcomes, index_outcome):
#    key = (tuple([tuple(io) for io in index_outcomes]), tuple(index_outcome))
#    if key in _cache:
#        return _cache[key]
#    
#    for dominator in index_outcomes:
#        if dominates(dominator, index_outcome):
##            _cache[key] = True
#            return True
#        
##    _cache[key] = False
    return index_outcome in index_outcomes
#    return False

def get_number_of_outcomes(distrs_from_cats_from_teams):
    result = 1
    for team in distrs_from_cats_from_teams:
        distrs_from_cats = distrs_from_cats_from_teams[team]
        for cat in distrs_from_cats:
            distr = distrs_from_cats[cat]
            result *= len(distr)
    return result

def outcome_iterator(distrs_from_cats_from_teams):
    #print('')
    #print(distrs_from_cats_from_teams)
    
    distrs_from_teams_and_cats = combine_cats_and_teams(distrs_from_cats_from_teams)
    teams_and_cats = list(distrs_from_teams_and_cats.keys())
    
    amount_lists_from_teams_and_cats, prob_lists_from_teams_and_cats = get_amount_and_prob_lists(distrs_from_teams_and_cats, teams_and_cats)
        
    
    most_likely_outcome = tuple([0]) * len(list(distrs_from_teams_and_cats.keys()))
    
    yield unpack_team_and_cat_outcome(get_outcome_from_index_outcome(most_likely_outcome, amount_lists_from_teams_and_cats, teams_and_cats))
    
    potential_outcomes = get_one_less_index_outcomes(most_likely_outcome, prob_lists_from_teams_and_cats, teams_and_cats)
    potential_outcomes.sort(key=lambda o: -get_prob(o, prob_lists_from_teams_and_cats, teams_and_cats))
    
    unsorted_potential_outcomes = set(potential_outcomes.copy())
    potential_outcomes = iter(potential_outcomes)#.__iter__()
#    i = 0
    
    multi_merge_iterator = MultiMergeIterator(lambda o: -get_prob(o, prob_lists_from_teams_and_cats, teams_and_cats), potential_outcomes)
    
    while True:
        try:
            most_likely_outcome = multi_merge_iterator.__next__()
            
            yield unpack_team_and_cat_outcome(get_outcome_from_index_outcome(most_likely_outcome, amount_lists_from_teams_and_cats, teams_and_cats))

            unsorted_potential_outcomes.remove(most_likely_outcome)

            new_outcomes = get_one_less_index_outcomes(most_likely_outcome, prob_lists_from_teams_and_cats, teams_and_cats)
            new_outcomes = [o for o in new_outcomes if not in_list_dominates(unsorted_potential_outcomes, o)]
            new_outcomes.sort(key=lambda o: -get_prob(o, prob_lists_from_teams_and_cats, teams_and_cats))

            for outcome in new_outcomes:
                unsorted_potential_outcomes.add(outcome)
            
            multi_merge_iterator.add_iterator(iter(new_outcomes))
        except StopIteration:
            raise StopIteration
        
    raise StopIteration
    
class Outcome:
    
    def __init__(self, index_outcome, probability):
        self.index_outcome = index_outcome
        self.probability = probability
        
    def __lt__(self, other):
        return self.probability < other.probability
    
    def __le__(self, other):
        return self.probability <= other.probability
    
    def __gt__(self, other):
        return self.probability > other.probability
    
    def __ge__(self, other):
        return self.probability >= other.probability
    
class IteratorWithData:
    
    def __init__(self, iterator, value, rank):
        self.iterator = iterator
        self.value = value
        self.rank = rank
        
    def set_value(self, value, key):
        self.value = value
        self.rank = key(value)
    
    def __cmp__(self, other):
        return self.rank - other.rank if (type(other) is IteratorWithData) else -other.__cmp__(self)

    def __lt__(self, other):
#        if type(self) is type(other):
        return self.rank < other.rank
#        return other.__gt__(self)
    
    def __le__(self, other):
#        if type(self) is type(other):
        return self.rank <= other.rank
#        return other.__ge__(self)
    
    def __eq__(self, other):
#        if type(self) == type(other):
        return self.rank == other.rank
#        return other == self
    
    def __ne__(self, other):
#        if type(self) == type(other):
        return self.rank < other.rank
#        return other >= self
    
    def __gt__(self, other):
#        if type(self) is type(other):
        return self.rank > other.rank
#        return other.__lt__(self)
    
    def __ge__(self, other):
#        if type(self) is type(other):
        return self.rank >= other.rank
#        return other.__le__(self)
    
class MultiMergeIterator:
    
    def __init__(self, key, *vars):
        self.key = key#lambda a: key(a[1])
        self.sort_key = lambda a: a.rank
        self.iterators = blist.sortedlist([])
        for iterator in vars:
            self.add_iterator(iterator)
#            try:
#                val = iterator.__next__()
#                self.iterators.append(IteratorWithData(iterator, val, self.key(val)))
#            except StopItera
            
#        self.iterators.sort(key=self.sort_key)
         
    def __next__(self):
        try:
            result = self.iterators[0].value
        except IndexError:
            raise StopIteration
        
        try:
            self.iterators[0].set_value(self.iterators[0].iterator.__next__(), self.key)
        except StopIteration:
            self.iterators.pop(0)
        
        if len(self.iterators) >= 2 and self.iterators[0].rank > self.iterators[1].rank:
            try:
                add = self.iterators[0]
                self.iterators.pop(0)
                self._add_iterator_with_state(add)
#                self.iterators = list(heapq.merge(self.iterators, [add], key=self.sort_key))
            except StopIteration:
                pass
            
        return result
    
    def _add_iterator_with_state(self, iterator):
        self.iterators.add(iterator)
#        bisect.insort_left(self.iterators, iterator)
#        self.iterators.insert(iterator)
    
    def add_iterator(self, iterator):
        try:
            val = iterator.__next__()
    #        sort_val = self.key(val)
            add = IteratorWithData(iterator, val, self.key(val))
            self._add_iterator_with_state(add)
        except StopIteration:
            pass
#        self.iterators.insert(add)
        
#        min_index = 0
#        max_index = len(self.iterators)
#        curr_index = max_index // 2
#        while min_index != max_index:
#            
#            print('min: ' + min_index.__str__() + ' max: ' + max_index.__str__() + ' curr: ' + curr_index.__str__())
#            
#            check = self.iterators[curr_index][2]
#            if sort_val < check:
#                max_index = curr_index
#            elif sort_val == check:
#                min_index = max_index = curr_index
#            else:
#                min_index = curr_index + 1
#                
#            curr_index = (max_index + min_index) // 2
#        
#        self.iterators.insert(curr_index, add)