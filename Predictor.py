import random

def predict_match(red_teams, blue_teams, evaluate_match, trials):
    all_teams = []
    all_teams.extend(red_teams)
    all_teams.extend(blue_teams)
    
    matches = {}
    for i in range(0, trials):
        outcome = random_outcome(teams)
        match = evaluate_match(outcome)
        if not match in matches:
            matches[match] = 1
        else
            matches[match] = matches[match] + 1
    for match in matches:
        matches[match] = matches[match] / trials

    return matches, trials

def combine_predictions(m1, m2)
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
        
def random_outcome(teams): #teams is a map from teams to maps from maps from names to outcomes to probabilities 
    result = {}
    for team in teams:
        result[team] = random_team_outcome(team)
    return result
        
def random_team_outcome(team): #team is one team-map
    outcome = {}
    for category in team:
        probs = team[category]
        outcome[category] = random_category_outcome(probs)
    return outcome

def random_category_outcome(probs):
    num = random.random()
    for outcome in probs:
        if num < probs[outcome]:
            return outcome
        else
        num -= probs[outcome]
