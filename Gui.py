"""The module that contains the main application."""

import tkinter as tk
import math
import os
#import ast

#import Algorithm as al
import comp as cp
#from utils import Category
#import categories as ctgs
import Predictor as pd
import MatchEvaluators as me
import scoutingdatagetters as sdg
import games as gms

class CannotGetCompetitionError(BaseException):
    pass

class ZScoutFrame(tk.Frame):
    """The frame the ZScout Gui is in."""
           
    def __init__(self, parent):
        """Make a ZScoutFrame."""
        def save_cached_matches():
            """Save the matches in the match cache to the cache file."""
            cache_file = open(self.full_file_name, "w")
            cache_file.write(self.cached_matches.__repr__())
            cache_file.close()
            self.parent.destroy()
        
        tk.Frame.__init__(self, parent, background="white")   
        self.parent = parent
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        
        self.full_file_name = self.dir_path + "\\cache.zsc"
        
        self.parent.protocol("WM_DELETE_WINDOW", save_cached_matches)
        
        self.initUI()
    
    def initUI(self):
        """Initialize the user interface."""
        #frame methods
        def go_to_graph_frame():
            go_to_frame(self.graph_frame)
        
        def go_to_summary_frame():
            go_to_frame(self.team_summary_frame)
        
        def go_to_scouting_frame():
            go_to_frame(self.scouting_frame)
        
        def go_to_teams_frame():
            go_to_frame(self.teams_frame)
        
        def go_to_frame(frame):
            if self.active_frame == frame:
                return
            self.active_frame.pack_forget()
            frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.active_frame = frame
        #end frame methods

        #game methods
        def get_evaluate(can_null_eval=True):
            """Return the function to use to evaluate matches from the current prediction."""
            if len(get_cats()) == 1 and can_null_eval:
                return me.null_evaluate
            return self.game.evaluate
        #end game methods
        
        #scouting methods
        def set_comp():
            """Set the current competition to the one specified in the comp_choose field, set relevant variables, and get team contribution data."""
            self.comp = self.comp_choose.get()
            self.year = self.comp[:4]
            self.game = gms.GAMES_FROM_YEARS[self.year]
            
            segmenter = self.game.segment
            full_competition = cp.get_competition(self.comp)
            if full_competition == None:
                self.error.set(self.comp + " is not cached and there is no internet connection.")
                return

            scouting = sdg.get_scouting_data(self.game.get_data_from_match, self.comp)

            self.raw_scouting = sdg.get_raw_scouting_data(self.comp)

            self.error.set("")
            full_comp = full_competition[0]
            segmented = cp.segment_competition(full_comp, segmenter)

            self.categories = []
            contrs_from_category = {}
            check_cat = None
            for category in segmented:
                self.categories.append(category.pretty_name)
                check_cat = category
                
                segment = segmented[category]
                if not category in scouting:
                    scouting[category] = {}
                segment_scouting = scouting[category]
                self.game.fill_scout_from_categories[category](category, segment_scouting, segment)
                contrs_from_category[category] = self.game.algorithms_from_categories[category](segment, segment_scouting)#al.add_category_to_distrs(self.game.algorithms_from_categories[category](segment, segment_scouting), category)
            
            for scenario in self.game.scenarios:
                self.categories.append(scenario)
            
#            self.categories.sort()

            update_categories()

            self.contrs_from_team_from_category = {}
            for team in contrs_from_category[check_cat]:
                team_contrs = {}
                for category in segmented:
                    team_contrs[category] = contrs_from_category[category][team]
                self.contrs_from_team_from_category[team] = team_contrs
            
#            self.teams_inner_frame.pack_forget()
            self.teams_inner_frame = tk.Frame(self.teams_mid_frame, relief=tk.RAISED, borderwidth=1)
            self.teams_inner_frame.pack(side=tk.TOP)
            
            teams = list(self.contrs_from_team_from_category.keys())
            teams.sort(key=lambda t: int(t[3:]))
            tk.Label(self.teams_inner_frame, text='Teams:').pack(side=tk.TOP)
            for team in teams:
                tk.Label(self.teams_inner_frame, text=team[3:]).pack(side=tk.TOP)
            config_canvas(self.teams_canvas, width=150, height=662)
        #end scouting methods
        
        #predicting methods
        def read_cached_matches(): #cacheing disabled
            """Read the cached predicted match scores from the cache file"""
            self.cached_matches = {}
