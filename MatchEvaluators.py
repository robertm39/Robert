import math

#from Category import Category
#import Category as Ct
#from ScoreReq import ScoreReq
#from MatchPhase import MatchPhase
from utils import Category
import categories as ct

def get_outcome(team_outcome, string, allowed):
    #if pretty_from_ugly[string] in banned:
    #print(string)
    #if not Ct.PRETTY_FROM_TBA[string] in allowed:
    if type(string) == str:
        if not Category.PRETTY_FROM_TBA[string] in allowed:
            return 0
        return team_outcome[Category.CATEGORIES_FROM_TBA_NAMES[string]]
    else:
        if not string.pretty_name in allowed:
            return 0
        return team_outcome[string]
    #print("team_outcome: " + team_outcome.__str__())
    #return team_outcome[Ct.CATEGORIES_FROM_TBA_NAMES[string]]

def null_evaluate(outcome, red_teams, blue_teams, scenario=()):
    def one_side(teams):
        total = 0
        for team in teams:
            for cat in outcome[team]:
                #print("cat: " + cat.__str__())
                total += get_outcome(outcome[team], cat.tba_name, scenario)
        return total

    return one_side(red_teams), one_side(blue_teams)

def evaluate_stronghold_match(outcome, red_teams, blue_teams, scenario=()):
    def one_side(teams):
        total = 0
        for team in teams:
            team_outcome = outcome[team]

            total += 2 * get_outcome(team_outcome, ct.STRONGHOLD_TELEOP_LOW_BOULDERS.tba_name, scenario)
            total += 5 * get_outcome(team_outcome, ct.STRONGHOLD_TELEOP_HIGH_BOULDERS.tba_name, scenario)

            total += 5 * get_outcome(team_outcome, ct.STRONGHOLD_AUTON_LOW_BOULDERS.tba_name, scenario)
            total += 10 * get_outcome(team_outcome, ct.STRONGHOLD_AUTON_HIGH_BOULDERS.tba_name, scenario)
        return total
    
    red_total = one_side(red_teams)
    blue_total = one_side(blue_teams)
    
    return red_total, blue_total

GEAR_TOTALS = [1, 3, 7, 13] #1, 2, 4, 6

def evaluate_steamworks_match(outcome, red_teams, blue_teams, scenario=()):
    global GEAR_TOTALS
    
    def get_gear_score(aut_gears, tel_gears):
        gears = aut_gears + tel_gears + 1 #reserve gear
        score = 0
        for total in GEAR_TOTALS:
            if gears >= total:
                score += 40
            if aut_gears >= total:
                score += 20
        #print('score: ' + score.__str__())
        return score
    
    def one_side(teams):
        total = 0
        kpa = 0
        aut_gears = 0
        tel_gears = 0
        num_hang = 0
        foul = 0
        for team in teams:
            t_outcome = outcome[team]

            #auton
            kpa += math.floor(get_outcome(t_outcome, ct.STEAMWORKS_AUTON_LOW_FUEL.tba_name, scenario) / 3)
            kpa += get_outcome(t_outcome, ct.STEAMWORKS_AUTON_HIGH_FUEL.tba_name, scenario)

            total += get_outcome(t_outcome, ct.STEAMWORKS_AUTON_BASELINE.tba_name, scenario) * 5
            aut_gears += get_outcome(t_outcome, ct.STEAMWORKS_AUTON_GEARS.tba_name, scenario)
            #end auton

            #teleop
            kpa += math.floor(get_outcome(t_outcome, ct.STEAMWORKS_TELEOP_LOW_FUEL.tba_name, scenario) / 9)
            kpa += math.floor(get_outcome(t_outcome, ct.STEAMWORKS_TELEOP_HIGH_FUEL.tba_name, scenario) / 3)
            tel_gears += get_outcome(t_outcome, ct.STEAMWORKS_TELEOP_GEARS.tba_name, scenario)
            num_hang += get_outcome(t_outcome, ct.STEAMWORKS_TELEOP_HANGING.tba_name, scenario)
            #end teleop

            #fouls
            foul += get_outcome(t_outcome, ct.FOULS, scenario) * 5
            foul += get_outcome(t_outcome, ct.TECH_FOULS, scenario) * 25

        total += kpa
        total += get_gear_score(aut_gears, tel_gears)
        total += 50 * num_hang
        if "elims" in scenario:
            if aut_gears + tel_gears + 1 >= 13:
                total += 100
            if kpa >= 40:
                total += 20

        return total, foul

    red = one_side(red_teams)
    blue = one_side(blue_teams)

    return red[0] + blue[1], blue[0] + red[1]
