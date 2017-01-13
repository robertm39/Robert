from tkinter import *
import os
#import atexit
import ast

#from StrongholdMatchSegmenter import *
import MatchSegmenters
from Algorithm import *
from SegmentMatch import *
from Category import *
from MatchPhase import *
from ScoreReq import *
import Predictor as pd
import MatchEvaluators


class CannotGetCompetitionError(BaseException):
    pass

class ZScoutFrame(Frame):
           
    def __init__(self, parent):
        def save_cached_matches():
            cache_file = open(self.full_file_name, "w")
            cache_file.write(self.cached_matches.__repr__())
            cache_file.close()
            self.parent.destroy()
        
        Frame.__init__(self, parent, background="white")   
        self.parent = parent
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        #print(self.dir_path)
        self.full_file_name = self.dir_path + "\\cache.zsc"
        #atexit.register(save_cached_matches)
        self.parent.protocol("WM_DELETE_WINDOW", save_cached_matches)
        
        self.initUI()
    
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

        #game methods
        def get_segmenter():
            if self.year == "2016":
                segmenter = MatchSegmenters.stronghold_segment
                #print(segmenter)
                return segmenter
            elif self.year == "2017":
                return None #can't wait to see what this one will be
            return None

        def get_evaluate():
            if len(get_categories()) - len(get_banned_cats()) == 1:
                return MatchEvaluators.null_evaluate
            if self.year == "2016":
                return MatchEvaluators.evaluate_stronghold_match
            elif self.year == "2017":
                return MatchEvaluators.evaluate_steamworks_match #yaaaaay
            return None

        def get_predict_match():
            if self.year == "2016":
                return pd.generic_predict_match
            elif self.year == "2017":
                return pd.generic_predict_match

        def get_categories():
            if self.year == "2016":
                result = []
                result.append(MatchEvaluators.category_from_string("teleopBouldersLow"))
                result.append(MatchEvaluators.category_from_string("teleopBouldersHigh"))
                result.append(MatchEvaluators.category_from_string("autonBouldersLow"))
                result.append(MatchEvaluators.category_from_string("autonBouldersHigh"))
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
        #end game methods
        
        #scouting methods
        def set_comp():
            self.comp = self.comp_choose.get()
            self.year = self.comp[:4]
            #print(self.year)
            
            segmenter = get_segmenter()
            #competition = get_segmented_competition(self.comp, segmenter)
            full_competition = get_competition(self.comp)
            if full_competition == None:
                self.error.set(self.comp + " is not cached and there is no connection.")
                return

            self.error.set("")
            full_comp = full_competition[0]
            #print(segmenter)
            segmented = segment_competition(full_comp, segmenter)
            #segmented = competition[0]
            #full_comp = competition[1]
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

            update_categories()

            self.contrs_from_team_from_category = {}
            for team in contrs_from_category[check_cat]:
                team_contrs = {}
                for category in segmented:
                    team_contrs[category] = contrs_from_category[category][team]
                self.contrs_from_team_from_category[team] = team_contrs            
        #end scouting methods

        #predicting methods
        def read_cached_matches():
            try:    
                cache_file = open(self.full_file_name, "r")
                data = cache_file.read()
                if len(data) == 0:
                    data = "{}"
                self.cached_matches = ast.literal_eval(data)
                cache_file.close()
            except FileNotFoundError:
                self.cached_matches = {}

        def filter_for_categories():
            pass #finish
        
        def get_outcome(team_outcome, string, banned):
            if get_pretty_string(string) in banned:
                return 0
            return team_outcome[category_from_string(string)]

        def get_banned_cats():
            return self.category_frame.get_banned_categories()
    
        def get_key():
            tokens = self.team_numbers_field.get().split()
            reached_vs = False
            red_teams = []
            blue_teams = []
            
            for token in tokens:
                if token == 'vs' or token == 'vs.':
                    reached_vs = True
                else:
                    team = 'frc' + token
                    if not reached_vs:
                        red_teams.append(team)
                    else:
                        blue_teams.append(team)

            return self.comp, tuple(red_teams), tuple(blue_teams), tuple(get_banned_cats())
                
        def do_prediction():
            o_red_teams = []
            o_blue_teams = []
            
            red_teams = {}
            blue_teams = {}
            tokens = self.team_numbers_field.get().split()
            reached_vs = False

            TRIALS = 100000 #100,000


            banned_cats = get_banned_cats()
            scenario = []
            for cat in banned_cats:
                scenario.append(cat)
            scenario = tuple(scenario)
            for token in tokens:
                if token == 'vs' or token == 'vs.':
                    reached_vs = True
                else:
                    team = 'frc' + token
                    if not reached_vs:
                        o_red_teams.append(team)
                        red_teams[team] = self.contrs_from_team_from_category[team]
                    else:
                        o_blue_teams.append(team)
                        blue_teams[team] = self.contrs_from_team_from_category[team]

            predict_match = get_predict_match()
            prediction = predict_match(red_teams, blue_teams, get_evaluate(), TRIALS, scenario, self.year)
            
            key = self.comp, tuple(o_red_teams), tuple(o_blue_teams), scenario
            
            if not key in self.cached_matches:
                self.cached_matches[key] = prediction
            else:
                self.cached_matches[key] = pd.combine_predictions(prediction, self.cached_matches[key])
            self.last_key = key
            
            show_graph()

        def show_graph():
            key = get_key()
            if not key == "":
                if self.has_graph:
                    self.ascii_graph.pack_forget()

                self.ascii_graph = GraphDataPanel(self.graph_container, self.cached_matches[key][0])
                self.ascii_graph.pack(side=TOP, pady=3)
                self.has_graph = True

        def update_categories():
            if self.has_categories:
                self.category_frame.pack_forget()
            self.category_frame  = CategoryChooserPanel(self.categories_container, self.categories)
            self.category_frame.pack(side=TOP)
            self.has_categories = True
            
        #end predicting methods
        
        self.parent.title("ZScout")
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

        #vars
        self.has_graph = False
        self.cached_matches = {}
        read_cached_matches()
        self.last_key = ""
        self.year = ""
        #end vars
        
        self.graph_frame = Frame(self, relief=RAISED, borderwidth=1)
        self.graph_frame.pack(side=TOP, fill=BOTH, expand=True)
        self.active_frame = self.graph_frame
        
        self.team_numbers_label = Label(self.graph_frame, text="Team Number(s):")
        self.team_numbers_label.pack(side=TOP, padx=5, pady=5)
        
        self.team_numbers_field = Entry(self.graph_frame, width=29)
        self.team_numbers_field.pack(side=TOP, padx=5, pady=5)
        
        self.do_prediction_button = Button(self.graph_frame, text="Do Prediction", command=do_prediction)
        self.do_prediction_button.pack(side=TOP, padx=5, pady=5)
        
        self.show_button = Button(self.graph_frame, text="Show Graph", command=show_graph)
        self.show_button.pack(side=TOP, padx=5, pady=5)

        self.graph_type = StringVar()
        self.margins_button = RadioButton(self.graph_frame, text="Margin Graph", var=self.graph_type, value="margin")
        
        
        self.categories_container = Frame(self.graph_frame)
        self.categories_container.pack(side=TOP, pady=3)
        self.has_categories = False
        self.category_frame = None
        
        self.graph_container = Frame(self.graph_frame)
        self.graph_container.pack(side=TOP, pady=3)
        
        self.has_graph = False
        #end make graph frame
        
        #make scouting frame
        
        #vars
        self.error = StringVar()
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

        self.error_label = Label(self.scouting_frame, textvariable=self.error)
        self.error_label.pack(side=TOP, pady=5)
        #end make scouting frame