#            try:    
#                cache_file = open(self.full_file_name, "r")
#                data = cache_file.read()
#                if len(data) == 0:
#                    data = "{}"
#                self.cached_matches = ast.literal_eval(data)
#                cache_file.close()
#            except FileNotFoundError:
#                self.cached_matches = {}
        
        def get_cats():
            """Return the categories and scenarios to be used in the next match prediction."""
            return self.category_frame.get_categories()
    
        def get_key():
            """Return the key to be used in the cached predicted match score dict."""
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

            return self.comp, tuple(red_teams), tuple(blue_teams), tuple(get_cats())
                
        def do_prediction():
            """Do a match prediction with the current teams, categories and scenarios. If there is already a prediction, combine it with the new one."""
            o_red_teams = []
            o_blue_teams = []
            
            red_teams = {}
            blue_teams = {}
            tokens = self.team_numbers_field.get().split()
            reached_vs = False

            TRIALS = 10000 #100,000 2,000

            cats = get_cats()
            scenario = []
            for cat in cats:
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

            predict_match = self.game.predict
            can_null_eval = len(red_teams) + len(blue_teams) == 1
            prediction = predict_match(red_teams, blue_teams, get_evaluate(can_null_eval), TRIALS, scenario, self.year)
            
            key = self.comp, tuple(o_red_teams), tuple(o_blue_teams), scenario
            
            if not key in self.cached_matches:
                self.cached_matches[key] = prediction
            else:
                self.cached_matches[key] = pd.combine_predictions(prediction, self.cached_matches[key])
            self.last_key = key
            
            show_graph()

        def show_graph():
            """Show the predicted match score data for the teams, categories and scenarios selected."""
            key = get_key()
            if not key == "":
                if self.has_graph:
                    self.ascii_graph.pack_forget()
                root = tk.Tk()
                new_window = tk.Toplevel(root)
                root.withdraw()
                self.ascii_graph = GraphDataPanel(new_window, self.cached_matches[key][0])
                self.ascii_graph.pack(side=tk.TOP, pady=3)
                self.has_graph = True
                self.probs.set("Red: " + round(100*self.ascii_graph.red_prob, 1).__str__() + "% Blue: " + round(100*self.ascii_graph.blue_prob, 1).__str__() + "% Tie: " + round(100*self.ascii_graph.tie_prob, 1).__str__() + "%")
        
        def update_categories():
            """Update the category frame."""
            if self.has_categories:
                self.category_frame.pack_forget()
            self.category_frame  = CategoryChooserPanel(self.categories_container, self.categories)
            self.category_frame.pack(side=tk.TOP)
            self.has_categories = True
            
        #end predicting methods
        
        #team summary methods
        def get_match_scouting_string(match, line_data):
            """Return a string describing the match and line data in human-readable format."""
#            result = '  ' + '#' + match.__str__() + '  '
            result = ''
            line_data_types = ['match_id']
            line_data['match_id'] = match
            for data_type in self.game.scouting_data_types:
                line_data_types.append(data_type)
                
            for line_data_type in line_data_types:
                data = line_data[line_data_type]
                length = len(line_data_type)
#                result += ' '*(4-prev_data_length) + line_data_type.__str__() + ': ' + data.__str__()
                inner_length = length - len(data.__str__())
                result += ' '*math.floor(inner_length /2) + data.__str__() + ' '*math.ceil(inner_length / 2) + ' '*2
