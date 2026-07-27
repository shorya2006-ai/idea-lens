import json
import os
#----------Search History--------

SEARCH_HISTORY_FILE = "search_history.json"


def load_search_history():

    if not os.path.exists(SEARCH_HISTORY_FILE):
        return {}
try:
    with open(SEARCH
