import random

def combine_predictions(m1, m2):
    trials = m1[1] + m2[1]
    result = {}
    
    m1_ratio = m1[1] / trials
    for match in m1[0]:
        if not match in result:
            result[match] = m1[0][match] / m1_ratio
        else:
            result[match] += m1[0][match] / m1_ratio

    m2_ratio = m2[1] / trials
    for match in m2[0]:
        if not match in result:
            result[match] = m2[0][match] / m2_ratio
        else:
            result[match] += m2[0][match] / m2_ratio

    return result, trials

def get_team_from_team_map(team):
    for t in team:
        return t

def predict_match(red_teams, blue_teams, evaluate_match, trials): #teams: (team -> (category -> (amount -> prob)* )* )
    all_teams = []
    all_teams.extend(red_teams)
    all_teams.extend(blue_teams)

    #print(red_teams)
    
    matches = {}
    teams = []
    teams.extend(red_teams)
    teams.extend(blue_teams)
    for i in range(0, trials):
        outcome = random_outcome(teams)
        
        o_red_teams = []
        for t in red_teams:
            o_red_teams.append(get_team_from_team_map(t))

        o_blue_teams = []
        for t in blue_teams:
            o_blue_teams.append(get_team_from_team_map(t))
            
        match = evaluate_match(outcome, o_red_teams, o_blue_teams)
        if not match in matches:
            matches[match] = 1
        else:
            matches[match] = matches[match] + 1
    for match in matches:
        matches[match] = matches[match] / trials

    return matches, trials

def random_outcome(teams): #teams is a map from teams to maps from maps from names to outcomes to probabilities 
    result = {}
    for team in teams:
        actual_team = get_team_from_team_map(team)
        result[actual_team] = random_team_outcome(team)
    return result
        
def random_team_outcome(team): #team is one team-map
    outcome = {}
    for category in team:
        probs = team[category]
        outcome[category] = random_category_outcome(probs)
    return outcome

def random_category_outcome(probs):
    num = random.random()
    #print(probs)
    check_cat = None
    for category in probs:
        check_cat = category
    probs = probs[check_cat]
    
    for outcome in probs:
        #print(probs[outcome])
        if num < probs[outcome]:
            return outcome
        else:
            num -= probs[outcome]