#                prev_data_length = len(data.__str__())
                
            return result.rstrip()
        
        def get_column_string():
            result = 'match_id  '
            for data_type in self.game.scouting_data_types:
                result += data_type.__str__() + '  '
                
            return result.rstrip()
        
        def show_summary():
            team = 'frc' + self.team_summary_team_field.get()
            self.team_summary_inner_frame.pack_forget()
            self.team_summary_inner_frame = tk.Frame(self.team_summary_canvas_frame, relief=tk.RAISED, borderwidth=1)
            self.team_summary_inner_frame.pack(side=tk.TOP)
            
            teams = {team: self.contrs_from_team_from_category[team]}
#            print(teams)
            blue_teams = {}
            first = True
            
            
            scouting_text_scrollbar = tk.Scrollbar(self.team_summary_inner_frame, orient='horizontal')
            scouting_text_pane = tk.Text(self.team_summary_inner_frame, wrap=tk.NONE, xscrollcommand = scouting_text_scrollbar)
            scouting_text_pane.pack(side=tk.TOP, fill=tk.X, padx=0, pady=1)
            scouting_text_scrollbar.pack(side=tk.TOP, fill=tk.BOTH, padx=0, pady=2)
            scouting_text_scrollbar.config(command=scouting_text_pane.xview)
            
            raw_team_scouting = self.raw_scouting.get(team, [])
            scouting_string_list = [get_column_string()]
            for match, line_data in raw_team_scouting:
                scouting_string_list.append(get_match_scouting_string(match, line_data))
                
            for s in scouting_string_list:
                scouting_text_pane.insert(tk.INSERT, s + '\n')
            
            for category in self.game.categories:
                scenario = tuple([category.pretty_name])
                TRIALS = 10000
                prediction = self.game.predict(teams, blue_teams, me.null_evaluate, TRIALS, scenario, self.year)
                if not first:
                    tk.Label(self.team_summary_inner_frame, text=' ').pack(side=tk.TOP, padx=0, pady=5)
                label = tk.Label(self.team_summary_inner_frame, text=category.pretty_name + ':')
                label.pack(side=tk.TOP, padx=5, pady=5)
                graph_frame = GraphDataPanel(self.team_summary_inner_frame, prediction[0], g_height=300, max_width=650, red_and_blue=False)
                graph_frame.pack(side=tk.TOP, padx=5, pady=5)
                
                first = False
                
#            self.team_summary_canvas.configure(scrollregion=self.team_summary_canvas.bbox('all'))
                        
