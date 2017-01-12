import math

def get_categories():
    if self.year == "2016":
        result = []
        result.append(category_from_string("teleopBouldersLow"))
        result.append(category_from_string("teleopBouldersHigh"))
        result.append(category_from_string("autonBouldersLow"))
        result.append(category_from_string("autonBouldersHigh"))
        return result
    elif self.year == "2017":
        return None #can't wait to see what this one will be
    return None

def get_pretty_string(string):
    if string == "teleopBouldersLow":
        return "teleop low goal"
    elif string == "teleopBouldersHigh":
        return "teleop high goal"
    elif string == "autonBouldersLow":
        return "auton low goal"
    elif string == "autonBouldersHigh":
        return "auton high goal"

def get_outcome(team_outcome, string, banned):
    if get_pretty_string(string) in banned:
        return 0
    return team_outcome[category_from_string(string)]

def evaluate_stronghold_match(outcome, red_teams, blue_teams, scenario=()):
    def one_side(teams):
        total = 0
        for team in teams:
            team_outcome = outcome[team]

            total += 2 * get_outcome(team_outcome, "teleopBouldersLow", scenario)
            total += 5 * get_outcome(team_outcome, "teleopBouldersHigh", scenario)

            total += 5 * get_outcome(team_outcome, "autonBouldersLow", scenario)
            total += 10 * get_outcome(team_outcome, "autonBouldersHigh", scenario)
        return total
    
    red_total = one_side(red_teams)
    blue_total = one_side(blue_teams)
    
    return red_total, blue_total

def evaluate_steamworks_match(outcome, red_teams, blue_teams, scenario=()):
    AUTON_GEARS = ""
    AUTON_LOW = ""
    AUTON_HIGH = ""
    AUTON_BASELINE = ""

    TELEOP_GEARS = ""
    TELEOP_LOW = ""
    TELEOP_HIGH = ""
    TELEOP_HANG = ""

    FOUL = ""
    TECH_FOUL = ""

    GEAR_TOTALS = [1, 3, 7, 13]

    def get_gear_score(aut_gears, tel_gears):
        gears = aut_gears + tel_gears
        score = 0
        for total in GEAR_TOTALS:
            if gears >= total:
                score += 40
            if aut_gears >= total:
                score += 20
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
            kpa += math.floor(get_outcome(t_outcome, AUTON_LOW, scenario) / 3)
            kpa += get_outcome(t_outcome, AUTON_HIGH, scenario)

            total += get_outcome(t_outcome, AUTON_BASELINE, scenario) * 5
            aut_gears += get_outcome(t_outcome, AUTON_GEARS, scenario)
            #end auton

            #teleop
            kpa += math.floor(get_outcome(t_outcome, TELEOP_LOW, scenario) / 9)
            kpa += math.floor(get_outcome(t_outcome, TELEOP_HIGH, scenario) / 3)
            tel_gears += get_outcome(t_outcome, TELEOP_GEARS, scenario)
            num_hang += get_outcome(t_outcome, TELEOP_HANG, scenario)
            #end teleop

            #fouls
            foul += get_outcome(t_outcome, FOUL, scenario) * 5
            foul += get_outcome(t_outcome, TECH_FOUL, scenario) * 25

        total += kpa
        total += get_gear_score(aut_gears, tel_gears)
        total += 50 * num_hang
        if "elims" in scenario:
            if num_hang >= 3:
                total += 100
            if kpa >= 40
                total += 20

        return total, foul

    red = one_side(red_teams)
    blue = one_side(blue_teams)

    return red[0] + blue[1], blue[0] + red[1]
