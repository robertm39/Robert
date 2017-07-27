import random

import mc_utils as mcut

def combine_predictions(m1, m2):
    trials = m1[1] + m2[1]
    #print(trials)
    result = {}
    
    m1_ratio = m1[1] / trials
    #print("m1_ratio: " + m1_ratio.__str__())
    for match in m1[0]:
        if not match in result:
            result[match] = m1[0][match] * m1_ratio
        else:
            result[match] += m1[0][match] * m1_ratio

    m2_ratio = m2[1] / trials
    #print("m2_ratio: " + m2_ratio.__str__())
    for match in m2[0]:
        if not match in result:
            result[match] = m2[0][match] * m2_ratio
        else:
            result[match] += m2[0][match] * m2_ratio

    return result, trials

def get_team_from_team_map(team):
    #for t in team:
    #    return t
    return team
def get_teams_from_team_maps(teams):
    result = []
    for team in teams:
        result.append(get_team_from_team_map(team))
    return result

def get_probs_from_team_maps(teams):
    result = []
    for team in teams:
        result.append(teams[team])
    return result

#scenarios
def allocate_one_each(teams):
    pass

def get_extra_scenario(year, red_teams, blue_teams):
    if year == "2016":
        pass
#end scenarios

def get_prob(outcome, distrs_from_cats_from_teams):
    result = 1
    for team in outcome:
        for category in outcome[team]:
            amount = outcome[team][category]
            result *= distrs_from_cats_from_teams[team][category][amount]
    return result

def smart_predict_match_trials_bound(gen_trials, enum_trials):
    return lambda r, b, e, t, s, y: smart_predict_match(r, b, e, t, s, y, gen_trials=gen_trials, enum_trials=enum_trials)

def smart_predict_match(red_teams, blue_teams, evaluate_match, trials, scenario, year, gen_threshold=20000, enum_trials=None, gen_trials=None):
    team_maps = {}
    team_maps.update(red_teams)
    team_maps.update(blue_teams)
    
    amount_outcomes = mcut.get_number_of_outcomes(team_maps)
    
#    print('amount_outcomes: ' + amount_outcomes.__str__())
    
    if amount_outcomes <= gen_threshold:
        enum_trials = trials if enum_trials == None else enum_trials
        return enumerate_predict_match(red_teams, blue_teams, evaluate_match, enum_trials, scenario, year)
    
    gen_trials = trials if gen_trials == None else gen_trials
    return generic_predict_match(red_teams, blue_teams, evaluate_match, gen_trials, scenario, year)

def enumerate_predict_match(red_teams, blue_teams, evaluate_match, trials, scenario, year, __cache={}):
    o_red_teams = get_teams_from_team_maps(red_teams)
    o_blue_teams = get_teams_from_team_maps(blue_teams)
    matches = {}
    
    team_maps = {}
    team_maps.update(red_teams)
    team_maps.update(blue_teams)
    
    iterator = mcut.outcome_iterator(team_maps)
    key = (tuple(o_red_teams), tuple(o_blue_teams), scenario, year)
    #print(key)
    if key in __cache:
        iterator = __cache[key]
    else:
        __cache[key] = iterator
    tot_prob = 0
    for i in range(0, trials):
        try:
            outcome = iterator.__next__()
            #print(outcome)
            match = evaluate_match(outcome, o_red_teams, o_blue_teams, scenario)
            prob = get_prob(outcome, team_maps)
            tot_prob += prob
            if not match in matches:
                matches[match] = 0
            matches[match] += prob
        except StopIteration:
            break
        
    if tot_prob == 0:
        return ([], 0)
        
    for match in matches:
        matches[match] /= tot_prob
    
    #print(tot_prob)
    #print('')
    
    return matches, tot_prob

def all_outcomes(teams):
    pass

def generic_predict_match(red_teams, blue_teams, evaluate_match, trials, scenario, year):
    '''
    red_teams: (team -> (category -> (amount -> prob)))
    blue_teams:(team -> (category -> (amount -> prob)))
    evaluate_match: takes (team -> (category -> amount))
    trials: int
    '''

    #print("predict match")
    #print("red: " + red_teams.__str__() + " blue: " + blue_teams.__str__())
#    print('red: ' + red_teams.__str__())
    o_red_teams = get_teams_from_team_maps(red_teams)
    o_blue_teams = get_teams_from_team_maps(blue_teams)
    matches = {}
    #red_teams = get_probs_from_team_maps(red_teams)
    #blue_teams = get_probs_from_team_maps(blue_teams)
    
    teams = {}
    teams.update(red_teams)
    teams.update(blue_teams)
    #print(teams)

    #print(o_red_teams)
    for i in range(0, trials):
        outcome = random_outcome(teams)
        #for t in red_teams:
        #    o_red_teams.append(get_team_from_team_map(t))
        #for t in blue_teams:
        #    o_blue_teams.append(get_team_from_team_map(t))
        
        match = evaluate_match(outcome, o_red_teams, o_blue_teams, scenario)
        if not match in matches:
            matches[match] = 1
        else:
            matches[match] = matches[match] + 1
    for match in matches:
        matches[match] = matches[match] / trials

    return matches, trials

def random_outcome(teams): #checked
    '''
    teams: (team -> (category -> (amount -> prob)))
    returns (team -> (category -> amount))
    '''
    result = {}
    for team in teams:
        #actual_team = get_team_from_team_map(team)
        result[team] = random_team_outcome(teams[team])
    return result
        
def random_team_outcome(team): #checked
    '''
    team: (category -> (amount -> prob))
    returns (category -> amount)
    '''
    outcome = {}
    for category in team:
        probs = team[category]
        outcome[category] = random_category_outcome(probs)
    return outcome

def random_category_outcome(probs): #checked
    '''
    probs: (amount -> prob)
    return amount
    '''
    num = random.random()
    
#    check_cat = None
#    for category in probs:
#        check_cat = category
#    probs = probs[check_cat]
    
    for outcome in probs:
        #print(probs[outcome])
        if num < probs[outcome]:
            return outcome #return return return
        else:
            num -= probs[outcome]