#            self.team_summary_canvas.config(width=1300,height=600)
#            self.team_summary_scroll.on_frame_configure(None)
        #end team summary methods
        
        self.parent.title("ZScout")
        self.pack(fill=tk.BOTH, expand=True)
        
        def config_canvas(canvas, width=1343, height=662):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.config(width=width,height=height)
        
        #make menu
        self.menubar = tk.Menu(self)
        self.frame_select = tk.Menu(self.menubar, tearoff=0)
        self.frame_select.add_command(label='Graphs', command=go_to_graph_frame)
        self.frame_select.add_command(label='Summary', command=go_to_summary_frame)
        self.frame_select.add_command(label='Competition', command=go_to_scouting_frame)
        self.frame_select.add_command(label='Teams', command=go_to_teams_frame)
        self.menubar.add_cascade(label='Sections', menu=self.frame_select)
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
        
        self.graph_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        self.graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.active_frame = self.graph_frame
        
        self.team_numbers_label = tk.Label(self.graph_frame, text="Team Number(s):")
        self.team_numbers_label.pack(side=tk.TOP, padx=5, pady=2)
        
        self.team_numbers_field = tk.Entry(self.graph_frame, width=29)
        self.team_numbers_field.pack(side=tk.TOP, padx=5, pady=2)
        
        self.do_prediction_button = tk.Button(self.graph_frame, text="Do Prediction", command=do_prediction)
        self.do_prediction_button.pack(side=tk.TOP, padx=5, pady=2)
        
        self.show_button = tk.Button(self.graph_frame, text="Show Graph", command=show_graph)
        self.show_button.pack(side=tk.TOP, padx=5, pady=2)

        self.graph_type = tk.StringVar()
        self.margins_button = tk.Radiobutton(self.graph_frame, text="Margin Graph", var=self.graph_type, value="margin")
        
        self.categories_container = tk.Frame(self.graph_frame)
        self.categories_container.pack(side=tk.TOP, pady=2)
        self.has_categories = False
        self.category_frame = None
        
        self.probs = tk.StringVar()
        self.probs_label = tk.Label(self.graph_frame, textvariable=self.probs)
        self.probs_label.pack(side=tk.TOP, pady=2)
        
        self.has_graph = False
        #end make graph frame
        
        #make team summary frame
        
        self.team_summary_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        
        self.team_summary_x_scroll = tk.Scrollbar(self.team_summary_frame, orient=tk.HORIZONTAL)
        self.team_summary_x_scroll.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.team_summary_y_scroll = tk.Scrollbar(self.team_summary_frame, orient=tk.VERTICAL)
        self.team_summary_y_scroll.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.team_summary_canvas = tk.Canvas(self.team_summary_frame, xscrollcommand=self.team_summary_x_scroll.set, yscrollcommand=self.team_summary_y_scroll.set)
        self.team_summary_canvas.grid(row=0, column=0)
        
        self.team_summary_canvas_frame = tk.Frame(self.team_summary_canvas)
        self.team_summary_canvas_frame.bind('<Configure>', lambda e: config_canvas(self.team_summary_canvas))
        
        self.team_summary_canvas.create_window((0,0), window=self.team_summary_canvas_frame, anchor='nw', tags='self.team_summary_canvas_frame')
        
        self.team_summary_x_scroll.config(command=self.team_summary_canvas.xview)
        self.team_summary_y_scroll.config(command=self.team_summary_canvas.yview)
        
        self.team_summary_team_label = tk.Label(self.team_summary_canvas_frame, text='Team:')
        self.team_summary_team_label.pack(side=tk.TOP, padx=5, pady=5)
        
        self.team_summary_team_field = tk.Entry(self.team_summary_canvas_frame)
        self.team_summary_team_field.pack(side=tk.TOP, padx=5, pady=5)
        
        self.team_summary_button = tk.Button(self.team_summary_canvas_frame, command=show_summary, text='Show Summary')
        self.team_summary_button.pack(side=tk.TOP, padx=5, pady=5)
        
        self.team_summary_inner_frame = tk.Frame(self.team_summary_canvas_frame, relief=tk.RAISED, borderwidth=1)
        #end make team summary frame
        
        #make competition frame
        
        #vars
        self.error = tk.StringVar()
        self.contrs_from_team_from_category = {}
        self.categories = []
        #end vars
        
        self.scouting_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        self.comp_label = tk.Label(self.scouting_frame, text="Competition:")
        self.comp_label.pack(side=tk.TOP, padx=5, pady=5)

        self.comp_choose = tk.Entry(self.scouting_frame)
        self.comp_choose.pack(side=tk.TOP, padx=5, pady=5)

        self.comp_button = tk.Button(self.scouting_frame, text="Accept", command=set_comp)
        self.comp_button.pack(side=tk.TOP, padx=5, pady=5)

        self.error_label = tk.Label(self.scouting_frame, textvariable=self.error)
        self.error_label.pack(side=tk.TOP, pady=5)
        #end make competition frame
        
        #make teams frame
        
        self.teams_frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        
        self.teams_scroll = tk.Scrollbar(self.teams_frame, orient=tk.VERTICAL)
        self.teams_scroll.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.teams_canvas = tk.Canvas(self.teams_frame, yscrollcommand=self.teams_scroll.set)
        self.teams_canvas.grid(row=0, column=0)
        
        self.teams_mid_frame = tk.Frame(self.teams_canvas, relief=tk.RAISED, borderwidth=1)
        self.teams_mid_frame.bind('<Configure>', lambda e: config_canvas(self.teams_canvas, width=150, height=662))
        
        self.teams_canvas.create_window((0,0), window=self.teams_mid_frame, anchor='nw', tags='self.teams_mid_frame')
        
        self.teams_scroll.config(command=self.teams_canvas.yview)
        
        self.teams_inner_frame = tk.Frame(self.teams_mid_frame, relief=tk.RAISED, borderwidth=1)
        self.teams_inner_frame.pack(side=tk.TOP)
        
        #end make teams frame

