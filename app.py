import os
import streamlit as st
from pathlib import Path
from datetime import datetime

from vector_db import (
    search_similar,
    add_new_idea,
    load_index,
    initialize_from_pdfs
)
