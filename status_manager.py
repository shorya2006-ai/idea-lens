import json
import os
#----------------IDEA STATUS--------------
IDEA_STATUS_FILE = "idea_status.json"


def load_idea_status():

    if not os.path.exists(IDEA_STATUS_FILE):
        return {}
