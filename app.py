from importlib.metadata import metadata
import json
import pandas as pd
import plotly.express as px
import streamlit as st
import os
import pdfplumber
import time
data_folder = "pdf_data"
os.makedirs(data_folder, exist_ok=True)
from collections import Counter
from pathlib import Path
from datetime import datetime
from groq_helper import generate_groq_analysis
from docx import Document
from pptx import Presentation
from vector_db import search_similar, add_new_idea, initialize_from_pdfs, load_index
# ---------------- INIT ----------------
initialize_from_pdfs()
st.set_page_config(page_title="AI Idea Detector", layout="wide")
if "page" not in st.session_state:
st.session_state.page = "dashboard"
if "user_type" not in st.session_state:
st.session_state.user_type = None
if "search_history" not in st.session_state:
st.session_state.search_history = []
if "selected_review_file" not in st.session_state:
st.session_state.selected_review_file = None
if "pending_status_action" not in st.session_state:
st.session_state.pending_status_action = None
if "pending_status_file" not in st.session_state:
st.session_state.pending_status_file = None
