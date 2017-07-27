# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 19:30:12 2017

@author: rober
"""

import requests
import os
import datetime
import ast

URL_BASE = "https://www.thebluealliance.com/api/v2/"
HEADER = {"X-TBA-App-Id":"FRC830:z_scout:1.0"}

comp_cache_initialized = False
comp_cache = {}

dir_path = ""
file_name = ""

def update_comp_cache():
    global file_name
    
    cache_file = open(file_name, "w")
    cache_file.write(comp_cache.__repr__())
    cache_file.close()

def init_check():
    global comp_cache, comp_cache_initialized, dir_path, file_name
    
    if not comp_cache_initialized:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_name = dir_path + "\\comp_cache.zsc"
        comp_cache_initialized = True
        try:
            cache_file = open(file_name, "r")
            data = cache_file.read()
            if len(data) == 0:
                data = "{}"
            comp_cache = ast.literal_eval(data)
            cache_file.close()
        except FileNotFoundError:
            cache_file = open(file_name, "w") #create file
            comp_cache = {}

def request_competition(event):
    global URL_BASE, HEADER
    
    MATCH_URL_EXT = "event/%s/matches"
    source = (URL_BASE + MATCH_URL_EXT) % event
    matches = requests.get(source, headers = HEADER).json()
    EVENT_URL_EXT = "event/" + event
    event_data = requests.get(URL_BASE + EVENT_URL_EXT, headers=HEADER).json()
    
    return matches, event_data

def get_competition(event):
    init_check()

    if event in comp_cache:
        try:
            event_data_url = URL_BASE + "event/" + event
            event_data = requests.get(event_data_url, headers = HEADER).json()
            end_date_string = event_data["end_date"].replace("-", " ")
            tokens = end_date_string.split()
            year = int(tokens[0])
            month = int(tokens[1])
            day = int(tokens[2])

            end_date = datetime.datetime(year, month, day)
            now = datetime.datetime.now()
            now = datetime.datetime(now.year, now.month, now.day)
            if end_date < now:
                if comp_cache[event + ' done'] == True:
                    return comp_cache[event]
                
            result = request_competition(event)
            comp_cache[event] = result #even though the cache has the event, there might be new matches
            comp_cache[event + ' done'] = end_date < now
            update_comp_cache()
            return result
        except requests.exceptions.ConnectionError:
            return comp_cache[event]
    else:
        try:
            event_data_url = URL_BASE + "event/" + event
            event_data = requests.get(event_data_url, headers = HEADER).json()
            end_date_string = event_data["end_date"].replace("-", " ")
            tokens = end_date_string.split()
            year = int(tokens[0])
            month = int(tokens[1])
            day = int(tokens[2])
            
            end_date = datetime.datetime(year, month, day)
            now = datetime.datetime.now()
            now = datetime.datetime(now.year, now.month, now.day)
            
            result = request_competition(event)
            comp_cache[event] = result
            comp_cache[event + ' done'] = end_date < now
            update_comp_cache()
            return result
        except requests.exceptions.ConnectionError:
            return None

def get_matches_before(competition, match_number):
    result = []
    for match in competition:
        if match["match_number"] < match_number:
            result.append(match)
    return result

def segment_competition(competition, segmenter):
    result = {}
    for match in competition:
        if(match['comp_level'] == 'qm' and not match['score_breakdown'] == None):
            #print(segmenter)
            side_matches = segmenter(match)
            #segments = match_segmenter.segment(match)
            for side_match in side_matches:
                for key in side_match:
                    if not (key in result):
                        result[key] = []
                    add = side_match[key]
                    if not add == None:
                        if(not add in result[key]):
                            result[key].append(add)
    return result