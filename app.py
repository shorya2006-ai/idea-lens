import json
import pandas as pd
import plotly.express as px
import streamlit as st
import os
import pdfplumber

from pathlib import Path
from datetime import datetime
from groq_helper import generate_groq_analysis
from docx import Document
from pptx import Presentation
from vector_db import (
    search_similar,
    add_new_idea,
    initialize_from_pdfs,
    load_index
)

# ---------------- INIT ----------------

initialize_from_pdfs()

st.set_page_config(
    page_title="AI Idea Detector",
    layout="wide"
)

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "user_type" not in st.session_state:
    st.session_state.user_type = None

if "search_history" not in st.session_state:
    st.session_state.search_history = []

# ---------------- EMPLOYEE PDF ----------------

def load_employee_ids_from_pdf(
    pdf_path="employee_database_100.pdf"
):
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


# ---------------- ADMIN PDF ----------------

def load_admin_credentials_from_pdf(
    pdf_path="admin_database_5.pdf"
):
    admins = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text:
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
            explanation += (
                " Common keywords include: "
                + ", ".join(common_words[:8])
            )
        else:
            explanation += (
                " There are no strong overlapping keywords "
                "but conceptual similarity exists."
            )

        return explanation

    except:
        return "AI explanation could not be generated"


# ---------- CONTRIBUTOR ANALYTICS ----------

CONTRIBUTOR_FILE = "contributions.json"


def load_contributions():
    try:
        if os.path.exists(CONTRIBUTOR_FILE):
            with open(CONTRIBUTOR_FILE, "r") as f:
                return json.load(f)
    except:
        pass

    return {}


