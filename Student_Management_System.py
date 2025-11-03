"""
Advanced Smart Student Management System with Subject-wise Marks
Author: Muhammad Zarq Ali (Multi-Subject Enhanced Version)
Features:
- Individual marks for 5 subjects (English, Urdu, Science, Maths, Computer)
- Auto-calculation of total marks, percentage, and grade
- Professional Tkinter UI with subject entry fields
- Enhanced analytics with subject-wise performance
- Treeview for records with sorting
- File-based persistence
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

FILENAME = "students_subjects.txt"
SUBJECTS = ["English", "Urdu", "Science", "Maths", "Computer"]
MAX_MARKS_PER_SUBJECT = 100
TOTAL_MAX_MARKS = MAX_MARKS_PER_SUBJECT * len(SUBJECTS)

# ========================= UTILITY & VALIDATION =========================

def ensure_file():
    """Create file if not exists"""
    if not os.path.exists(FILENAME):
        open(FILENAME, "w").close()

def load_students():
    """Return list of student records as dicts"""
    ensure_file()
    students = []
    with open(FILENAME, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 11:  # id, name, age, 5 subjects, total, percentage, grade
                continue
            sid, name, age, eng, urd, sci, mat, comp, total, perc, grade = parts
            students.append({
                "id": sid, 
                "name": name, 
                "age": age,
                "english": eng,
                "urdu": urd,
                "science": sci,
                "maths": mat,
                "computer": comp,
                "total": total,
                "percentage": perc,
                "grade": grade
            })
    return students

def save_students(list_of_dicts):
    """Overwrite students file from list of dicts"""
    with open(FILENAME, "w") as f:
        for s in list_of_dicts:
            f.write(f"{s['id']},{s['name']},{s['age']},{s['english']},{s['urdu']},"
                   f"{s['science']},{s['maths']},{s['computer']},{s['total']},"
                   f"{s['percentage']},{s['grade']}\n")

def is_duplicate_id(sid):
    """Check if student ID already exists"""
    students = load_students()
    return any(s["id"] == sid for s in students)

def calculate_total_and_grade(marks_dict):
    """
    Calculate total, percentage and grade from subject marks
    marks_dict: {"english": "85", "urdu": "90", ...}
    Returns: (total, percentage, grade)
    """
    total = sum(int(marks_dict[subj.lower()]) for subj in SUBJECTS)
    percentage = (total / TOTAL_MAX_MARKS) * 100
    
    # Grade calculation based on percentage
    if percentage >= 90: grade = "A+"
    elif percentage >= 80: grade = "A"
    elif percentage >= 70: grade = "B"
    elif percentage >= 60: grade = "C"
    elif percentage >= 50: grade = "D"
    else: grade = "F"
    
    return total, round(percentage, 2), grade

def validate_inputs(sid, name, age, marks_dict, check_unique=True):
    """
    Validate form inputs
    marks_dict: {"english": "85", "urdu": "90", ...}
    """
    # ID validation
    if not sid.strip():
        return False, "❌ ID cannot be empty."
    if not sid.isdigit():
        return False, "❌ ID must be numeric."
    if check_unique and is_duplicate_id(sid):
        return False, "❌ ID already exists. Choose another."
    
    # Name validation
    if not name.strip():
        return False, "❌ Name cannot be empty."
    if name.isdigit():
        return False, "❌ Name cannot be numeric only."
    if not name.replace(" ", "").isalpha():
        return False, "❌ Name must contain only letters and spaces."
    
    # Age validation
    if not age.strip():
        return False, "❌ Age cannot be empty."
    if not age.isdigit():
        return False, "❌ Age must be numeric."
    age_int = int(age)
    if age_int <= 0:
        return False, "❌ Age must be greater than 0."
    if age_int > 99:
        return False, "❌ Age must be reasonable (1-99)."
    
    # Subject marks validation
    for subj in SUBJECTS:
        mark = marks_dict.get(subj.lower(), "").strip()
        if not mark:
            return False, f"❌ {subj} marks cannot be empty."
        if not mark.isdigit():
            return False, f"❌ {subj} marks must be numeric."
        mark_int = int(mark)
        if mark_int < 0 or mark_int > MAX_MARKS_PER_SUBJECT:
            return False, f"❌ {subj} marks must be between 0 and {MAX_MARKS_PER_SUBJECT}."
    
    return True, ""

# ========================= CORE LOGIC FUNCTIONS =========================

def add_student_record(sid, name, age, marks_dict):
    """Add new student record"""
    ok, msg = validate_inputs(sid, name, age, marks_dict, check_unique=True)
    if not ok:
        return False, msg
    
    total, percentage, grade = calculate_total_and_grade(marks_dict)
    
    with open(FILENAME, "a") as f:
        f.write(f"{sid},{name},{age},{marks_dict['english']},{marks_dict['urdu']},"
               f"{marks_dict['science']},{marks_dict['maths']},{marks_dict['computer']},"
               f"{total},{percentage},{grade}\n")
    
    return True, f"✅ Student '{name}' added with grade {grade} ({percentage}%)."

def update_student_record(sid, name, age, marks_dict):
    """Update existing student record"""
    ok, msg = validate_inputs(sid, name, age, marks_dict, check_unique=False)
    if not ok:
        return False, msg
    
    students = load_students()
    found = False
    for s in students:
        if s["id"] == sid:
            total, percentage, grade = calculate_total_and_grade(marks_dict)
            s["name"] = name
            s["age"] = age
            s["english"] = marks_dict["english"]
            s["urdu"] = marks_dict["urdu"]
            s["science"] = marks_dict["science"]
            s["maths"] = marks_dict["maths"]
            s["computer"] = marks_dict["computer"]
            s["total"] = str(total)
            s["percentage"] = str(percentage)
            s["grade"] = grade
            found = True
            break
    
    if not found:
        return False, "❌ ID not found."
    
    save_students(students)
    return True, f"✅ Record updated. New grade: {grade} ({percentage}%)"

def delete_student_record(sid):
    """Delete student record"""
    students = load_students()
    new = [s for s in students if s["id"] != sid]
    deleted = len(new) != len(students)
    if deleted:
        save_students(new)
    return deleted

def analyze_students():
    """Analyze student data and return comprehensive statistics"""
    students = load_students()
    if not students:
        return None
    
    totals = [int(s["total"]) for s in students]
    percentages = [float(s["percentage"]) for s in students]
    
    avg_total = sum(totals) / len(totals)
    avg_percentage = sum(percentages) / len(percentages)
    high_total = max(totals)
    low_total = min(totals)
    
    # Top performers
    top = [s for s in students if int(s["total"]) == high_total]
    
    # Subject-wise averages
    subject_avgs = {}
    for subj in SUBJECTS:
        subj_marks = [int(s[subj.lower()]) for s in students]
        subject_avgs[subj] = sum(subj_marks) / len(subj_marks)
    
    # Grade distribution
    grades = {}
    for s in students:
        grades[s["grade"]] = grades.get(s["grade"], 0) + 1
    
    # Pass/Fail (50% and above)
    passed = len([p for p in percentages if p >= 50])
    pass_rate = (passed / len(students)) * 100
    
    return {
        "total_students": len(students),
        "avg_total": avg_total,
        "avg_percentage": avg_percentage,
        "high_total": high_total,
        "low_total": low_total,
        "top": top,
        "subject_avgs": subject_avgs,
        "grades": grades,
        "students": students,
        "passed": passed,
        "pass_rate": pass_rate,
        "percentages": percentages
    }

# ========================= GUI APPLICATION =========================

class SmartSMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Student Management System - Multi-Subject Version by Muhammad Zarq Ali")
        self.geometry("1200x700")
        self.configure(bg="#f4f6f9")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self._create_widgets()
        self.refresh_treeview()

    def _create_widgets(self):
        # ============= HEADER =============
        header = tk.Frame(self, bg="#2b2d42", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, 
                text="🎓 Smart Student Management System - Multi-Subject", 
                bg="#2b2d42",
                fg="white", 
                font=("Helvetica", 18, "bold")).pack(pady=5)
        
        tk.Label(header,
                text="Subject-wise Marks • Auto Total & Grade • Advanced Analytics",
                bg="#2b2d42",
                fg="#8d99ae",
                font=("Helvetica", 10)).pack()

        # ============= LEFT PANEL: FORM =============
        left = tk.Frame(self, bg="#ffffff", padx=15, pady=15)
        left.pack(side="left", fill="y")

        # Scrollable form
        canvas = tk.Canvas(left, bg="#ffffff", width=280, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form title
        form_title = tk.Label(scrollable_frame, 
                             text="📝 Student Form", 
                             font=("Helvetica", 14, "bold"), 
                             bg="#ffffff",
                             fg="#2b2d42")
        form_title.grid(row=0, column=0, columnspan=2, pady=(0,15))

        # Basic info fields
        row = 1
        basic_fields = [
            ("ID:", "e_id"),
            ("Name:", "e_name"),
            ("Age:", "e_age")
        ]
        
        for label, attr in basic_fields:
            tk.Label(scrollable_frame, text=label, bg="#ffffff", 
                    font=("Helvetica", 10, "bold")).grid(
                row=row, column=0, sticky="e", pady=6, padx=(0,8))
            entry = tk.Entry(scrollable_frame, width=20, font=("Helvetica", 10))
            entry.grid(row=row, column=1, pady=6)
            setattr(self, attr, entry)
            row += 1

        # Subject marks section
        sep1 = ttk.Separator(scrollable_frame, orient="horizontal")
        sep1.grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)
        row += 1

        tk.Label(scrollable_frame, text="📚 Subject Marks (out of 100)", 
                bg="#ffffff", font=("Helvetica", 11, "bold"),
                fg="#2b2d42").grid(row=row, column=0, columnspan=2, pady=(0,10))
        row += 1

        # Subject entry fields
        self.subject_entries = {}
        for subj in SUBJECTS:
            tk.Label(scrollable_frame, text=f"{subj}:", bg="#ffffff", 
                    font=("Helvetica", 10)).grid(
                row=row, column=0, sticky="e", pady=5, padx=(0,8))
            entry = tk.Entry(scrollable_frame, width=20, font=("Helvetica", 10))
            entry.grid(row=row, column=1, pady=5)
            entry.bind('<KeyRelease>', self.preview_results)
            self.subject_entries[subj.lower()] = entry
            row += 1

        # Results preview
        sep2 = ttk.Separator(scrollable_frame, orient="horizontal")
        sep2.grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)
        row += 1

        tk.Label(scrollable_frame, text="📊 Preview Results", 
                bg="#ffffff", font=("Helvetica", 11, "bold"),
                fg="#2b2d42").grid(row=row, column=0, columnspan=2, pady=(0,8))
        row += 1

        preview_fields = [
            ("Total:", "lbl_total"),
            ("Percentage:", "lbl_percentage"),
            ("Grade:", "lbl_grade")
        ]

        for label, attr in preview_fields:
            tk.Label(scrollable_frame, text=label, bg="#ffffff", 
                    font=("Helvetica", 10)).grid(
                row=row, column=0, sticky="e", pady=4, padx=(0,8))
            lbl = tk.Label(scrollable_frame, text="—", bg="#ffffff", 
                          font=("Helvetica", 10, "bold"), fg="#8338ec")
            lbl.grid(row=row, column=1, sticky="w", pady=4)
            setattr(self, attr, lbl)
            row += 1

        # Buttons
        sep3 = ttk.Separator(scrollable_frame, orient="horizontal")
        sep3.grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)
        row += 1

        buttons = [
            ("➕ Add Student", self.on_add, "#2b2d42"),
            ("✏️ Update Record", self.on_update, "#e76f51"),
            ("🗑️ Delete Record", self.on_delete, "#f94144"),
            ("🔄 Clear Form", self.clear_form, "#9a8c98"),
        ]

        for text, cmd, color in buttons:
            btn = tk.Button(scrollable_frame, text=text, width=24, bg=color, fg="white",
                          font=("Helvetica", 10, "bold"),
                          command=cmd, cursor="hand2")
            btn.grid(row=row, column=0, columnspan=2, pady=4)
            row += 1

        # Search section
        sep4 = ttk.Separator(scrollable_frame, orient="horizontal")
        sep4.grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)
        row += 1

        tk.Label(scrollable_frame, text="🔍 Search:", bg="#ffffff", 
                font=("Helvetica", 10)).grid(row=row, column=0, sticky="e", pady=4)
        self.e_search = tk.Entry(scrollable_frame, width=20, font=("Helvetica", 10))
        self.e_search.grid(row=row, column=1, pady=4)
        row += 1

        btn_search = tk.Button(scrollable_frame, text="Search", width=24, bg="#4cc9f0",
                              font=("Helvetica", 10, "bold"),
                              command=self.on_search, cursor="hand2")
        btn_search.grid(row=row, column=0, columnspan=2, pady=4)
        row += 1

        btn_refresh = tk.Button(scrollable_frame, text="🔄 Refresh All", width=24, bg="#06d6a0",
                               font=("Helvetica", 10, "bold"),
                               command=self.refresh_treeview, cursor="hand2")
        btn_refresh.grid(row=row, column=0, columnspan=2, pady=4)
        row += 1

        # Analytics & Export
        sep5 = ttk.Separator(scrollable_frame, orient="horizontal")
        sep5.grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)
        row += 1

        btn_analyze = tk.Button(scrollable_frame, text="📊 Analyze Data", width=24, 
                               bg="#8338ec", fg="white",
                               font=("Helvetica", 11, "bold"),
                               command=self.show_analysis_window, cursor="hand2")
        btn_analyze.grid(row=row, column=0, columnspan=2, pady=4)
        row += 1

        btn_export = tk.Button(scrollable_frame, text="💾 Export to CSV", width=24,
                              bg="#577590", fg="white",
                              font=("Helvetica", 10, "bold"),
                              command=self.export_to_csv, cursor="hand2")
        btn_export.grid(row=row, column=0, columnspan=2, pady=4)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ============= RIGHT PANEL: TREEVIEW =============
        right = tk.Frame(self, bg="#ffffff", padx=10, pady=10)
        right.pack(side="left", fill="both", expand=True)

        tree_title = tk.Label(right, text="📋 Student Records", 
                             font=("Helvetica", 14, "bold"),
                             bg="#ffffff", fg="#2b2d42")
        tree_title.pack(pady=(0,10))

        # Treeview with scrollbar
        tree_frame = tk.Frame(right)
        tree_frame.pack(fill="both", expand=True)

        cols = ("id", "name", "age", "english", "urdu", "science", "maths", 
                "computer", "total", "percentage", "grade")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=25)
        
        # Configure columns
        col_config = {
            "id": ("ID", 60),
            "name": ("Name", 120),
            "age": ("Age", 50),
            "english": ("Eng", 60),
            "urdu": ("Urd", 60),
            "science": ("Sci", 60),
            "maths": ("Math", 60),
            "computer": ("Comp", 60),
            "total": ("Total", 70),
            "percentage": ("Perc%", 70),
            "grade": ("Grade", 60)
        }
        
        for c in cols:
            heading, width = col_config[c]
            self.tree.heading(c, text=heading, command=lambda _c=c: self.sort_by(_c))
            self.tree.column(c, anchor="center", width=width)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="left", fill="y")

        # ============= BOTTOM STATUS BAR =============
        self.status = tk.Label(self, text=f"Ready | Total: 0 students | Max Marks: {TOTAL_MAX_MARKS}", 
                              anchor="w", bg="#2b2d42", fg="white",
                              font=("Helvetica", 10), padx=10)
        self.status.pack(side="bottom", fill="x")

    # ========================= UI HELPER METHODS =========================

    def preview_results(self, event=None):
        """Preview total, percentage, and grade as user types"""
        try:
            marks_dict = {}
            all_valid = True
            
            for subj in SUBJECTS:
                mark = self.subject_entries[subj.lower()].get().strip()
                if not mark or not mark.isdigit():
                    all_valid = False
                    break
                mark_int = int(mark)
                if mark_int < 0 or mark_int > MAX_MARKS_PER_SUBJECT:
                    all_valid = False
                    break
                marks_dict[subj.lower()] = mark
            
            if all_valid:
                total, percentage, grade = calculate_total_and_grade(marks_dict)
                self.lbl_total.config(text=f"{total}/{TOTAL_MAX_MARKS}")
                self.lbl_percentage.config(text=f"{percentage}%")
                self.lbl_grade.config(text=grade)
            else:
                self.lbl_total.config(text="—")
                self.lbl_percentage.config(text="—")
                self.lbl_grade.config(text="—")
        except:
            self.lbl_total.config(text="—")
            self.lbl_percentage.config(text="—")
            self.lbl_grade.config(text="—")

    def clear_form(self):
        """Clear all form fields"""
        self.e_id.delete(0, tk.END)
        self.e_name.delete(0, tk.END)
        self.e_age.delete(0, tk.END)
        
        for entry in self.subject_entries.values():
            entry.delete(0, tk.END)
        
        self.lbl_total.config(text="—")
        self.lbl_percentage.config(text="—")
        self.lbl_grade.config(text="—")
        self.status.config(text="Form cleared.")

    def refresh_treeview(self):
        """Refresh treeview with all records"""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        students = load_students()
        for s in students:
            self.tree.insert("", "end", values=(
                s["id"], s["name"], s["age"], s["english"], s["urdu"],
                s["science"], s["maths"], s["computer"], s["total"],
                f"{s['percentage']}%", s["grade"]))
        
        self.status.config(text=f"Loaded {len(students)} records | Max Marks: {TOTAL_MAX_MARKS}")

    def sort_by(self, col):
        """Sort treeview by column"""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        try:
            items.sort(key=lambda t: float(t[0].replace('%', '')))
        except ValueError:
            items.sort()
        
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

    def on_tree_select(self, event):
        """Load selected record into form"""
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        
        self.e_id.delete(0, tk.END)
        self.e_id.insert(0, values[0])
        self.e_name.delete(0, tk.END)
        self.e_name.insert(0, values[1])
        self.e_age.delete(0, tk.END)
        self.e_age.insert(0, values[2])
        
        # Load subject marks
        for i, subj in enumerate(SUBJECTS):
            self.subject_entries[subj.lower()].delete(0, tk.END)
            self.subject_entries[subj.lower()].insert(0, values[3+i])
        
        # Update preview
        self.lbl_total.config(text=f"{values[8]}/{TOTAL_MAX_MARKS}")
        self.lbl_percentage.config(text=values[9])
        self.lbl_grade.config(text=values[10])
        
        self.status.config(text=f"Record {values[0]} loaded into form.")

    # ========================= BUTTON CALLBACKS =========================

    def on_add(self):
        """Add new student"""
        sid = self.e_id.get().strip()
        name = self.e_name.get().strip()
        age = self.e_age.get().strip()
        
        marks_dict = {subj.lower(): self.subject_entries[subj.lower()].get().strip() 
                     for subj in SUBJECTS}
        
        success, msg = add_student_record(sid, name, age, marks_dict)
        
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_treeview()
            self.clear_form()
        else:
            messagebox.showerror("Validation Error", msg)

    def on_update(self):
        """Update existing student"""
        sid = self.e_id.get().strip()
        if not sid:
            messagebox.showwarning("Input Required", 
                                 "Please select a record or enter ID to update.")
            return
        
        name = self.e_name.get().strip()
        age = self.e_age.get().strip()
        marks_dict = {subj.lower(): self.subject_entries[subj.lower()].get().strip() 
                     for subj in SUBJECTS}
        
        success, msg = update_student_record(sid, name, age, marks_dict)
        
        if success:
            messagebox.showinfo("Updated", msg)
            self.refresh_treeview()
        else:
            messagebox.showerror("Error", msg)

    def on_delete(self):
        """Delete student record"""
        sid = self.e_id.get().strip()
        if not sid:
            messagebox.showwarning("Input Required", 
                                 "Please select a record or enter ID to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete student ID {sid}?")
        if not confirm:
            return
        
        deleted = delete_student_record(sid)
        if deleted:
            messagebox.showinfo("Deleted", "✅ Record deleted successfully.")
            self.refresh_treeview()
            self.clear_form()
        else:
            messagebox.showerror("Error", "❌ ID not found.")

    def on_search(self):
        """Search for students"""
        key = self.e_search.get().strip().lower()
        if not key:
            messagebox.showwarning("Input Required", "Enter ID or Name to search.")
            return
        
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        students = load_students()
        results = [s for s in students 
                  if key in s["id"].lower() or key in s["name"].lower()]
        
        for s in results:
            self.tree.insert("", "end", values=(
                s["id"], s["name"], s["age"], s["english"], s["urdu"],
                s["science"], s["maths"], s["computer"], s["total"],
                f"{s['percentage']}%", s["grade"]))
        
        self.status.config(text=f"Search: {len(results)} records found.")

    def export_to_csv(self):
        """Export data to CSV file"""
        students = load_students()
        if not students:
            messagebox.showwarning("No Data", "No records to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("ID,Name,Age,English,Urdu,Science,Maths,Computer,Total,Percentage,Grade\n")
                    for s in students:
                        f.write(f"{s['id']},{s['name']},{s['age']},{s['english']},{s['urdu']},"
                               f"{s['science']},{s['maths']},{s['computer']},{s['total']},"
                               f"{s['percentage']},{s['grade']}\n")
                messagebox.showinfo("Success", f"✅ Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Export failed: {e}")

    # ========================= ANALYSIS WINDOW =========================

    def show_analysis_window(self):
        """Show comprehensive data analysis with subject-wise breakdown"""
        data = analyze_students()
        if not data:
            messagebox.showwarning("No Data", "No records to analyze.")
            return

        w = tk.Toplevel(self)
        w.title("📊 Comprehensive Data Analysis")
        w.geometry("1000x700")
        w.configure(bg="#f4f6f9")

        title = tk.Label(w, text="📊 Student Performance Analysis", 
                        font=("Helvetica", 16, "bold"),
                        bg="#2b2d42", fg="white", pady=12)
        title.pack(fill="x")

        # Create notebook for tabs
        notebook = ttk.Notebook(w)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # TAB 1: Overall Statistics
        tab1 = tk.Frame(notebook, bg="#ffffff")
        notebook.add(tab1, text="📈 Overall Stats")

        summary_text = f"""
