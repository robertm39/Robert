from tkinter import *
import os
import atexit
import ast

from StrongholdMatchSegmenter import *
from Algorithm import *
from SegmentMatch import *
from Category import *
from MatchPhase import *
from ScoreReq import *
import Predictor as pd

class ZScoutFrame(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
        self.parent = parent
        self.initUI()
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        print(self.dir_path)
        self.full_file_name = self.dir_path _ "\\cache.zsc"
        atexit.register(save_cached_matches)

    def save_cached_matches():
            cache_file = open(self.full_file_name, access_mode="w")
            cache_file.write(cached_matches.__repr__())
            cache_file.close()
        
    def initUI(self):
        #frame methods
        def go_to_graph_frame():
            go_to_frame(self.graph_frame)
        
        def go_to_scouting_frame():
            go_to_frame(self.scouting_frame)
        
        def go_to_frame(frame):
            if self.active_frame == frame:
                return
            self.active_frame.pack_forget()
            frame.pack(side=TOP, fill=BOTH, expand=True)
            self.active_frame = frame
        #end frame methods

        def category_from_string(string):
            if string == "teleopBouldersLow":
                return Category(True, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop low goal')
            elif string == "teleopBouldersHigh":
                return Category(True, ScoreReq.INDIVIDUAL, MatchPhase.TELEOP, 'teleop high goal')
            elif string == "autonBouldersLow":
                return Category(True, ScoreReq.INDIVIDUAL, MatchPhase.AUTON, 'auton low goal')
            elif string == "autonBouldersHigh":
                return Category(True, ScoreReq.INDIVIDUAL, MatchPhase.AUTON, 'auton high goal')
            raise RuntimeError("string: " + string)
            
        #scouting methods
        def set_comp():
            self.comp = self.comp_choose.get()
            
            segmenter = StrongholdMatchSegmenter()
            segmented = get_segmented_competition(self.comp, segmenter)
            #print(segmented)
            #print("")

            self.categories = []
            contrs_from_category = {}
            check_cat = None
            for category in segmented:
                #print(category)
                self.categories.append(category)
                check_cat = category
                
                segment = segmented[category]
                #print(segment)
                scouting = {}
                fill_scouting(category, scouting, segment)
                #print(scouting)
                contrs_from_category[category] = get_team_prob_distrs(segment, scouting)

            self.contrs_from_team_from_category = {}
            for team in contrs_from_category[check_cat]:
                team_contrs = {}
                for category in segmented:
                    team_contrs[category] = contrs_from_category[category][team]
                self.contrs_from_team_from_category[team] = team_contrs            
        #end scouting methods

        #predicting methods
        def read_cached_matches():
            
                
        def evaluate_stronghold_match(outcome, red_teams, blue_teams):
            red_total = 0
            for team in red_teams:
                team_outcome = outcome[team]
                red_total += 2 * team_outcome[category_from_string("teleopBouldersLow")]
                red_total += 5 * team_outcome[category_from_string("teleopBouldersHigh")]

            blue_total = 0
            for team in blue_teams:
                team_outcome = outcome[team]
                blue_total += 2 * team_outcome[category_from_string("teleopBouldersLow")]
                blue_total += 5 * team_outcome[category_from_string("teleopBouldersHigh")]
            return red_total, blue_total
                
        def do_prediction():
            red_teams = []
            blue_teams = []
            tokens = self.team_numbers_field.get().split()
            reached_vs = False

            TRIALS = 10000 #10,000

            for token in tokens:
                if token == 'vs' or token == 'vs.':
                    reached_vs = True
                else:
                    team = 'frc' + token
                    if not reached_vs:
                        red_teams.append(self.contrs_from_team_from_category[team])
                    else:
                        blue_teams.append(self.contrs_from_team_from_category[team])

            prediction = pd.predict_match(red_teams, blue_teams, evaluate_stronghold_match, TRIALS)
            if not (red_teams, blue_teams) in cached_matches:
                cached_matches[red_teams, blue_teams] = prediction
            else:
                cached_matches[red_teams, blue_teams] = pd.combine_predictions(prediction, cached_matches[red_teams, blue_teams])
            print(prediction)
        #end predicting methods
        
        self.parent.title("ZScout")
        #self.style = tk.Style()
        #self.style.theme_use("default")

##        frame = Frame(self, relief=RAISED, borderwidth=1)
##        frame.pack(fill=BOTH, expand=True)

        
        
        self.pack(fill=BOTH, expand=True)

        #make menu
        self.menubar = Menu(self)
        self.frame_select = Menu(self.menubar, tearoff=0)
        self.frame_select.add_command(label="Graphs", command=go_to_graph_frame)
        self.frame_select.add_command(label="Scouting", command=go_to_scouting_frame)
        self.menubar.add_cascade(label="Sections", menu=self.frame_select)
        self.parent.config(menu=self.menubar)
        #end make menu

        #make graph frame
        self.cached_matches = {}
        
        self.graph_frame = Frame(self, relief=RAISED, borderwidth=1)
        self.graph_frame.pack(side=TOP, fill=BOTH, expand=True)
        self.active_frame = self.graph_frame
        
        self.team_numbers_label = Label(self.graph_frame, text="Team Number(s):")
        self.team_numbers_label.pack(side=TOP, padx=5, pady=5)
        
        self.team_numbers_field = Entry(self.graph_frame)
        self.team_numbers_field.pack(side=TOP, padx=5, pady=5)

        self.do_prediction_button = Button(self.graph_frame, text="Do Prediction", command=do_prediction)
        self.do_prediction_button.pack(side=TOP, padx=5, pady=5)
        #end make graph frame

        #make scouting frame
        
        #vars
        self.contrs_from_team_from_category = {}
        self.categories = []
        #end vars
        
        self.scouting_frame = Frame(self, relief=RAISED, borderwidth=1)
        self.comp_label = Label(self.scouting_frame, text="Competition:")
        self.comp_label.pack(side=TOP, padx=5, pady=5)

        self.comp_choose = Entry(self.scouting_frame)
        self.comp_choose.pack(side=TOP, padx=5, pady=5)

        self.comp_button = Button(self.scouting_frame, text="Accept", command=set_comp)
        self.comp_button.pack(side=TOP, padx=5, pady=5)
        
        #end make scouting frame
        
##        close_button = Button(self, text="Close")
##        close_button.pack(side=RIGHT, padx=5, pady=5)
##
##        ok_button = Button(self, text="Ok")
##        ok_button.pack(side=RIGHT)

def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = ZScoutFrame(root)
    root.mainloop()  

if __name__ == '__main__':
    main()
