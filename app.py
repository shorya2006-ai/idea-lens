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