def save_contributions(data):
    try:
        with open(CONTRIBUTOR_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass


def increment_contribution(emp_id):
    try:
        data = load_contributions()
        data[emp_id] = data.get(emp_id, 0) + 1
        save_contributions(data)
    except:
        pass


def get_top_contributors(top_n=5):
    try:
        data = load_contributions()

        sorted_data = sorted(
            data.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_data[:top_n]

    except:
        return []


# ---------------- SEARCH HISTORY ----------------

SEARCH_HISTORY_FILE = "search_history.json"


def load_search_history():
    if not os.path.exists(SEARCH_HISTORY_FILE):
        return {}
# ---------------- IDEA STATUS ----------------

IDEA_STATUS_FILE = "idea_status.json"


def load_idea_status():
    if not os.path.exists(IDEA_STATUS_FILE):
        return {}

    try:
        with open(IDEA_STATUS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_idea_status(data):
    with open(IDEA_STATUS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_idea_status(file_name, employee):
    data = load_idea_status()

    data[file_name] = {
        "employee": employee,
        "status": "Pending",
        "viewed": False
    }


    try:
        with open(SEARCH_HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

 save_idea_status(data)


def update_idea_status(file_name, status):
    data = load_idea_status()

    if file_name in data:
        data[file_name]["status"] = status
        data[file_name]["viewed"] = True

    save_idea_status(data)


# ---------------- SEARCH HISTORY ----------------

SEARCH_HISTORY_FILE = "search_history.json"


def load_search_history():
    if not os.path.exists(SEARCH_HISTORY_FILE):
        return {}

    try:
        with open(SEARCH_HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_search_history(data):
    with open(SEARCH_HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_search_history(emp_id, search_text):
    data = load_search_history()

    if emp_id not in data:
        data[emp_id] = []

    data[emp_id].append(search_text)

    save_search_history(data)

# ---------------- DASHBOARD ----------------

if st.session_state.page == "dashboard":

    st.markdown(
        "<h1 style='text-align:center;'>AI Idea Duplicate Detector</h1>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Admin Login", use_container_width=True):
            st.session_state.page = "admin_login"

    with col2:
        if st.button("Employee Login", use_container_width=True):
            st.session_state.page = "employee_login"


# ---------------- ADMIN LOGIN ----------------

elif st.session_state.page == "admin_login":

    st.title("Admin Login")

    admin_id = st.text_input("Admin ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        admins = load_admin_credentials_from_pdf()

        if (
            admin_id in admins and
            password == admins[admin_id]["password"]
        ):
            st.session_state.user_type = "admin"
            st.session_state.admin_name = admins[admin_id]["name"]
            st.session_state.page = "main"

        else:
            st.error("Invalid credentials")


# ---------------- EMPLOYEE LOGIN ----------------

elif st.session_state.page == "employee_login":

    st.title("Employee Login")

    emp_id = st.text_input("Employee ID")

    if st.button("Login"):

        valid_ids = load_employee_ids_from_pdf()

        if emp_id in valid_ids:
            st.session_state.user_type = "employee"
            st.session_state.emp_id = emp_id
            st.session_state.page = "main"

        else:
            st.error("Invalid Employee ID")
# ---------------- MAIN ----------------

elif st.session_state.page == "main":

    # Top Bar
    col1, col2 = st.columns([10, 1])

    with col1:
        st.title("AI Idea Duplicate Detector")

    with col2:
        if st.button("Logout"):
            st.session_state.page = "dashboard"
            st.session_state.user_type = None
            st.rerun()

    # ---------------- ADMIN CONTROLS ----------------

    if st.session_state.user_type == "admin":

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Revisit Idea"):
                update_idea_status(
                    st.session_state.selected_preview_file,
                    "Revisit"
                )
                st.success("Idea marked for revisit.")
                st.rerun()

        with col2:
            if st.button("Idea Approved"):
                update_idea_status(
                    st.session_state.selected_preview_file,
                    "Approved"
                )
                st.success("Idea approved.")
                st.rerun()

        with col3:
            if st.button("Idea Implemented"):
                update_idea_status(
                    st.session_state.selected_preview_file,
                    "Implemented"
                )
                st.success("Idea implemented.")
                st.rerun()

        st.write(f"Admin: {st.session_state.admin_name}")
 # ---------------- CONTRIBUTOR GRAPH ----------------

    from collections import Counter

    def get_top_contributors():
        _, metadata = load_index()

        contributors = []

        for item in metadata:
            source = item.get("source", "")

            if "(" in source and ")" in source:
                try:
                    employee = source.split("(")[-1].replace(")", "").strip()
                    contributors.append(employee)
                except:
                    pass

        counts = Counter(contributors)

        return list(counts.items())


    top_contributors = get_top_contributors()

    if top_contributors:

        df = pd.DataFrame(
            top_contributors,
            columns=[
                "Employee ID",
                "Ideas Submitted"
            ]
        )

        fig = px.bar(
            df,
            x="Employee ID",
            y="Ideas Submitted",
            title="Contributor's Graph"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        table_df = df.copy()

        table_df.insert(
            0,
            "S.No",
            range(1, len(table_df) + 1)
        )

        st.subheader("Contributor Details")

        styled_df = (
            table_df.style
            .set_properties(**{"text-align": "center"})
            .set_table_styles([
                {
                    "selector": "th",
                    "props": [("text-align", "center")]
                }
            ])
        )

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.sidebar.info("No contributions recorded yet.")
 # ---------------- EMPLOYEE VIEW ----------------

    if st.session_state.user_type == "employee":
        st.write(f"Employee: {st.session_state.emp_id}")

    data_folder = "pdf_data"
    os.makedirs(data_folder, exist_ok=True)

    all_files = os.listdir(data_folder)

    # ---------------- ADMIN PENDING APPROVALS ----------------

    if st.session_state.user_type == "admin":

        idea_data = load_idea_status()

        pending = [
            file
            for file, details in idea_data.items()
            if details["viewed"] == False
        ]

        st.sidebar.markdown("---")
        st.sidebar.subheader("Pending For Your Approval")

        if pending:
            for item in pending:
                st.sidebar.write(item)
        else:
            st.sidebar.success("No Pending Approvals")

    # ---------------- SIDEBAR FILE SEARCH ----------------

    st.sidebar.header("Files")

    search = st.sidebar.text_input("Search")

    if search and len
if filtered:

    selected_file = st.sidebar.selectbox(
        "Select File",
        filtered
    )

    if (
        st.session_state.user_type == "admin"
        and selected_file
    ):

        file_path = os.path.join(
            data_folder,
            selected_file
        )

        try:

            class UploadedFileMock:

                def _init_(self, path):
                    self.name = path.name
                    self.type = ""
                    self.file = open(path, "rb")

                def read(self):
                    return self.file.read()

            preview_content = extract_text_from_file(
                UploadedFileMock(Path(file_path))
            )

            st.subheader("Idea Content")

            st.text_area(
                "Preview",
                preview_content,
                height=400
            )

        except Exception as e:
            st.warning(f"Preview unavailable: {e}")

    if os.path.exists(file_path):

        col1, col2 = st.sidebar.columns(2)

        with col1:
            with open(file_path, "rb") as file:
                st.download_button(
                    label="Download File",
                    data=file.read(),
                    file_name=selected_file,
                    mime="application/octet-stream",
                    key="download_btn"
                )

        if st.session_state.user_type == "admin":

            with col2:
                if st.button(
                    "Delete File",
                    key="delete_file_btn"
                ):

                    try:
                        os.remove(file_path)
                        st.success(
                            f"{selected_file} deleted successfully."
                        )
                        st.rerun()

                    except Exception as e:
                        st.error(
                            f"Error deleting file: {str(e)}"
                        )

else:
    st.sidebar.info("No files found")
# ---------------- UPLOAD HISTORY ----------------

st.sidebar.markdown("---")
st.sidebar.markdown("### Upload History")

_, metadata = load_index()

uploads_by_employee = {}

for item in metadata:

    source = item.get("source", "")

    if "(" in source and ")" in source:

        try:
            employee = source.split("(")[-1].replace(")", "").strip()

            if employee not in uploads_by_employee:
                uploads_by_employee[employee] = []

            uploads_by_employee[employee].append(source)

        except:
            pass


# -------- Employee Upload History --------

if st.session_state.user_type == "employee":

    emp_id = st.session_state.emp_id

    employee_uploads = uploads_by_employee.get(
        emp_id,
        []
    )

    if employee_uploads:

        for upload in reversed(employee_uploads[-10:]):
            st.sidebar.write(upload)

    else:
        st.sidebar.info("No uploads found.")


# -------- Admin Upload History --------

elif st.session_state.user_type == "admin":

    employee_list = sorted(
        uploads_by_employee.keys()
    )

    if employee_list:

        selected_employee = st.sidebar.selectbox(
            "Select Employee Upload History",
            employee_list,
            key="upload_history_selector"
        )

        employee_uploads = uploads_by_employee.get(
            selected_employee,
            []
        )

        if employee_uploads:

            for upload in reversed(employee_uploads[-20:]):
                st.sidebar.write(upload)

        else:
            st.sidebar.info("No uploads found.")
# ---------------- SEARCH HISTORY ----------------

st.sidebar.markdown("---")
st.sidebar.subheader("Search History")

history_data = load_search_history()

if st.session_state.user_type == "employee":

    emp_id = st.session_state.emp_id

    employee_history = history_data.get(
        emp_id,
        []
    )

    if employee_history:

        for search in reversed(employee_history[-10:]):
            st.sidebar.write(search)

    else:
        st.sidebar.info("No search history.")

elif st.session_state.user_type == "admin":

    all_employees = sorted(history_data.keys())

    if all_employees:

        selected_employee = st.sidebar.selectbox(
            "Select Employee",
            all_employees
        )

        employee_history = history_data.get(
            selected_employee,
            []
        )

        if employee_history:

            for search in reversed(employee_history[-20:]):
                st.sidebar.write(search)

        else:
            st.sidebar.info(
                "No search history available."
            )
# ---------------- INPUT ----------------

uploaded_file = st.file_uploader(
    "Upload File",
    type=["pdf", "docx", "pptx"]
)

idea = st.text_area(
    "Enter Idea *",
    placeholder="Enter your idea here...",
    help="This field is mandatory. File upload is optional."
)

final_input = ""

col1, col2 = st.columns(2)

with col1:
    check_clicked = st.button("Check Similarity")

with col2:
    upload_clicked = st.button("Upload Idea")

# ---------------- CHECK SIMILARITY ----------------

if check_clicked:

    if not idea.strip():
        st.error("Please enter an idea before checking similarity.")
        st.stop()

    final_input = idea.strip()

    if uploaded_file:
        file_text = extract_text_from_file(uploaded_file)

        final_input = f"""
User Idea:
{idea}

Supporting Document:
{file_text}
"""

# ---------------- UPLOAD IDEA ----------------

if upload_clicked:

    user = st.session_state.get("emp_id", "admin")

    if not idea.strip():
        st.error("Please enter an idea before uploading.")
        st.stop()

    # Duplicate Check
    duplicate_results = search_similar(
        idea.strip(),
        k=1
    )

    if duplicate_results:

        duplicate_score = duplicate_results[0]["score"]

        if duplicate_score >= 0.70:
            st.error(
                "You cannot upload the file as similar idea already exists in the repository."
            )
            st.stop()

    # -------- Upload with File --------

    if uploaded_file:

        existing_files = os.listdir(data_folder)

        if uploaded_file.name in existing_files:
            st.error(
                "This file already exists in the repository."
            )
            st.stop()

        text = extract_text_from_file(uploaded_file)

        add_new_idea(
            text,
            source=f"{uploaded_file.name} ({user})"
        )

        add_idea_status(
            uploaded_file.name,
            user
        )
# -------- Manual Idea --------

    else:

        results = search_similar(
            idea.strip(),
            k=1
        )

        if results:

            score = results[0]["score"]

            if score >= 0.70:
                st.error(
                    "You can't upload the file. A highly similar idea already exists in the repository."
                )
                st.stop()

        manual_name = (
            f"Manual_Idea_{user}{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        add_new_idea(
            idea.strip(),
            source=f"Manual Idea ({user})"
        )

        add_idea_status(
            manual_name,
            user
        )

    st.success("Idea uploaded successfully!")
