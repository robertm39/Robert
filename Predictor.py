import random

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

def predict_match(red_teams, blue_teams, evaluate_match, trials):
    '''
    red_teams: (team -> (category -> (amount -> prob)))
    blue_teams:(team -> (category -> (amount -> prob)))
    evaluate_match: takes (team -> (category -> amount))
    trials: int
    '''

    #print("predict match")
    #print("red: " + red_teams.__str__() + " blue: " + blue_teams.__str__())
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
        
        match = evaluate_match(outcome, o_red_teams, o_blue_teams)
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
    #print(probs)
    check_cat = None
    for category in probs:
        check_cat = category
    probs = probs[check_cat]
    
    for outcome in probs:
        #print(probs[outcome])
        if num < probs[outcome]:
            return outcome #return return return
        else:
            num -= probs[outcome]
