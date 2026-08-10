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
from auth import (
    load_employee_ids_from_pdf,
    load_admin_credentials_from_pdf,
    extract_text_from_file,
    generate_ai_explanation
)

from status_manager import (
    load_idea_status,
    save_idea_status,
    add_idea_status,
    update_idea_status,
    mark_notification_as_read
)
from contributor_manager import (
    get_top_contributors
)

from history_manager import (
    load_search_history,
    save_search_history,
    add_search_history
)
from admin_dashboard import (
    show_admin_dashboard
)

from employee_dashboard import (
    show_employee_dashboard
)
