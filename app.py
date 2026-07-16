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
# ---------------- EMPLOYEE PDF ----------------
def load_employee_ids_from_pdf(pdf_path="employee_database_100.pdf"):
emp_ids = set()
try:
with pdfplumber.open(pdf_path) as pdf:
for page in pdf.pages:
text = page.extract_text()
if text:
for line in text.split("\n"):
parts = line.split()
if parts and parts[0].startswith("EMP"):
emp_ids.add(parts[0])
except:
pass
return emp_ids
if "pending_status_file" not in st.session_state:
st.session_state.pending_status_file = None
# ---------------- ADMIN PDF ----------------
def load_admin_credentials_from_pdf(pdf_path="admin_database_5.pdf"):
admins = {}
try:
with pdfplumber.open(pdf_path) as pdf:
for page in pdf.pages:
text = page.extract_text()
for line in text.split("\n"):
parts = line.split()
if len(parts) >= 4 and parts[0].startswith("ADM"):
admins[parts[0]] = {
"name": parts[1] + " " + parts[2],
"password": parts[3]
}
except:
pass
return admins
# ---------------- TEXT EXTRACTION ----------------
def extract_text_from_file(uploaded_file):
text = ""
try:
filename = uploaded_file.name.lower()
if filename.endswith(".pdf"):
with pdfplumber.open(uploaded_file) as pdf:
for page in pdf.pages:
text += page.extract_text() or ""
elif filename.endswith(".docx"):
doc = Document(uploaded_file)
for para in doc.paragraphs:
text += para.text + "\n"
elif filename.endswith(".pptx"):
prs = Presentation(uploaded_file)
for slide in prs.slides:
for shape in slide.shapes:
if hasattr(shape, "text"):
text += shape.text + "\n"
else:
text = uploaded_file.read().decode(errors="ignore")
except:
text = ""
return text
# ---------------- AI EXPLANATION ----------------
def generate_ai_explanation(input_text, matched_text, score):
try:
if not matched_text:
return "No matched content available to generate explanation."
input_words = set(input_text.lower().split())
matched_words = set(matched_text.lower().split())
common_words = list(input_words.intersection(matched_words))
if score > 0.75:
level = "highly similar"
elif score > 0.5:
level = "moderately similar"
else:
level = "mostly different"
explanation = f"The ideas are {level}."
if common_words:
explanation += " Common keywords include: " + ", ".join(common_words[:8])
else:
explanation += " There are no strong overlapping keywords but conceptual similarity exists."
