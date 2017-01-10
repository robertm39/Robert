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
            try:    
                cache_file = open(self.full_file_name, "r")
                data = cache_file.read()
                if len(data) == 0:
                    data = "{}"
                self.cached_matches = ast.literal_eval(data)
                cache_file.close()
            except FileNotFoundError:
                self.cached_matches = {}
                
        def evaluate_stronghold_match(outcome, red_teams, blue_teams):
            red_total = 0
            #print(outcome)
            for team in red_teams:
                team_outcome = outcome[team]
                red_total += 2 * team_outcome[category_from_string("teleopBouldersLow")]
                red_total += 5 * team_outcome[category_from_string("teleopBouldersHigh")]

                red_total += 5 * team_outcome[category_from_string("autonBouldersLow")]
                red_total += 10 * team_outcome[category_from_string("autonBouldersHigh")]

            blue_total = 0
            for team in blue_teams:
                team_outcome = outcome[team]
                blue_total += 2 * team_outcome[category_from_string("teleopBouldersLow")]
                blue_total += 5 * team_outcome[category_from_string("teleopBouldersHigh")]
                
                blue_total += 5 * team_outcome[category_from_string("autonBouldersLow")]
                blue_total += 10 * team_outcome[category_from_string("autonBouldersHigh")]
            return red_total, blue_total

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

            return self.comp, tuple(red_teams), tuple(blue_teams)
                
        def do_prediction():
            o_red_teams = []
            o_blue_teams = []
            
            red_teams = {}
            blue_teams = {}
            tokens = self.team_numbers_field.get().split()
            reached_vs = False

            TRIALS = 100000 #100,000

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

            #print(red_teams.__str__() + " " + blue_teams.__str__())
            #print(red_teams)
            prediction = pd.predict_match(red_teams, blue_teams, evaluate_stronghold_match, TRIALS)
            #print(red_teams)
            key = self.comp, tuple(o_red_teams), tuple(o_blue_teams)
            #print(teams_tuple.__repr__())
            if not key in self.cached_matches:
                self.cached_matches[key] = prediction
            else:
                self.cached_matches[key] = pd.combine_predictions(prediction, self.cached_matches[key])
            self.last_key = key
            #print(self.cached_matches[key])
            show_graph()

        def show_graph():
            key = get_key()
            #if self.last_key != "":
            if not key == "":
                if self.has_graph:
                    self.ascii_graph.pack_forget()
                    #self.ascii_graph.forget_pack()
                #print(self.cached_matches[self.last_key])
                #self.ascii_graph = AsciiDataPanel(self, self.cached_matches[self.last_key][0])
                self.ascii_graph = GraphDataPanel(self, self.cached_matches[key][0])
                self.ascii_graph.pack(side=TOP, pady=3)
                self.has_graph = True
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

        #vars
        self.has_graph = False
        self.cached_matches = {}
        read_cached_matches()
        self.last_key = ""
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

        self.has_graph = False
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

def is_full_match(matches):
    result = False
    for match in matches:
        if match[1] != 0:
            result = True
    return result

