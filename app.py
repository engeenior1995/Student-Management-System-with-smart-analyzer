"""
Smart Student Management System - Streamlit Version
Original Tkinter author: Muhammad Zarq Ali
Same logic: 5 subjects, auto total/percentage/grade, CRUD, analytics.
Single file. No extra requirements (pandas ships with Streamlit).
"""

import os
import streamlit as st
import pandas as pd

FILENAME = "students_subjects.txt"
SUBJECTS = ["English", "Urdu", "Science", "Maths", "Computer"]
MAX_MARKS_PER_SUBJECT = 100
TOTAL_MAX_MARKS = MAX_MARKS_PER_SUBJECT * len(SUBJECTS)

# ========================= UTILITY & VALIDATION (same as original) =========================

def ensure_file():
    if not os.path.exists(FILENAME):
        open(FILENAME, "w").close()

def load_students():
    ensure_file()
    students = []
    with open(FILENAME, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 11:
                continue
            sid, name, age, eng, urd, sci, mat, comp, total, perc, grade = parts
            students.append({
                "id": sid, "name": name, "age": age,
                "english": eng, "urdu": urd, "science": sci,
                "maths": mat, "computer": comp,
                "total": total, "percentage": perc, "grade": grade,
            })
    return students

def save_students(list_of_dicts):
    with open(FILENAME, "w") as f:
        for s in list_of_dicts:
            f.write(f"{s['id']},{s['name']},{s['age']},{s['english']},{s['urdu']},"
                    f"{s['science']},{s['maths']},{s['computer']},{s['total']},"
                    f"{s['percentage']},{s['grade']}\n")

def is_duplicate_id(sid):
    return any(s["id"] == sid for s in load_students())

def calculate_total_and_grade(marks_dict):
    total = sum(int(marks_dict[subj.lower()]) for subj in SUBJECTS)
    percentage = (total / TOTAL_MAX_MARKS) * 100
    if percentage >= 90: grade = "A+"
    elif percentage >= 80: grade = "A"
    elif percentage >= 70: grade = "B"
    elif percentage >= 60: grade = "C"
    elif percentage >= 50: grade = "D"
    else: grade = "F"
    return total, round(percentage, 2), grade

def validate_inputs(sid, name, age, marks_dict, check_unique=True):
    if not sid.strip():
        return False, "❌ ID cannot be empty."
    if not sid.isdigit():
        return False, "❌ ID must be numeric."
    if check_unique and is_duplicate_id(sid):
        return False, "❌ ID already exists. Choose another."

    if not name.strip():
        return False, "❌ Name cannot be empty."
    if name.isdigit():
        return False, "❌ Name cannot be numeric only."
    if not name.replace(" ", "").isalpha():
        return False, "❌ Name must contain only letters and spaces."

    if not age.strip():
        return False, "❌ Age cannot be empty."
    if not age.isdigit():
        return False, "❌ Age must be numeric."
    age_int = int(age)
    if age_int <= 0:
        return False, "❌ Age must be greater than 0."
    if age_int > 99:
        return False, "❌ Age must be reasonable (1-99)."

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

# ========================= CORE LOGIC (same as original) =========================

def add_student_record(sid, name, age, marks_dict):
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
    students = load_students()
    new = [s for s in students if s["id"] != sid]
    deleted = len(new) != len(students)
    if deleted:
        save_students(new)
    return deleted

def analyze_students():
    students = load_students()
    if not students:
        return None
    totals = [int(s["total"]) for s in students]
    percentages = [float(s["percentage"]) for s in students]
    high_total = max(totals)
    top = [s for s in students if int(s["total"]) == high_total]

    subject_avgs = {}
    for subj in SUBJECTS:
        marks = [int(s[subj.lower()]) for s in students]
        subject_avgs[subj] = sum(marks) / len(marks)

    grades = {}
    for s in students:
        grades[s["grade"]] = grades.get(s["grade"], 0) + 1

    passed = len([p for p in percentages if p >= 50])
    return {
        "total_students": len(students),
        "avg_total": sum(totals) / len(totals),
        "avg_percentage": sum(percentages) / len(percentages),
        "high_total": high_total,
        "low_total": min(totals),
        "top": top,
        "subject_avgs": subject_avgs,
        "grades": grades,
        "students": students,
        "passed": passed,
        "pass_rate": (passed / len(students)) * 100,
        "percentages": percentages,
    }

# ========================= UI HELPERS =========================

def students_df(students):
    rows = []
    for s in students:
        rows.append({
            "ID": int(s["id"]), "Name": s["name"], "Age": int(s["age"]),
            "Eng": int(s["english"]), "Urd": int(s["urdu"]), "Sci": int(s["science"]),
            "Math": int(s["maths"]), "Comp": int(s["computer"]),
            "Total": int(s["total"]), "Perc %": float(s["percentage"]), "Grade": s["grade"],
        })
    return pd.DataFrame(rows)

def marks_from_state(prefix):
    return {s.lower(): str(int(st.session_state[f"{prefix}_{s}"])) for s in SUBJECTS}

def marks_inputs(prefix):
    cols = st.columns(len(SUBJECTS))
    for col, subj in zip(cols, SUBJECTS):
        with col:
            st.number_input(subj, min_value=0, max_value=MAX_MARKS_PER_SUBJECT,
                            step=1, key=f"{prefix}_{subj}")

def preview(prefix):
    total, perc, grade = calculate_total_and_grade(marks_from_state(prefix))
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", f"{total}/{TOTAL_MAX_MARKS}")
    c2.metric("Percentage", f"{perc}%")
    c3.metric("Grade", grade)

# ---- callbacks ----

def add_cb():
    ok, msg = add_student_record(
        st.session_state["add_id"].strip(),
        st.session_state["add_name"].strip(),
        st.session_state["add_age"].strip(),
        marks_from_state("add"),
    )
    st.session_state["flash"] = (ok, msg)
    if ok:
        st.session_state["add_id"] = ""
        st.session_state["add_name"] = ""
        st.session_state["add_age"] = ""
        for s in SUBJECTS:
            st.session_state[f"add_{s}"] = 0

def update_cb():
    ok, msg = update_student_record(
        st.session_state["sel_id"],
        st.session_state["upd_name"].strip(),
        st.session_state["upd_age"].strip(),
        marks_from_state("upd"),
    )
    st.session_state["flash"] = (ok, msg)

def delete_cb():
    if not st.session_state.get("del_confirm"):
        st.session_state["flash"] = (False, "⚠️ Tick the confirm box first.")
        return
    sid = st.session_state["sel_id"]
    if delete_student_record(sid):
        st.session_state["flash"] = (True, "✅ Record deleted successfully.")
        st.session_state.pop("sel_id", None)
        st.session_state.pop("loaded_id", None)
        st.session_state["del_confirm"] = False
    else:
        st.session_state["flash"] = (False, "❌ ID not found.")

# ========================= APP =========================

st.set_page_config(page_title="Smart Student Management System", page_icon="🎓", layout="wide")

# widget defaults
defaults = {"add_id": "", "add_name": "", "add_age": "", "upd_name": "", "upd_age": "",
            "del_confirm": False}
for s in SUBJECTS:
    defaults[f"add_{s}"] = 0
    defaults[f"upd_{s}"] = 0
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

st.title("🎓 Smart Student Management System")
st.caption("Subject-wise Marks • Auto Total & Grade • Advanced Analytics")

flash = st.session_state.pop("flash", None)
if flash:
    (st.success if flash[0] else st.error)(flash[1])

tab_add, tab_edit, tab_records, tab_analytics = st.tabs(
    ["➕ Add Student", "✏️ Update / 🗑️ Delete", "📋 Records", "📊 Analytics"])

# ---------- ADD ----------
with tab_add:
    c1, c2, c3 = st.columns(3)
    c1.text_input("ID", key="add_id")
    c2.text_input("Name", key="add_name")
    c3.text_input("Age", key="add_age")
    st.markdown(f"**📚 Subject Marks (out of {MAX_MARKS_PER_SUBJECT})**")
    marks_inputs("add")
    preview("add")
    st.button("➕ Add Student", on_click=add_cb, type="primary")

# ---------- UPDATE / DELETE ----------
with tab_edit:
    students = load_students()
    if not students:
        st.info("No records yet. Add a student first.")
    else:
        by_id = {s["id"]: s for s in students}
        sel = st.selectbox("Select student", list(by_id.keys()), key="sel_id",
                           format_func=lambda i: f"{i} - {by_id[i]['name']}")
        if st.session_state.get("loaded_id") != sel:
            s = by_id[sel]
            st.session_state["upd_name"] = s["name"]
            st.session_state["upd_age"] = s["age"]
            for subj in SUBJECTS:
                st.session_state[f"upd_{subj}"] = int(s[subj.lower()])
            st.session_state["loaded_id"] = sel

        c1, c2 = st.columns(2)
        c1.text_input("Name", key="upd_name")
        c2.text_input("Age", key="upd_age")
        marks_inputs("upd")
        preview("upd")

        b1, b2 = st.columns(2)
        with b1:
            st.button("✏️ Update Record", on_click=update_cb, type="primary")
        with b2:
            st.checkbox("Confirm delete", key="del_confirm")
            st.button("🗑️ Delete Record", on_click=delete_cb)

# ---------- RECORDS ----------
with tab_records:
    students = load_students()
    key = st.text_input("🔍 Search by ID or Name").strip().lower()
    shown = [s for s in students if key in s["id"].lower() or key in s["name"].lower()] if key else students
    if shown:
        df = students_df(shown)
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={"Perc %": st.column_config.NumberColumn(format="%.2f%%")})
        st.caption(f"{len(shown)} record(s) | Max Marks: {TOTAL_MAX_MARKS} | Click a column header to sort")
        st.download_button("💾 Export to CSV", df.to_csv(index=False).encode("utf-8"),
                           file_name="students.csv", mime="text/csv")
    else:
        st.info("No records found.")