def is_full_match(matches):
    """Return False if the matches have 0 for each blue score. Otherwise, return True."""
    result = False
    for match in matches:
        if match[1] != 0:
            result = True
    return result

class CategoryChooserPanel(tk.Frame):
    """A panel that lets the user choose which categories and scenarios will be used."""
    
    def __init__(self, parent, options):
        """Make a CategoryChoosePanel with the passed categories.
        
        Arguments:
            parent -- the parent of the CategoryChooserPanel
            options -- the categories and scenarios the user can choose from
        """
        tk.Frame.__init__(self, parent, background="white")
        self.pack(fill=tk.BOTH, expand=True)
        
        self.all_var = tk.IntVar()
        all_check = tk.Checkbutton(self, text="All", variable=self.all_var)
        all_check.pack(side=tk.TOP, pady=3)
        
        self.vars_from_names = {}
        
        for category in options:
            var = tk.IntVar()
            check = tk.Checkbutton(self, text=category, variable=var)
            check.pack(side=tk.TOP, pady=3)
            self.vars_from_names[category] = var

    def get_categories(self):
        """Return the names of the selected categories and scenarions."""
        if self.all_var.get():
            return self.vars_from_names.copy()
        result = []
        for name in self.vars_from_names:
            if self.vars_from_names[name].get():
                result.append(name)
        return result
        
class GraphDataPanel(tk.Frame): #clean up
    """A Panel that shows predicted match score information in a graph."""
    
    def __init__(self, parent, match_data, g_height=600, max_width = 1300, pix_per_margin=None, text_pad=16, red_and_blue=True, num_margins=None): #num_probs = 401 pix_per_prob = 3
        """Make a GraphDataPanel.
        
        Arguments:
            parent -- the parent of the GraphDataPanel
            match_data -- the match score data to show in the graph
        
        Keyword Arguments:
            g_height -- the height of the graph (default 600)
            max_width -- the maximum width of the graph (default 1300)
            pix_per_margin -- how many pixels each bar gets (default None)
            text_pad -- how much padding to have for the bar labels (default 16)
            num_margins -- how many margins to show on the graph (default None)
        """
        MARGIN_TIERS = [1, 5, 15, 25, 50, 100, 150, 200, 250, 300]#, 350, 400, 450, 500]