📈 OVERALL STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Students: {data['total_students']}
• Average Total Marks: {data['avg_total']:.2f}/{TOTAL_MAX_MARKS}
• Average Percentage: {data['avg_percentage']:.2f}%
• Highest Total: {data['high_total']}/{TOTAL_MAX_MARKS}
• Lowest Total: {data['low_total']}/{TOTAL_MAX_MARKS}
• Pass Rate: {data['pass_rate']:.1f}% ({data['passed']}/{data['total_students']})

🏆 TOP PERFORMER(S):
"""
        for t in data["top"]:
            summary_text += f"   • {t['name']} (ID: {t['id']}) - {t['total']}/{TOTAL_MAX_MARKS} ({t['percentage']}%)\n"

        summary_text += f"""

📚 SUBJECT-WISE AVERAGE MARKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for subj in SUBJECTS:
            avg = data['subject_avgs'][subj]
            perc = (avg / MAX_MARKS_PER_SUBJECT) * 100
            summary_text += f"   • {subj:12s}: {avg:.2f}/{MAX_MARKS_PER_SUBJECT} ({perc:.1f}%)\n"

        txt = tk.Text(tab1, wrap="word", font=("Courier", 10),
                     bg="#f8f9fa", relief="flat", padx=15, pady=15)
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("end", summary_text)
        txt.config(state="disabled")

        # TAB 2: Charts
        tab2 = tk.Frame(notebook, bg="#ffffff")
        notebook.add(tab2, text="📊 Visual Charts")

        # Create figure with multiple subplots
        fig = Figure(figsize=(10, 8), dpi=100)
        
        # Chart 1: Grade distribution (Pie)
        ax1 = fig.add_subplot(221)
        grades = data["grades"]
        labels = list(grades.keys())
        sizes = [grades[k] for k in labels]
        colors = ['#2b2d42', '#8d99ae', '#06d6a0', '#ffd60a', '#ef233c', '#d90429']
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.set_title("Grade Distribution", fontweight='bold', fontsize=12)

        # Chart 2: Top 5 students (Bar)
        ax2 = fig.add_subplot(222)
        sorted_students = sorted(data['students'], 
                                key=lambda s: int(s['total']), reverse=True)[:5]
        names = [s['name'][:10] for s in sorted_students]
        totals = [int(s['total']) for s in sorted_students]
        bars = ax2.bar(names, totals, color='#8338ec')
        ax2.set_title("Top 5 Students (Total Marks)", fontweight='bold', fontsize=12)
        ax2.set_ylabel("Total Marks")
        ax2.set_ylim(0, TOTAL_MAX_MARKS)
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')

        # Chart 3: Subject-wise average (Bar)
        ax3 = fig.add_subplot(223)
        subjects = list(data['subject_avgs'].keys())
        avgs = [data['subject_avgs'][s] for s in subjects]
        bars3 = ax3.bar(subjects, avgs, color='#4cc9f0')
        ax3.set_title("Subject-wise Average Marks", fontweight='bold', fontsize=12)
        ax3.set_ylabel("Average Marks")
        ax3.set_ylim(0, MAX_MARKS_PER_SUBJECT)
        ax3.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='Pass Mark')
        
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=9)

        # Chart 4: Percentage distribution (Histogram)
        ax4 = fig.add_subplot(224)
        percentages = data['percentages']
        ax4.hist(percentages, bins=10, color='#06d6a0', edgecolor='black', alpha=0.7)
        ax4.set_title("Percentage Distribution", fontweight='bold', fontsize=12)
        ax4.set_xlabel("Percentage")
        ax4.set_ylabel("Number of Students")
        ax4.axvline(x=50, color='r', linestyle='--', alpha=0.7, label='Pass Line')
        ax4.legend()

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=tab2)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        canvas.draw()

        # TAB 3: Detailed Subject Analysis
        tab3 = tk.Frame(notebook, bg="#ffffff")
        notebook.add(tab3, text="📚 Subject Details")

        detail_frame = tk.Frame(tab3, bg="#ffffff", padx=15, pady=15)
        detail_frame.pack(fill="both", expand=True)

        detail_text = "📚 DETAILED SUBJECT-WISE ANALYSIS\n"
        detail_text += "=" * 70 + "\n\n"

        for subj in SUBJECTS:
            subj_marks = [int(s[subj.lower()]) for s in data['students']]
            avg = sum(subj_marks) / len(subj_marks)
            highest = max(subj_marks)
            lowest = min(subj_marks)
            passed = len([m for m in subj_marks if m >= 50])
            pass_rate = (passed / len(subj_marks)) * 100
            
            # Find top scorers
            top_scorers = [s for s in data['students'] if int(s[subj.lower()]) == highest]
            
            detail_text += f"📖 {subj.upper()}\n"
            detail_text += f"   Average: {avg:.2f}/{MAX_MARKS_PER_SUBJECT} ({(avg/MAX_MARKS_PER_SUBJECT)*100:.1f}%)\n"
            detail_text += f"   Highest: {highest}/{MAX_MARKS_PER_SUBJECT}\n"
            detail_text += f"   Lowest: {lowest}/{MAX_MARKS_PER_SUBJECT}\n"
            detail_text += f"   Pass Rate: {pass_rate:.1f}% ({passed}/{len(subj_marks)})\n"
            detail_text += f"   Top Scorer(s): "
            detail_text += ", ".join([f"{t['name']} ({t[subj.lower()]})" for t in top_scorers[:3]])
            detail_text += "\n\n"

        txt_detail = tk.Text(detail_frame, wrap="word", font=("Courier", 10),
                            bg="#f8f9fa", relief="flat")
        txt_detail.pack(fill="both", expand=True)
        txt_detail.insert("end", detail_text)
        txt_detail.config(state="disabled")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(detail_frame, command=txt_detail.yview)
        txt_detail.configure(yscrollcommand=scrollbar.set)

# ========================= MAIN ENTRY POINT =========================

def main():
    """Launch the application"""
    ensure_file()
    app = SmartSMSApp()
    app.mainloop()

if __name__ == "__main__":
    main()