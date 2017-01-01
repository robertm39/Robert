from StrongholdMatchSegmenter import *
from Algorithm import *

from SegmentMatch import *
from Category import *
from MatchPhase import *
from ScoreReq import *

def segmenter_test():
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = get_segmented_competition(event, segmenter)
    teleop_low_goal_category = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    result = segmented[teleop_low_goal_category]
    print(len(result))
    print(result)

def eq_test():
    teleop_low_goal_category_one = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    teleop_low_goal_category_two = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    print(teleop_low_goal_category_one ==  teleop_low_goal_category_two)

    number = 1
    category = teleop_low_goal_category_one
    amount = 2
    teams = ['frc830', 'frc3880', 'frc123']

    seg_one = SegmentMatch(number, category, amount, teams)
    seg_two = SegmentMatch(number, category, amount, teams)
    print(seg_one == seg_two)

def stacking_indiv_target_finder_test(competition):
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = get_segmented_competition(event, segmenter)
    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    low_goal = segmented[teleop_low_goal]

def get_stack_indiv_averages_test():
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = get_segmented_competition(event, segmenter)
    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    low_goal = segmented[teleop_low_goal]
    scouting = {}
    fill_in_stacking_indiv_scouting(low_goal, scouting)
    contrs = get_stack_indiv_averages(low_goal, scouting)
    return contrs
    
def fill_in_scouting_stacking_indiv_test(competition):
    segmenter = StrongholdMatchSegmenter()
    event = "2016mihow"
    segmented = get_segmented_competition(event, segmenter)
    teleop_low_goal = Category(1, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
    low_goal = segmented[teleop_low_goal]
    scouting = {}
    fill_in_stacking_indiv_scouting(low_goal, scouting)
    print(scouting)
