#!/usr/bin/env python3
"""
Kalinga University - Student Report Card (Desktop GUI)
----------------------------------------------------------------------
A Tkinter desktop application version of the result-sheet, styled as a
university report card.

Features
  - University header with crest/logo
  - Dropdown selectors: Programme (Department/Course) and Semester
  - Auto-loads the correct subject list for the selected Programme + Semester
  - Editable "Obtained" marks (External / Internal) per subject
  - Automatic Pass/Fail per subject (>=40% in external, internal AND total)
  - Overall percentage, grade band and result badge
  - Next-semester performance prediction
  - Embedded bar chart (course-wise % + current % + predicted %)

Run with:
    pip install matplotlib pillow --break-system-packages   (if not already installed)
    python3 report_card_app.py

Note on the logo:
  The official Kalinga University logo is bundled in an "assets" folder next
  to this script (assets/kalinga_university_logo.png) and loads automatically.
  Keep the "assets" folder alongside report_card_app.py when you copy/move it.
"""

import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ----------------------------------------------------------------------
# 1. DATA
# ----------------------------------------------------------------------

PROGRAMME_COURSES = {
    "B.Tech Computer Science": {
        1: [["CS101", "Programming Fundamentals"], ["MA101", "Engineering Mathematics I"],
            ["PH101", "Engineering Physics"], ["HU101", "Communication Skills"],
            ["CS102", "Computer Workshop"]],
        2: [["CS201", "Data Structures"], ["MA201", "Engineering Mathematics II"],
            ["EC201", "Digital Electronics"], ["CS202", "Object Oriented Programming"],
            ["EVS201", "Environmental Studies"]],
        3: [["CS301", "Database Management Systems"], ["CS302", "Operating Systems"],
            ["CS303", "Computer Networks"], ["MA301", "Discrete Mathematics"],
            ["CS304", "Web Technologies"]],
        "default": [["CS401", "Software Engineering"], ["CS402", "Design and Analysis of Algorithms"],
                    ["CS403", "Computer Architecture"], ["CS404", "Java Programming"],
                    ["CS405", "Python Programming"]],
    },
    "BCA": {
        1: [["BCA101", "Computer Fundamentals"], ["BCA102", "Programming in C"],
            ["BCA103", "Mathematics for Computing"], ["BCA104", "Digital Logic"],
            ["BCA105", "Communication Skills"]],
        2: [["BCA201", "Data Structures Using C"], ["BCA202", "Database Management System"],
            ["BCA203", "Object Oriented Programming"], ["BCA204", "Computer Organization"],
            ["BCA205", "Environmental Studies"]],
        3: [["BCA301", "Web Development"], ["BCA302", "Operating System"],
            ["BCA303", "Software Engineering"], ["BCA304", "Computer Networks"],
            ["BCA305", "Python Programming"]],
        "default": [["BCA401", "Java Programming"], ["BCA402", "Data Analytics"],
                    ["BCA403", "Cloud Computing"], ["BCA404", "Cyber Security"],
                    ["BCA405", "Project Work"]],
    },
    "B.Sc Information Technology": {
        1: [["IT101", "IT Fundamentals"], ["IT102", "Programming Logic"],
            ["IT103", "Mathematics I"], ["IT104", "Digital Systems"],
            ["IT105", "Technical Communication"]],
        2: [["IT201", "Database Systems"], ["IT202", "Data Structures"],
            ["IT203", "Computer Networks"], ["IT204", "Web Design"],
            ["IT205", "Statistics"]],
        "default": [["IT301", "Operating Systems"], ["IT302", "Software Testing"],
                    ["IT303", "Mobile Application Development"], ["IT304", "Information Security"],
                    ["IT305", "Minor Project"]],
    },
    "B.Tech Civil Engineering": {
        1: [["CE101", "Engineering Mechanics"], ["MA101", "Engineering Mathematics I"],
            ["PH101", "Engineering Physics"], ["CE102", "Civil Engineering Materials"],
            ["HU101", "Communication Skills"]],
        2: [["CE201", "Surveying"], ["CE202", "Strength of Materials"],
            ["CE203", "Fluid Mechanics"], ["MA201", "Engineering Mathematics II"],
            ["EVS201", "Environmental Studies"]],
        "default": [["CE301", "Structural Analysis"], ["CE302", "Geotechnical Engineering"],
                    ["CE303", "Transportation Engineering"], ["CE304", "Concrete Technology"],
                    ["CE305", "Water Resources Engineering"]],
    },
    "B.Tech Mechanical Engineering": {
        1: [["ME101", "Engineering Graphics"], ["MA101", "Engineering Mathematics I"],
            ["PH101", "Engineering Physics"], ["ME102", "Workshop Practice"],
            ["HU101", "Communication Skills"]],
        2: [["ME201", "Thermodynamics"], ["ME202", "Material Science"],
            ["ME203", "Fluid Mechanics"], ["MA201", "Engineering Mathematics II"],
            ["EVS201", "Environmental Studies"]],
        "default": [["ME301", "Machine Design"], ["ME302", "Manufacturing Processes"],
                    ["ME303", "Heat Transfer"], ["ME304", "Theory of Machines"],
                    ["ME305", "Industrial Engineering"]],
    },
    "B.Tech Electrical Engineering": {
        1: [["EE101", "Basic Electrical Engineering"], ["MA101", "Engineering Mathematics I"],
            ["PH101", "Engineering Physics"], ["EE102", "Electrical Workshop"],
            ["HU101", "Communication Skills"]],
        2: [["EE201", "Circuit Theory"], ["EE202", "Electrical Machines I"],
            ["EE203", "Digital Electronics"], ["MA201", "Engineering Mathematics II"],
            ["EVS201", "Environmental Studies"]],
        "default": [["EE301", "Power Systems"], ["EE302", "Control Systems"],
                    ["EE303", "Power Electronics"], ["EE304", "Measurements and Instrumentation"],
                    ["EE305", "Microprocessors"]],
    },
    "BBA": {
        1: [["BB101", "Principles of Management"], ["BB102", "Financial Accounting"],
            ["BB103", "Business Economics"], ["BB104", "Business Communication"],
            ["BB105", "Computer Applications"]],
        2: [["BB201", "Marketing Management"], ["BB202", "Cost Accounting"],
            ["BB203", "Business Law"], ["BB204", "Organizational Behaviour"],
            ["BB205", "Quantitative Techniques"]],
        "default": [["BB301", "Human Resource Management"], ["BB302", "Financial Management"],
                    ["BB303", "Operations Management"], ["BB304", "Consumer Behaviour"],
                    ["BB305", "Entrepreneurship Development"]],
    },
    "B.Com": {
        1: [["BC101", "Financial Accounting"], ["BC102", "Business Organization"],
            ["BC103", "Business Economics"], ["BC104", "Business Mathematics"],
            ["BC105", "Environmental Studies"]],
        2: [["BC201", "Corporate Accounting"], ["BC202", "Business Law"],
            ["BC203", "Cost Accounting"], ["BC204", "Income Tax Law"],
            ["BC205", "E-Commerce"]],
        "default": [["BC301", "Auditing"], ["BC302", "Management Accounting"],
                    ["BC303", "Company Law"], ["BC304", "Banking and Insurance"],
                    ["BC305", "Goods and Services Tax"]],
    },
    "BA English": {
        1: [["BAE101", "English Poetry"], ["BAE102", "English Prose"],
            ["BAE103", "History of English Literature"], ["BAE104", "Communication English"],
            ["BAE105", "Indian Writing in English"]],
        2: [["BAE201", "Drama"], ["BAE202", "Fiction"], ["BAE203", "Literary Criticism"],
            ["BAE204", "Linguistics"], ["BAE205", "Environmental Studies"]],
        "default": [["BAE301", "American Literature"], ["BAE302", "Postcolonial Literature"],
                    ["BAE303", "World Literature"], ["BAE304", "Creative Writing"],
                    ["BAE305", "Research Methodology"]],
    },
    "BA Psychology": {
        1: [["BAP101", "Introduction to Psychology"], ["BAP102", "Biological Psychology"],
            ["BAP103", "Social Psychology"], ["BAP104", "Communication Skills"],
            ["BAP105", "Environmental Studies"]],
        2: [["BAP201", "Developmental Psychology"], ["BAP202", "Cognitive Psychology"],
            ["BAP203", "Psychological Statistics"], ["BAP204", "Research Methods"],
            ["BAP205", "Counselling Basics"]],
        "default": [["BAP301", "Abnormal Psychology"], ["BAP302", "Personality Theories"],
                    ["BAP303", "Health Psychology"], ["BAP304", "Organizational Psychology"],
                    ["BAP305", "Practical Psychology"]],
    },
    "B.Sc Nursing": {
        1: [["NS101", "Anatomy"], ["NS102", "Physiology"], ["NS103", "Nursing Foundation"],
            ["NS104", "Nutrition"], ["NS105", "Psychology"]],
        2: [["NS201", "Microbiology"], ["NS202", "Pharmacology"],
            ["NS203", "Medical Surgical Nursing I"], ["NS204", "Community Health Nursing"],
            ["NS205", "Pathology"]],
        "default": [["NS301", "Medical Surgical Nursing II"], ["NS302", "Child Health Nursing"],
                    ["NS303", "Mental Health Nursing"], ["NS304", "Obstetrical Nursing"],
                    ["NS305", "Nursing Research"]],
    },
    "B.Pharm": {
        1: [["BP101", "Human Anatomy and Physiology"], ["BP102", "Pharmaceutical Analysis"],
            ["BP103", "Pharmaceutics"], ["BP104", "Pharmaceutical Inorganic Chemistry"],
            ["BP105", "Communication Skills"]],
        2: [["BP201", "Pharmaceutical Organic Chemistry"], ["BP202", "Biochemistry"],
            ["BP203", "Pathophysiology"], ["BP204", "Computer Applications in Pharmacy"],
            ["BP205", "Environmental Sciences"]],
        "default": [["BP301", "Pharmacology"], ["BP302", "Medicinal Chemistry"],
                    ["BP303", "Pharmacognosy"], ["BP304", "Pharmaceutical Microbiology"],
                    ["BP305", "Industrial Pharmacy"]],
    },
    "LLB": {
        1: [["LB101", "Legal Methods"], ["LB102", "Law of Contract I"],
            ["LB103", "Constitutional Law I"], ["LB104", "Law of Torts"],
            ["LB105", "Legal English"]],
        2: [["LB201", "Law of Contract II"], ["LB202", "Constitutional Law II"],
            ["LB203", "Family Law I"], ["LB204", "Criminal Law I"],
            ["LB205", "Jurisprudence"]],
        "default": [["LB301", "Property Law"], ["LB302", "Administrative Law"],
                    ["LB303", "Company Law"], ["LB304", "Labour Law"],
                    ["LB305", "Public International Law"]],
    },
    "B.Ed": {
        1: [["ED101", "Childhood and Growing Up"], ["ED102", "Contemporary India and Education"],
            ["ED103", "Learning and Teaching"], ["ED104", "Language Across Curriculum"],
            ["ED105", "ICT in Education"]],
        2: [["ED201", "Assessment for Learning"], ["ED202", "Pedagogy of School Subject I"],
            ["ED203", "Pedagogy of School Subject II"], ["ED204", "Inclusive Education"],
            ["ED205", "School Internship"]],
        "default": [["ED301", "Knowledge and Curriculum"], ["ED302", "Gender School and Society"],
                    ["ED303", "Educational Technology"], ["ED304", "Guidance and Counselling"],
                    ["ED305", "Action Research"]],
    },
    "MCA": {
        1: [["MCA101", "Advanced Programming"], ["MCA102", "Database Management Systems"],
            ["MCA103", "Computer Networks"], ["MCA104", "Discrete Mathematics"],
            ["MCA105", "Software Lab"]],
        2: [["MCA201", "Advanced Java"], ["MCA202", "Data Mining"],
            ["MCA203", "Operating Systems"], ["MCA204", "Web Technologies"],
            ["MCA205", "Cloud Computing"]],
        "default": [["MCA301", "Artificial Intelligence"], ["MCA302", "Machine Learning"],
                    ["MCA303", "Cyber Security"], ["MCA304", "Mobile Computing"],
                    ["MCA305", "Major Project"]],
    },
    "MBA": {
        1: [["MB101", "Management Process"], ["MB102", "Managerial Economics"],
            ["MB103", "Accounting for Managers"], ["MB104", "Business Statistics"],
            ["MB105", "Organizational Behaviour"]],
        2: [["MB201", "Marketing Management"], ["MB202", "Financial Management"],
            ["MB203", "Human Resource Management"], ["MB204", "Operations Research"],
            ["MB205", "Business Analytics"]],
        "default": [["MB301", "Strategic Management"], ["MB302", "International Business"],
                    ["MB303", "Supply Chain Management"], ["MB304", "Digital Marketing"],
                    ["MB305", "Project Management"]],
    },
    "M.Com": {
        1: [["MC101", "Advanced Accounting"], ["MC102", "Managerial Economics"],
            ["MC103", "Business Environment"], ["MC104", "Statistical Analysis"],
            ["MC105", "Corporate Law"]],
        2: [["MC201", "Financial Management"], ["MC202", "Cost Management"],
            ["MC203", "Tax Planning"], ["MC204", "Research Methodology"],
            ["MC205", "E-Commerce"]],
        "default": [["MC301", "International Accounting"], ["MC302", "Security Analysis"],
                    ["MC303", "Auditing Standards"], ["MC304", "Banking and Finance"],
                    ["MC305", "Dissertation"]],
    },
}