def is_full_match(matches):
    result = False
    for match in matches:
        if match[1] != 0:
            result = True
    return result

class CategoryChooserPanel(Frame):
    def __init__(self, parent, categories):
        Frame.__init__(self, parent, background="white")
        self.pack(fill=BOTH, expand=True)
        
        self.all_var = IntVar()
        all_check = Checkbutton(self, text="All", variable=self.all_var)
        all_check.pack(side=TOP, pady=3)
        
        self.vars_from_names = {}
        
        for category in categories:
            var = IntVar()
            check = Checkbutton(self, text=category.name, variable=var)
            check.pack(side=TOP, pady=3)
            self.vars_from_names[category.name] = var

    def get_banned_categories(self):
        if self.all_var.get():
            return []
        result = []
        for name in self.vars_from_names:
            if not self.vars_from_names[name].get():
                result.append(name)
        #print(result)
        return result
        
class GraphDataPanel(Frame):

    def __init__(self, parent, match_data, g_height=300, pix_per_prob=3, text_pad=30, num_probs=401):
        self.pad = 2
        
        tot_height = g_height + text_pad
        
        def get_margin(match):
            return match[0] - match[1]
        
        def data_sort(m_1):
            return get_margin(m_1)

        def get_x(margin):
            return pix_per_prob * (num_probs // 2 + 1) + (margin + self.pad) * pix_per_prob

        def get_y(prob):
            if prob == 0:
                return tot_height
            return  min(g_height, round(g_height - prob * g_height)) + text_pad
        
        Frame.__init__(self, parent, background="white")
        
        #HEIGHT = 300
        #PIX_PER_PROB = 3
        #NUM_PROBS = 401
        
        self.canvas = Canvas(self, width=(num_probs + self.pad*2)*pix_per_prob + 1, height=tot_height, bd=1, bg="white")
        self.canvas.pack(side=TOP)
        
        match_keys = []
        match_keys.extend(match_data.keys())
        match_keys.sort(key=data_sort)
        
        margins = []
        probs_from_margins = {}

        h_w = pix_per_prob // 2
        
        light_gray = "#efefef"
        darker_gray = "#dfdfdf"
        even_darker_gray = "#9f9f9f"
        
        for margin in range(-(num_probs // 2), num_probs // 2 + 1, 5):
            #x = PIX_PER_PROB * (num_probs // 2 + 1) + margin * PIX_PER_PROB
            x = get_x(margin)
            top = 15

            if margin % 10 == 0:
                if margin == 0:
                    self.canvas.create_line(x, tot_height, x, top, fill = even_darker_gray)
                else:
                    self.canvas.create_line(x, tot_height, x, top, fill = darker_gray)
                self.canvas.create_text(x, 8, text=margin)
            else:
                self.canvas.create_line(x, tot_height, x, top, fill = light_gray)
        self.canvas.create_line(0, tot_height, get_x(205), tot_height)
        self.canvas.create_line(0, get_y(0.75), get_x(205), get_y(0.75), fill = light_gray)
        self.canvas.create_line(0, get_y(0.5), get_x(205), get_y(0.5), fill = light_gray)
        self.canvas.create_line(0, get_y(0.25), get_x(205), get_y(0.25), fill = light_gray)
        #self.canvas.create_text(PIX_PER_PROB * (NUM_PROBS // 2 + 1), 8, text="0")
        
        for match in match_keys:
            margin = get_margin(match)
            if not margin in probs_from_margins:
                probs_from_margins[margin] = match_data[match]
            else:
                probs_from_margins[margin] += match_data[match]
            if not margin in margins:
                margins.append(margin)
        #print(h_w)
        for margin in margins:
            prev_prob = probs_from_margins.get(margin - 1, 0)
            prob = probs_from_margins[margin]
            next_prob = probs_from_margins.get(margin + 1, 0)
            
            prev_y = get_y(prev_prob)
            y = get_y(prob)
            next_y = get_y(next_prob)

            #print("prob: " + prob.__str__() + " y: " + y.__str__())
            
            x = get_x(margin)
            #x = PIX_PER_PROB * (NUM_PROBS // 2 + 1) + margin * PIX_PER_PROB

            r_fill=""
            if margin > 0:
                r_fill = "red"
            elif margin < 0:
                r_fill = "blue"
            else:
                r_fill = "magenta"

            if not y == tot_height:
                self.canvas.create_rectangle(x-h_w, tot_height, x+h_w, y, fill=r_fill) 
                #self.canvas.create_line(x-h_w, y, x+h_w, y)
                
                #if y < prev_y:
                #    self.canvas.create_line(x-h_w, y, x-h_w, prev_y)
                #if y < next_y:
                #    self.canvas.create_line(x+h_w, y, x+h_w, next_y)

def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = ZScoutFrame(root)
    root.mainloop()  

if __name__ == '__main__':
    main()