#        TWO_SIDE_MARGIN_TIERS = [(2*t)+1 for t in ONE_SIDE_MARGIN_TIERS]
        
        self.pad = 2
        
        tot_height = g_height + text_pad
        
        def get_margin(match):
            """Return the margin of the match's scores. Matches blue wins in have a negative margin."""
            return match[0] - match[1]
        
        def data_sort(match):
            """Return the margin of the match's scores. Used as a sort key."""
            return get_margin(match)

        def get_x(margin):
            """Return the x value of the center of the bar for the margin."""
            #return pix_per_margin * (num_margins // 2 + 1) + (margin + self.pad) * pix_per_margin
            return pix_per_margin * (((num_margins // 2) if red_and_blue else 0) + margin + 1)

        def get_y(prob):
            """Return the y value of the top of a bar representing this prob."""
            if prob == 0:
                return text_pad + g_height
            return text_pad + min(g_height - 1, (1 - prob) * g_height)
            #return  min(g_height, round(g_height - prob * g_height)) + text_pad
        
        def get_num_margins(max_red_margin, max_blue_margin):
            """Return the number of margins to be used.
            
            Arguments:
                max_red_margin -- the maximum red margin
                max_blue_margin -- the maximum blue margin
            """
            if num_margins == None:
                result = None
                result = max(max_red_margin, max_blue_margin)#*2 + 1
                for tier in MARGIN_TIERS:#(TWO_SIDE_MARGIN_TIERS if red_and_blue else ONE_SIDE_MARGIN_TIERS):
                    if result <= tier:
                        result = tier*2+1 if red_and_blue else tier
                        #print('num_margins: ' + result.__str__())
                        return result
                tier = MARGIN_TIERS[-1]
                return tier*2+1 if red_and_blue else tier
            return num_margins
        
        def get_one_side_margins():
            return (num_margins // 2 - 1) if red_and_blue else num_margins
        
        def get_pix_per_margin():
            """Return how many pixels wide each bar should be."""
            if pix_per_margin == None:
                result = math.floor(max_width / (num_margins + 1))
                return result
            return pix_per_margin
        
        tk.Frame.__init__(self, parent, background="white")
        
        max_red_margin = 0
        max_blue_margin = 0
        for match in match_data:
            if match_data[match] > 0:
                max_red_margin = max(max_red_margin, abs(get_margin(match)))
                max_blue_margin = max(max_blue_margin, abs(-get_margin(match)))
        
        num_margins = get_num_margins(max_red_margin, max_blue_margin)
        pix_per_margin = get_pix_per_margin()
        
        #self.canvas = tk.Canvas(self, width=(num_probs + self.pad*2)*pix_per_prob + 1, height=tot_height, bd=1, bg="white")
        self.canvas = tk.Canvas(self, width=get_x((num_margins // 2) if red_and_blue else num_margins) + 1*pix_per_margin, height=tot_height, bd=1, bg="white")
        self.canvas.pack(side=tk.TOP)
        
        match_keys = []
        match_keys.extend(match_data.keys())
        match_keys.sort(key=data_sort)
        
        margins = []
        probs_from_margins = {}

        h_w = pix_per_margin // 2
        
        light_gray = "#efefef"
        darker_gray = "#dfdfdf"
        even_darker_gray = "#9f9f9f"
        
        for margin in range((-5*math.floor((num_margins // 2)/5)) if red_and_blue else 0, 5*math.ceil(((num_margins // 2) if red_and_blue else num_margins)/5) + 1, 5):
            #x = PIX_PER_PROB * (num_probs // 2 + 1) + margin * PIX_PER_PROB
            x = get_x(margin)
            top = 15

            if margin % 10 == 0:
                if margin == 0:
                    self.canvas.create_line(x, tot_height, x, top, fill = even_darker_gray)
                else:
                    self.canvas.create_line(x, tot_height, x, top, fill = darker_gray)
                self.canvas.create_text(x, 8, text=abs(margin).__str__())
            else:
                self.canvas.create_line(x, tot_height, x, top, fill = light_gray)
        self.canvas.create_line(0, tot_height, get_x(num_margins / 2 + 5), tot_height)
        self.canvas.create_line(0, get_y(1.0), get_x(num_margins / 2 + 5), get_y(1.0))#, fill = light_gray)
        self.canvas.create_line(0, get_y(0.75), get_x(num_margins / 2 + 5), get_y(0.75), fill = light_gray)
        self.canvas.create_line(0, get_y(0.5), get_x(num_margins / 2 + 5), get_y(0.5), fill = light_gray)
        self.canvas.create_line(0, get_y(0.25), get_x(num_margins / 2 + 5), get_y(0.25), fill = light_gray)
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
        self.red_prob = 0
        self.blue_prob = 0
        self.tie_prob = 0
        for margin in margins:
            prob = probs_from_margins[margin]
            y = get_y(prob)
            x = get_x(margin)
            r_fill=""
            if margin > 0:
                r_fill = "red"
                self.red_prob += prob
            elif margin < 0:
                r_fill = "blue"
                self.blue_prob += prob
            else:
                r_fill = "magenta"
                self.tie_prob += prob

            if not y == tot_height:
                self.canvas.create_rectangle(x-h_w, tot_height, x+h_w, y, fill=r_fill)

def main():
    """Run ZScout."""
    root = tk.Tk()
    root.geometry('350x250+300+300')
    tk.app = ZScoutFrame(root)
    root.mainloop()  

if __name__ == '__main__':
    main()