DEFAULT_MARKS = [[70, 56, 30, 25], [70, 50, 30, 24], [70, 47, 30, 23],
                 [70, 61, 30, 26], [70, 55, 30, 27]]

# ---- Theme colors (matched to the original design) ----
INK = "#172033"
MUTED = "#647086"
LINE = "#d9e0ea"
SURFACE = "#ffffff"
SOFT = "#f5f7fb"
BRAND = "#0f5a8f"
BRAND_DARK = "#083b61"
ACCENT = "#b8891f"
PASS_C = "#187a45"
FAIL_C = "#b3261e"
PAGE_BG = "#eef3f8"


# ----------------------------------------------------------------------
# 2. CORE LOGIC (identical rules to the original result sheet)
# ----------------------------------------------------------------------

def to_number(value):
    cleaned = re.sub(r"[^0-9.]", "", str(value))
    try:
        num = float(cleaned) if cleaned not in ("", ".") else 0
    except ValueError:
        num = 0
    return num or 0


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def course_status(ext_max, ext_obt, int_max, int_obt, tot_max, tot_obt):
    if (ext_obt >= ext_max * 0.4 and int_obt >= int_max * 0.4 and tot_obt >= tot_max * 0.4):
        return "Pass"
    return "Fail"


def grade_from_percentage(pct):
    if pct >= 85:
        return {"text": "A+ Pass (First Class with Distinction)", "pass": True}
    if pct >= 75:
        return {"text": "A Pass (First Class Division)", "pass": True}
    if pct >= 65:
        return {"text": "B+ Pass (Second Class Division)", "pass": True}
    if pct >= 55:
        return {"text": "B Pass (Third Class Division)", "pass": True}
    if pct >= 45:
        return {"text": "C (Pass with Credit)", "pass": True}
    return {"text": "Fail", "pass": False}