# ---------- ANALYTICS ----------
with tab_analytics:
    data = analyze_students()
    if not data:
        st.info("No records to analyze.")
    else:
        m = st.columns(5)
        m[0].metric("Students", data["total_students"])
        m[1].metric("Avg Percentage", f"{data['avg_percentage']:.2f}%")
        m[2].metric("Highest Total", f"{data['high_total']}/{TOTAL_MAX_MARKS}")
        m[3].metric("Lowest Total", f"{data['low_total']}/{TOTAL_MAX_MARKS}")
        m[4].metric("Pass Rate", f"{data['pass_rate']:.1f}%", f"{data['passed']}/{data['total_students']}", delta_color="off")

        st.subheader("🏆 Top Performer(s)")
        for t in data["top"]:
            st.success(f"{t['name']} (ID: {t['id']}) - {t['total']}/{TOTAL_MAX_MARKS} ({t['percentage']}%)")

        ca, cb = st.columns(2)
        with ca:
            st.markdown("**Grade Distribution**")
            order = ["A+", "A", "B", "C", "D", "F"]
            gdf = pd.DataFrame({"Students": [data["grades"].get(g, 0) for g in order]}, index=order)
            st.bar_chart(gdf)
        with cb:
            st.markdown("**Top 5 Students (Total Marks)**")
            top5 = sorted(data["students"], key=lambda s: int(s["total"]), reverse=True)[:5]
            tdf = pd.DataFrame({"Total": [int(s["total"]) for s in top5]},
                               index=[f"{s['name']} ({s['id']})" for s in top5])
            st.bar_chart(tdf)

        cc, cd = st.columns(2)
        with cc:
            st.markdown("**Subject-wise Average Marks**")
            sdf = pd.DataFrame({"Average": [data["subject_avgs"][s] for s in SUBJECTS]}, index=SUBJECTS)
            st.bar_chart(sdf)
        with cd:
            st.markdown("**Percentage Distribution**")
            bins = [0] * 10
            for p in data["percentages"]:
                bins[min(int(p // 10), 9)] += 1
            hdf = pd.DataFrame({"Students": bins}, index=[f"{i}-{i + 10}" for i in range(0, 100, 10)])
            st.bar_chart(hdf)

        st.subheader("📚 Subject Details")
        for subj in SUBJECTS:
            marks = [int(s[subj.lower()]) for s in data["students"]]
            avg = sum(marks) / len(marks)
            highest, lowest = max(marks), min(marks)
            passed = len([x for x in marks if x >= 50])
            top_scorers = [s for s in data["students"] if int(s[subj.lower()]) == highest]
            with st.expander(f"📖 {subj.upper()} — Avg {avg:.2f}/{MAX_MARKS_PER_SUBJECT}"):
                st.write(f"**Average:** {avg:.2f}/{MAX_MARKS_PER_SUBJECT} ({avg / MAX_MARKS_PER_SUBJECT * 100:.1f}%)")
                st.write(f"**Highest:** {highest} | **Lowest:** {lowest}")
                st.write(f"**Pass Rate:** {passed / len(marks) * 100:.1f}% ({passed}/{len(marks)})")
                st.write("**Top Scorer(s):** " + ", ".join(f"{t['name']} ({t[subj.lower()]})" for t in top_scorers[:3]))

st.divider()
st.caption("⚠️ Free hosting resets files on restart. Use Records → Export to CSV to back up your data.")