##class AsciiDataPanel(Frame):
##
##    def __init__(self, parent, match_data):
##        def get_margin(match):
##            return match[0] - match[1]
##        
##        def data_sort(m_1):
##            return get_margin(m_1)
##
##        #self.pack(fill=BOTH, expand=True)
##
##        #super(DataPanel, self).__init__(parent, background="white")
##        Frame.__init__(self, parent, background="white")   
##        
##        self.data = match_data
##        match_keys = []
##        match_keys.extend(self.data.keys())
##        match_keys.sort(key=data_sort)
##
##        is_full_match = False
##        for match in match_keys:
##            if match[1] != 0:
##                is_full_match = True
##
##        if True: #is_full_match:
##            margins = []
##            probs_from_margins = {}
##            for match in match_keys:
##                margin = get_margin(match)
##                if not margin in probs_from_margins:
##                    probs_from_margins[margin] = self.data[match]
##                else:
##                    probs_from_margins[margin] += self.data[match]
##                if not margin in margins:
##                    margins.append(margin)
##            min_margin = min(margins)
##            max_margin = max(margins)
##
##            lines = []
##            lengths = []
##            for margin in range(min_margin, max_margin + 1):
##                g_text = margin.__str__()
##                prob = 0
##                if margin in margins:
##                    prob = probs_from_margins[margin]
##                total = 0
##                for i in range(0, round(prob * 50)):
##                    total += 1
##                    g_text += "]"
##                for i in range(total, 50):
##                    g_text += " "
##                g_text += " " + prob.__str__()
##                
##                lines.append(g_text)
##                lengths.append(len(g_text))
##                #label = Label(self, text=g_text)
##                #label.pack(side=TOP, padx=5, pady=3)
##            max_len = max(lengths)
##            for line in lines:
##                for i in range(0, max_len - len(line)):
##                    line += "  "
##                label = Label(self, text=line)
##                label.pack(side=TOP, padx=5, pady=3)
##                
class GraphDataPanel(Frame):

    def __init__(self, parent, match_data):
        self.pad = 2
        
        def get_margin(match):
            return match[0] - match[1]
        
        def data_sort(m_1):
            return get_margin(m_1)

        def get_x(margin):
            return PIX_PER_PROB * (NUM_PROBS // 2 + 1) + (margin + self.pad) * PIX_PER_PROB

        def get_y(prob):
            if prob == 0:
                return HEIGHT
            return min(300, round(HEIGHT - prob * HEIGHT))
        
        Frame.__init__(self, parent, background="white")

        HEIGHT = 300
        PIX_PER_PROB = 3
        NUM_PROBS = 401
        
        self.canvas = Canvas(self, width=(NUM_PROBS + self.pad*2)*PIX_PER_PROB + 1, height=HEIGHT, bd=1, bg="white")
        self.canvas.pack(side=TOP)

        match_keys = []
        match_keys.extend(match_data.keys())
        match_keys.sort(key=data_sort)

        margins = []
        probs_from_margins = {}

        light_gray = "#efefef"
        darker_gray = "#dfdfdf"
        even_darker_gray = "#9f9f9f"
        
        for margin in range(-(NUM_PROBS // 2), NUM_PROBS // 2 + 1, 5):
            #x = PIX_PER_PROB * (NUM_PROBS // 2 + 1) + margin * PIX_PER_PROB
            x = get_x(margin)
            top = 15

            if margin % 10 == 0:
                if margin == 0:
                    self.canvas.create_line(x, HEIGHT, x, top, fill = even_darker_gray)
                else:
                    self.canvas.create_line(x, HEIGHT, x, top, fill = darker_gray)
                self.canvas.create_text(x, 8, text=margin)
            else:
                self.canvas.create_line(x, HEIGHT, x, top, fill = light_gray)
        self.canvas.create_line(0, HEIGHT, get_x(205), HEIGHT)
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
        #print("")

        def get_graph_y(prob):
            if prob == 0:
                return HEIGHT
            return min(300, round(HEIGHT - prob * HEIGHT))
        
        for margin in margins:
            prev_prob = probs_from_margins.get(margin - 1, 0)
            prob = probs_from_margins[margin]
            next_prob = probs_from_margins.get(margin + 1, 0)
            #print(prob)

            #prev_y = round(HEIGHT - prev_prob * HEIGHT)
            #y = round(HEIGHT - prob * HEIGHT)
            #next_y = round(HEIGHT - next_prob * HEIGHT)
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

            if not y == 300:
                self.canvas.create_rectangle(x-1, HEIGHT, x+1, y, fill=r_fill) 
                self.canvas.create_line(x-1, y, x+1, y)

                if y < prev_y:
                    self.canvas.create_line(x-1, y, x-1, prev_y)
                if y < next_y:
                    self.canvas.create_line(x+1, y, x+1, next_y)

def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = ZScoutFrame(root)
    root.mainloop()  

if __name__ == '__main__':
    main()