def next_semester_prediction(pct, failed_courses):
    if pct >= 75:
        adjustment = 2
    elif pct >= 60:
        adjustment = 1
    elif pct >= 45:
        adjustment = -2
    else:
        adjustment = -5
    predicted_pct = clamp(pct + adjustment - (failed_courses * 3), 0, 100)
    will_pass = predicted_pct >= 45 and failed_courses <= 1
    return {"predictedPct": predicted_pct, "willPass": will_pass}


def build_default_rows(programme, semester):
    course_set = PROGRAMME_COURSES.get(programme)
    if not course_set:
        return None
    courses = course_set.get(semester, course_set["default"])
    rows = []
    for index, (code, name) in enumerate(courses):
        ext_max, ext_obt, int_max, int_obt = DEFAULT_MARKS[index % len(DEFAULT_MARKS)]
        rows.append({
            "code": code, "name": name,
            "externalMax": ext_max, "externalObtained": ext_obt,
            "internalMax": int_max, "internalObtained": int_obt,
        })
    return rows


# ----------------------------------------------------------------------
# 3. GUI APPLICATION
# ----------------------------------------------------------------------

class ReportCardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalinga University - Student Report Card")
        self.geometry("1180x860")
        self.configure(bg=PAGE_BG)
        self.minsize(1000, 700)

        self.mark_vars = []      # list of dicts: {ext_var, int_var, code,...}
        self.rows_static = []    # code/name/max marks for current selection
        self.chart_canvas = None

        self._build_scrollable_container()
        self._build_header()
        self._build_selection_bar()
        self._build_student_line()
        self._build_table_section()
        self._build_summary_section()
        self._build_prediction_section()
        self._build_chart_section()

        # Initial load matching the original page defaults
        self.programme_var.set("B.Tech Computer Science")
        self.semester_var.set("2")
        self.student_name_var.set("Aarav Sharma")
        self.enrollment_var.set("KU2024001")
        self.render_courses()

    # ---------------- scrollable page ----------------
    def _build_scrollable_container(self):
        outer = tk.Frame(self, bg=PAGE_BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg=PAGE_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.sheet = tk.Frame(self.canvas, bg=SURFACE, highlightbackground=LINE,
                               highlightthickness=1)
        self.sheet_window = self.canvas.create_window((0, 0), window=self.sheet, anchor="n")

        self.sheet.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

    def _on_canvas_resize(self, event):
        width = min(event.width - 20, 1200)
        self.canvas.coords(self.sheet_window, event.width / 2, 0)
        self.canvas.itemconfig(self.sheet_window, width=max(width, 900))

    # ---------------- header with official university logo ----------------
    def _build_header(self):
        header = tk.Frame(self.sheet, bg=BRAND_DARK)
        header.pack(fill="x")
        inner = tk.Frame(header, bg=BRAND_DARK)
        inner.pack(pady=16)

        logo_holder = tk.Frame(inner, bg="#ffffff", padx=10, pady=10)
        logo_holder.pack()
        self._load_logo(logo_holder)

        tk.Label(inner, text="Student Semester Result / Report Card", font=("Segoe UI", 13),
                 bg=BRAND_DARK, fg="#dce7f2").pack(pady=(6, 0))

        band = tk.Frame(header, bg=ACCENT, height=4)
        band.pack(fill="x")

    def _load_logo(self, holder):
        """Loads the official Kalinga University logo (assets/kalinga_university_logo.png,
        or a copy placed next to this script)."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(script_dir, "assets", "kalinga_university_logo.png"),
            os.path.join(script_dir, "kalinga_university_logo.png"),
            os.path.join(script_dir, "kalinga_university_logo.jpg"),
        ]
        for path in candidates:
            if PIL_AVAILABLE and os.path.exists(path):
                try:
                    img = Image.open(path)
                    target_h = 140
                    ratio = target_h / img.height
                    img = img.resize((int(img.width * ratio), target_h))
                    photo = ImageTk.PhotoImage(img)
                    lbl = tk.Label(holder, image=photo, bg="#ffffff")
                    lbl.image = photo  # keep reference so it isn't garbage-collected
                    lbl.pack()
                    return
                except Exception:
                    pass
        # Fallback: no logo file found - show the university name as text only.
        tk.Label(holder, text="KALINGA UNIVERSITY", font=("Segoe UI", 24, "bold"),
                 bg="#ffffff", fg=BRAND_DARK).pack()

    # ---------------- programme / semester selectors ----------------
    def _build_selection_bar(self):
        bar = tk.Frame(self.sheet, bg=SOFT, pady=16, padx=20)
        bar.pack(fill="x")
        for c in range(5):
            bar.columnconfigure(c, weight=1)

        # Student Name
        tk.Label(bar, text="STUDENT NAME", font=("Segoe UI", 9, "bold"),
                 bg=SOFT, fg=MUTED).grid(row=0, column=0, sticky="w", padx=6)
        self.student_name_var = tk.StringVar()
        tk.Entry(bar, textvariable=self.student_name_var, font=("Segoe UI", 11)
                 ).grid(row=1, column=0, sticky="ew", padx=6, pady=(2, 0))

        # Enrollment Number
        tk.Label(bar, text="ENROLLMENT NUMBER", font=("Segoe UI", 9, "bold"),
                 bg=SOFT, fg=MUTED).grid(row=0, column=1, sticky="w", padx=6)
        self.enrollment_var = tk.StringVar()
        tk.Entry(bar, textvariable=self.enrollment_var, font=("Segoe UI", 11)
                 ).grid(row=1, column=1, sticky="ew", padx=6, pady=(2, 0))

        # Programme / Department dropdown
        tk.Label(bar, text="PROGRAMME / DEPARTMENT", font=("Segoe UI", 9, "bold"),
                 bg=SOFT, fg=MUTED).grid(row=0, column=2, sticky="w", padx=6)
        self.programme_var = tk.StringVar()
        programme_box = ttk.Combobox(bar, textvariable=self.programme_var,
                                      values=list(PROGRAMME_COURSES.keys()),
                                      state="readonly", font=("Segoe UI", 11))
        programme_box.grid(row=1, column=2, sticky="ew", padx=6, pady=(2, 0))
        programme_box.bind("<<ComboboxSelected>>", lambda e: self.render_courses())

        # Semester dropdown
        tk.Label(bar, text="SEMESTER", font=("Segoe UI", 9, "bold"),
                 bg=SOFT, fg=MUTED).grid(row=0, column=3, sticky="w", padx=6)
        self.semester_var = tk.StringVar()
        semester_box = ttk.Combobox(bar, textvariable=self.semester_var,
                                     values=[str(i) for i in range(1, 9)],
                                     state="readonly", font=("Segoe UI", 11))
        semester_box.grid(row=1, column=3, sticky="ew", padx=6, pady=(2, 0))
        semester_box.bind("<<ComboboxSelected>>", lambda e: self.render_courses())

        # Show Result button
        show_btn = tk.Button(bar, text="Show Result", font=("Segoe UI", 11, "bold"),
                              bg=BRAND, fg="white", relief="flat", padx=16, pady=8,
                              activebackground=BRAND_DARK, activeforeground="white",
                              command=self.calculate_result)
        show_btn.grid(row=1, column=4, sticky="ew", padx=6, pady=(2, 0))

    # ---------------- student info line ----------------
    def _build_student_line(self):
        line = tk.Frame(self.sheet, bg=SURFACE, padx=20, pady=14)
        line.pack(fill="x")
        for c in range(4):
            line.columnconfigure(c, weight=1)

        self.info_name = self._info_box(line, "STUDENT NAME", 0)
        self.info_enroll = self._info_box(line, "ENROLLMENT NUMBER", 1)
        self.info_programme = self._info_box(line, "PROGRAMME", 2)
        self.info_semester = self._info_box(line, "SEMESTER", 3)

    def _info_box(self, parent, label, col):
        box = tk.Frame(parent, bg=SURFACE, highlightbackground=LINE, highlightthickness=1)
        box.grid(row=0, column=col, sticky="ew", padx=6)
        tk.Label(box, text=label, font=("Segoe UI", 8, "bold"), bg=SURFACE,
                 fg=MUTED, anchor="w").pack(fill="x", padx=10, pady=(8, 0))
        value = tk.Label(box, text="-", font=("Segoe UI", 13, "bold"), bg=SURFACE,
                          fg=INK, anchor="w")
        value.pack(fill="x", padx=10, pady=(0, 8))
        return value

    # ---------------- marks table ----------------
    def _build_table_section(self):
        wrap = tk.Frame(self.sheet, bg=SURFACE, padx=20, pady=6)
        wrap.pack(fill="x")

        tk.Label(wrap, text="Edit the 'Obtained' marks below, then click Show Result "
                            "to recalculate the result, prediction, and chart.",
                 font=("Segoe UI", 9, "italic"), bg=SURFACE, fg=MUTED
                 ).pack(anchor="w", pady=(0, 8))

        self.table_frame = tk.Frame(wrap, bg=SURFACE, highlightbackground=LINE,
                                     highlightthickness=1)
        self.table_frame.pack(fill="x")

        headers = ["Code", "Course Name", "Ext. Max", "Ext. Obt.", "Int. Max",
                   "Int. Obt.", "Tot. Max", "Tot. Obt.", "Result"]
        widths = [8, 30, 8, 8, 8, 8, 8, 8, 10]
        for c, (h, w) in enumerate(zip(headers, widths)):
            tk.Label(self.table_frame, text=h, font=("Segoe UI", 9, "bold"), bg="#e9eef5",
                     fg="#344054", width=w, borderwidth=1, relief="solid"
                     ).grid(row=0, column=c, sticky="nsew")

        self.body_start_row = 1  # rows will be inserted starting here

    # ---------------- summary ----------------
    def _build_summary_section(self):
        wrap = tk.Frame(self.sheet, bg=SURFACE, padx=20, pady=14)
        wrap.pack(fill="x")
        for c in range(4):
            wrap.columnconfigure(c, weight=1)

        self.sum_total_max = self._summary_box(wrap, "TOTAL MAX MARKS", 0)
        self.sum_total_obt = self._summary_box(wrap, "TOTAL MARKS OBTAINED", 1)
        self.sum_percentage = self._summary_box(wrap, "PERCENTAGE", 2)
        self.sum_result = self._summary_box(wrap, "OVERALL RESULT", 3, badge=True)

    def _summary_box(self, parent, label, col, badge=False):
        box = tk.Frame(parent, bg=SOFT, highlightbackground=LINE, highlightthickness=1)
        box.grid(row=0, column=col, sticky="ew", padx=6)
        tk.Label(box, text=label, font=("Segoe UI", 8, "bold"), bg=SOFT,
                 fg=MUTED, anchor="w").pack(fill="x", padx=10, pady=(8, 0))
        if badge:
            value = tk.Label(box, text="-", font=("Segoe UI", 11, "bold"), bg=PASS_C,
                              fg="white", anchor="center", padx=8, pady=4)
            value.pack(padx=10, pady=(4, 10), anchor="w")
        else:
            value = tk.Label(box, text="-", font=("Segoe UI", 15, "bold"), bg=SOFT,
                              fg=INK, anchor="w")
            value.pack(fill="x", padx=10, pady=(0, 10))
        return value

    # ---------------- prediction ----------------
    def _build_prediction_section(self):
        wrap = tk.Frame(self.sheet, bg=SURFACE, padx=20, pady=6)
        wrap.pack(fill="x")
        box = tk.Frame(wrap, bg=SURFACE, highlightbackground=LINE, highlightthickness=1)
        box.pack(fill="x")
        tk.Label(box, text="Next Semester Prediction", font=("Segoe UI", 13, "bold"),
                 bg=SURFACE, fg=BRAND).pack(anchor="w", padx=14, pady=(10, 4))
        self.prediction_label = tk.Label(box, text="-", font=("Segoe UI", 12, "bold"),
                                          bg=SURFACE, fg=INK, anchor="w", justify="left")
        self.prediction_label.pack(anchor="w", padx=14)
        self.prediction_basis = tk.Label(box, text="-", font=("Segoe UI", 9), bg=SURFACE,
                                          fg=MUTED, anchor="w", justify="left", wraplength=1000)
        self.prediction_basis.pack(anchor="w", padx=14, pady=(2, 12))

    # ---------------- chart ----------------
    def _build_chart_section(self):
        wrap = tk.Frame(self.sheet, bg=SURFACE, padx=20, pady=10)
        wrap.pack(fill="x")
        tk.Label(wrap, text="Course-wise Performance & Prediction Chart",
                 font=("Segoe UI", 13, "bold"), bg=SURFACE, fg=BRAND
                 ).pack(anchor="w", pady=(0, 8))
        self.chart_holder = tk.Frame(wrap, bg=SURFACE, height=340)
        self.chart_holder.pack(fill="x")

        footer = tk.Label(self.sheet, text="This report card is generated for academic "
                           "reference. Marks can be edited above for what-if analysis.",
                           font=("Segoe UI", 8), bg=SURFACE, fg=MUTED)
        footer.pack(anchor="w", padx=20, pady=(0, 18))

    # ------------------------------------------------------------------
    # LOGIC / RENDERING
    # ------------------------------------------------------------------
    def render_courses(self):
        """Loads the subject list for the selected Programme + Semester,
        populates editable rows with default marks (mirrors renderCourses())."""
        programme = self.programme_var.get()
        semester = int(self.semester_var.get()) if self.semester_var.get() else 2

        rows = build_default_rows(programme, semester)
        if rows is None:
            messagebox.showerror("Invalid Selection", "Please select a valid programme.")
            return

        # Clear old row widgets (keep header row 0)
        for widget in self.table_frame.grid_slaves():
            info = widget.grid_info()
            if int(info["row"]) >= self.body_start_row:
                widget.destroy()

        self.mark_vars = []
        for r, row in enumerate(rows, start=self.body_start_row):
            bg = "#fafbfd" if (r % 2 == 0) else SURFACE

            tk.Label(self.table_frame, text=row["code"], bg=bg, fg=INK, width=8,
                     borderwidth=1, relief="solid").grid(row=r, column=0, sticky="nsew")
            tk.Label(self.table_frame, text=row["name"], bg=bg, fg=INK, width=30,
                     anchor="w", borderwidth=1, relief="solid"
                     ).grid(row=r, column=1, sticky="nsew")
            tk.Label(self.table_frame, text=str(row["externalMax"]), bg=bg, fg=INK, width=8,
                     borderwidth=1, relief="solid").grid(row=r, column=2, sticky="nsew")

            ext_var = tk.StringVar(value=str(row["externalObtained"]))
            tk.Entry(self.table_frame, textvariable=ext_var, width=8, justify="center"
                     ).grid(row=r, column=3, sticky="nsew")

            tk.Label(self.table_frame, text=str(row["internalMax"]), bg=bg, fg=INK, width=8,
                     borderwidth=1, relief="solid").grid(row=r, column=4, sticky="nsew")

            int_var = tk.StringVar(value=str(row["internalObtained"]))
            tk.Entry(self.table_frame, textvariable=int_var, width=8, justify="center"
                     ).grid(row=r, column=5, sticky="nsew")

            tot_max_lbl = tk.Label(self.table_frame, text="-", bg=bg, fg=INK, width=8,
                                    borderwidth=1, relief="solid")
            tot_max_lbl.grid(row=r, column=6, sticky="nsew")
            tot_obt_lbl = tk.Label(self.table_frame, text="-", bg=bg, fg=INK, width=8,
                                    borderwidth=1, relief="solid")
            tot_obt_lbl.grid(row=r, column=7, sticky="nsew")
            status_lbl = tk.Label(self.table_frame, text="-", bg=bg, fg="white", width=10,
                                   borderwidth=1, relief="solid")
            status_lbl.grid(row=r, column=8, sticky="nsew")

            self.mark_vars.append({
                "code": row["code"], "name": row["name"],
                "externalMax": row["externalMax"], "internalMax": row["internalMax"],
                "ext_var": ext_var, "int_var": int_var,
                "tot_max_lbl": tot_max_lbl, "tot_obt_lbl": tot_obt_lbl,
                "status_lbl": status_lbl,
            })

        self.info_programme.config(text=programme)
        self.info_semester.config(text=f"Semester {semester}")
        self.calculate_result()

    def calculate_result(self):
        """Mirrors recalcFromTable(): recompute totals, grade, prediction, chart."""
        name = self.student_name_var.get().strip() or "Student"
        enrollment = self.enrollment_var.get().strip() or "Enrollment Number"
        self.info_name.config(text=name)
        self.info_enroll.config(text=enrollment)

        computed = []
        total_max = 0
        total_obt = 0
        failed_courses = 0

        for row in self.mark_vars:
            ext_max = to_number(row["externalMax"])
            int_max = to_number(row["internalMax"])
            ext_obt = to_number(row["ext_var"].get())
            int_obt = to_number(row["int_var"].get())
            tot_max = ext_max + int_max
            tot_obt = ext_obt + int_obt
            status = course_status(ext_max, ext_obt, int_max, int_obt, tot_max, tot_obt)

            row["tot_max_lbl"].config(text=f"{tot_max:.0f}")
            row["tot_obt_lbl"].config(text=f"{tot_obt:.0f}")
            row["status_lbl"].config(text=status, bg=(PASS_C if status == "Pass" else FAIL_C))

            total_max += tot_max
            total_obt += tot_obt
            if status == "Fail":
                failed_courses += 1

            computed.append({
                "code": row["code"], "status": status,
                "percentage": (tot_obt / tot_max * 100) if tot_max else 0,
            })

        pct = (total_obt / total_max * 100) if total_max else 0
        grade = grade_from_percentage(pct)
        prediction = next_semester_prediction(pct, failed_courses)

        self.sum_total_max.config(text=f"{total_max:.0f}")
        self.sum_total_obt.config(text=f"{total_obt:.0f}")
        self.sum_percentage.config(text=f"{pct:.2f}%")
        self.sum_result.config(text=grade["text"],
                                bg=(PASS_C if grade["pass"] else FAIL_C))

        outcome = "Likely Pass" if prediction["willPass"] else "Likely Fail"
        self.prediction_label.config(
            text=f"{outcome} next semester, predicted at {prediction['predictedPct']:.2f}%.")
        self.prediction_basis.config(
            text=f"Based on current percentage, {failed_courses} failed course(s), "
                 f"and the edited marks shown in the table.")

        self.draw_chart(computed, pct, prediction["predictedPct"])

    def draw_chart(self, rows, current_pct, predicted_pct):
        for widget in self.chart_holder.winfo_children():
            widget.destroy()

        labels = [r["code"] for r in rows] + ["Current", "Next"]
        values = [r["percentage"] for r in rows] + [current_pct, predicted_pct]
        colors = [BRAND if r["status"] == "Pass" else FAIL_C for r in rows]
        colors.append(PASS_C)
        colors.append(ACCENT if predicted_pct >= 45 else FAIL_C)

        fig, ax = plt.subplots(figsize=(10.5, 3.6), dpi=100)
        bars = ax.bar(labels, values, color=colors, width=0.55)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                    f"{value:.1f}%", ha="center", fontsize=8)
        ax.axhline(45, color=FAIL_C, linestyle="--", linewidth=1)
        ax.text(-0.4, 47, "Pass line 45%", color=FAIL_C, fontsize=8)
        ax.set_ylim(0, 110)
        ax.set_ylabel("Percentage")
        ax.grid(axis="y", linestyle="-", alpha=0.25)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)


if __name__ == "__main__":
    app = ReportCardApp()
    app.mainloop()
