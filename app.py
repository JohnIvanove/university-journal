
#*Імпорт бібліотек.
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import crud_sqlite as db
#Назва вікна.
APP_TITLE = "DB SQLite Tkinter"
#Бд за замовчуванням.
DEFAULT_DB = "app.db"

#* ---------- Вибір бд ----------.
#Деф вибору вибраної бази даних.
def choose_db_open():
    path = filedialog.askopenfilename (
        title="Open database",
        filetypes = [("SQLite DB", "*.db"), ("All files", "*.*")]
    )
    if path:
        set_db_and_reload (path)
#Деф вибору ново-створеної бази даних.
def choose_db_new():
    path = filedialog.asksaveasfilename (
        title = "Create new database",
        defaultextension = ".db",
        filetypes = [("SQLite DB", "*.db")]
    )
    if path:
        set_db_and_reload (path, new = True)
#Деф отримання/оновлення показу даних з підключеної бази даних.
def set_db_and_reload (path: str, new: bool = False):
    db.set_db_path (path)
    if new or not os.path.exists (path):
        db.init_db()
    db_label_var.set (f"DB: {path}")
    refresh_all()
#Деф чи введено число.
def ensure_int (s: str) -> bool:
    return s.isdigit()

#* ---------- UI оновлення студентів ----------.
#Деф оновлення показу студентів.
def refresh_students():
    course_filter = course_filter_var.get()
    tree_students.delete (*tree_students.get_children())
    data = []
    if course_filter and course_filter != "All":
        cid = int (course_filter.split (":", 1) [0])
        data = db.list_students_by_course (cid)
    else:
        data = db.list_students()
    for row in data:
        tree_students.insert ("", tk.END, iid = row ["id"], values = (row ["id"], row ["name"], row ["age"], row ["major"]))
    update_student_fields_from_selection()
#Деф показу вибраного студента.
def on_student_select (_event = None):
    update_student_fields_from_selection()
    refresh_student_enrollments()
#Деф оновлення показу фільтрів вибраного студента
def update_student_fields_from_selection():
    sel = tree_students.selection()
    if not sel:
        entry_name_var.set(""); entry_age_var.set(""); entry_major_var.set("")
        return
    sid = int (sel [0])
    s = db.get_student (sid)
    if not s:
        return
    entry_name_var.set (s ["name"] or "")
    entry_age_var.set (str (s ["age"]) if s ["age"] is not None else "")
    entry_major_var.set (s ["major"] or "")
#Деф показу ново-доданого студента.
def add_student():
    name = entry_name_var.get().strip()
    age = entry_age_var.get().strip()
    major = entry_major_var.get().strip() or None
    if not name or not ensure_int (age):
        messagebox.showerror ("Помилка", "Вкажи коректні ім'я та вік.")
        return
    db.create_student (name, int (age), major)
    refresh_students()
    clear_student_fields()
#Деф оновлення показу студента.
def update_student():
    sel = tree_students.selection()
    if not sel:
        messagebox.showinfo ("Увага", "Оберіть студента зі списку.")
        return
    sid = int (sel [0])
    name = entry_name_var.get().strip()
    age = entry_age_var.get().strip()
    major = entry_major_var.get().strip() or None
    if not name or not ensure_int (age):
        messagebox.showerror ("Помилка", "Вкажи коректні ім'я та вік.")
        return
    db.update_student (sid, name = name, age = int (age), major = major)
    refresh_students()
#Деф показу видалення студента.
def delete_student():
    sel = tree_students.selection()
    if not sel:
        return
    sid = int (sel [0])
    if messagebox.askyesno ("Підтвердження", "Видалити студента та його реєстрації?"):
        db.delete_student (sid)
        refresh_students()
        list_student_courses.delete (0, tk.END)
#Деф очищення полів для студента.
def clear_student_fields():
    entry_name_var.set(""); entry_age_var.set(""); entry_major_var.set("")

#* ---------- UI оновлення курсів ----------.
#Деф оновлення показу курсів.
def refresh_courses():
    tree_courses.delete (*tree_courses.get_children())
    for row in db.list_courses():
        tree_courses.insert ("", tk.END, iid = row ["course_id"], values = (row ["course_id"], row ["course_name"], row ["instructor"]))
    refresh_course_filter()
    update_course_fields_from_selection()
#Деф показу вибраного курсу.
def on_course_select (_event = None):
    update_course_fields_from_selection()
    refresh_students()
#Деф отримання показу курсів для оновлення.
def update_course_fields_from_selection():
    sel = tree_courses.selection()
    if not sel:
        entry_cname_var.set(""); entry_instr_var.set("")
        return
    cid = int (sel [0])
    c = db.get_course (cid)
    if not c:
        return
    entry_cname_var.set (c ["course_name"] or "")
    entry_instr_var.set (c ["instructor"] or "")
#Деф показу доданого курсу.
def add_course():
    cname = entry_cname_var.get().strip()
    instr = entry_instr_var.get().strip() or None
    if not cname:
        messagebox.showerror ("Помилка", "Назва курсу обов'язкова.")
        return
    db.create_course (cname, instr)
    refresh_courses()
    clear_course_fields()
#Деф оновлення показу курса.
def update_course():
    sel = tree_courses.selection()
    if not sel:
        messagebox.showinfo ("Увага", "Оберіть курс зі списку.")
        return
    cid = int (sel [0])
    cname = entry_cname_var.get().strip()
    instr = entry_instr_var.get().strip() or None
    if not cname:
        messagebox.showerror ("Помилка", "Назва курсу обов'язкова.")
        return
    db.update_course (cid, course_name = cname, instructor = instr)
    refresh_courses()
#Деф показу видалення курсу.
def delete_course():
    sel = tree_courses.selection()
    if not sel:
        return
    cid = int (sel [0])
    if messagebox.askyesno ("Підтвердження", "Видалити курс та всі пов'язані реєстрації?"):
        db.delete_course (cid)
        refresh_courses()
        refresh_students()
#Деф очищення полів курсу.
def clear_course_fields():
    entry_cname_var.set(""); entry_instr_var.set("")

#* ---------- Звязки ----------.
#Деф оновлення звязку студента
def refresh_student_enrollments():
    list_student_courses.delete (0, tk.END)
    sel = tree_students.selection()
    if not sel:
        return
    sid = int (sel [0])
    for c in db.list_courses_by_student (sid):
        list_student_courses.insert (tk.END, f"{c ['course_id']}: {c ['course_name']} ({c ['instructor'] or '—'})")
#Деф створення звязку студента.
def enroll_selected_student_to_course():
    sel_s = tree_students.selection()
    if not sel_s:
        messagebox.showinfo ("Увага", "Оберіть студента.")
        return
    sid = int (sel_s [0])

    course_choice = combo_enroll_course.get()
    if not course_choice:
        messagebox.showinfo ("Увага", "Оберіть курс для реєстрації.")
        return
    cid = int (course_choice.split (":", 1) [0])

    if not db.enroll_student (sid, cid):
        messagebox.showwarning ("Попередження", "Реєстрація вже існує або дані некоректні.")
    refresh_student_enrollments()
    refresh_students()
#Деф видалення звязку студента з курсом.
def unenroll_selected():
    sel_s = tree_students.selection()
    if not sel_s:
        return
    sid = int (sel_s [0])
    sel_idx = list_student_courses.curselection()
    if not sel_idx:
        return
    item = list_student_courses.get (sel_idx [0])
    cid = int (item.split (":", 1) [0])
    db.unenroll_student (sid, cid)
    refresh_student_enrollments()
    refresh_students()

#* ---------- Filters ----------
def refresh_course_filter():
    combo_values = ["All"] + [f"{c ['course_id']}: {c ['course_name']}" for c in db.list_courses()]
    course_filter_combo ["values"] = combo_values
    if "All" not in combo_values:
        course_filter_var.set ("All")
    else:
        cur = course_filter_var.get()
        if cur not in combo_values:
            course_filter_var.set ("All")
#Деф оновлення зміни фільтрів.
def on_course_filter_change (_event = None):
    refresh_students()
#Деф 
def reload_enroll_courses_combo():
    combo_enroll_course ["values"] = [f"{c ['course_id']}: {c ['course_name']}" for c in db.list_courses()]

#* ---------- Зіпуск UI ----------
#Базові налаштування.
root = tk.Tk()
root.title (APP_TITLE)
root.geometry ("1100x650")
root.minsize (900, 520)

#Меню.
menubar = tk.Menu (root)
dbmenu = tk.Menu (menubar, tearoff = False)
dbmenu.add_command (label = "Open…", command = choose_db_open)
dbmenu.add_command (label = "New…", command = choose_db_new)
menubar.add_cascade (label = "Database", menu = dbmenu)
root.config (menu = menubar)

#Верхня панель бази даних.
topbar = ttk.Frame (root, padding = (8, 6))
topbar.grid (row = 0, column = 0, sticky = "ew")
root.columnconfigure (0, weight = 1)
db_label_var = tk.StringVar (value = f"DB: {DEFAULT_DB}")
ttk.Label (topbar, textvariable = db_label_var).pack (side = "left")

ttk.Separator (topbar, orient = "vertical").pack (side = "left", fill = "y", padx = 8)
ttk.Label (topbar, text = "Filter by course:").pack (side = "left", padx = (0, 6))
course_filter_var = tk.StringVar (value="All")
course_filter_combo = ttk.Combobox (topbar, textvariable = course_filter_var, width = 32, state = "readonly")
course_filter_combo.pack (side = "left")
course_filter_combo.bind ("<<ComboboxSelected>>", on_course_filter_change)

#Головна сторінка.
panes = ttk.PanedWindow (root, orient = tk.HORIZONTAL)
panes.grid (row = 1, column = 0, sticky = "nsew", padx = 8, pady = 8)
root.rowconfigure (1, weight = 1)

#Встановлення студентів з ліва.
frame_students = ttk.Frame (panes, padding = 6)
panes.add (frame_students, weight = 3)

cols_s = ("ID", "Name", "Age", "Major")
tree_students = ttk.Treeview (frame_students, columns = cols_s, show = "headings", selectmode = "browse")
for c, w in zip (cols_s, (60, 220, 80, 220)):
    tree_students.heading (c, text = c)
    tree_students.column (c, width = w, anchor = "w")
tree_students.grid (row = 0, column = 0, columnspan = 4, sticky = "nsew")
frame_students.rowconfigure (0, weight = 1)
frame_students.columnconfigure (0, weight = 1)

tree_students.bind ("<<TreeviewSelect>>", on_student_select)

#Форма для студентів.
entry_name_var = tk.StringVar()
entry_age_var = tk.StringVar()
entry_major_var = tk.StringVar()

ttk.Label (frame_students, text = "Name").grid (row = 1, column = 0, sticky = "e", pady = (8,2))
ttk.Entry (frame_students, textvariable = entry_name_var).grid (row = 1, column = 1, sticky = "ew", pady = (8,2))
ttk.Label (frame_students, text = "Age").grid (row = 2, column = 0, sticky = "e")
ttk.Entry (frame_students, textvariable = entry_age_var).grid (row = 2, column = 1, sticky = "ew")
ttk.Label (frame_students, text = "Major").grid (row = 3, column = 0, sticky = "e")
ttk.Entry (frame_students, textvariable = entry_major_var).grid (row = 3, column = 1, sticky = "ew")

frame_students.columnconfigure (1, weight = 1)

ttk.Button (frame_students, text = "Add", command = add_student).grid (row = 1, column = 2, padx = 6, sticky = "ew")
ttk.Button (frame_students, text = "Update", command = update_student).grid (row = 2, column = 2, padx = 6, sticky = "ew")
ttk.Button (frame_students, text = "Delete", command = delete_student).grid (row = 3, column = 2, padx = 6, sticky = "ew")
ttk.Button (frame_students, text = "Clear", command = clear_student_fields).grid (row = 3, column = 3, padx = 6, sticky = "ew")

#Звязок для студентів.
enroll_box = ttk.Labelframe (frame_students, text = "Enrollments", padding = 6)
enroll_box.grid (row = 4, column = 0, columnspan = 4, sticky = "nsew", pady = (10,0))
frame_students.rowconfigure (4, weight = 1)

list_student_courses = tk.Listbox (enroll_box, height = 6)
list_student_courses.grid (row = 0, column = 0, columnspan = 3, sticky = "nsew")
enroll_box.rowconfigure (0, weight = 1); enroll_box.columnconfigure (0, weight = 1)

ttk.Button (enroll_box, text = "Unenroll selected", command = unenroll_selected).grid (row = 1, column = 0, sticky = "w", pady = (6,0))
ttk.Label (enroll_box, text = "Enroll to:").grid (row = 1, column = 1, sticky = "e", pady = (6,0))
combo_enroll_course = ttk.Combobox (enroll_box, state = "readonly", width = 32)
combo_enroll_course.grid (row = 1, column = 2, sticky = "ew", pady = (6,0))
ttk.Button (enroll_box, text = "Enroll", command = enroll_selected_student_to_course).grid (row = 1, column = 3, sticky = "ew", padx = (6,0), pady = (6,0))

#Встановлення курсів з права.
frame_courses = ttk.Frame (panes, padding = 6)
panes.add (frame_courses, weight = 2)

cols_c = ("ID", "Course", "Instructor")
tree_courses = ttk.Treeview (frame_courses, columns = cols_c, show = "headings", selectmode = "browse")
for c, w in zip (cols_c, (60, 260, 200)):
    tree_courses.heading (c, text = c)
    tree_courses.column (c, width = w, anchor = "w")
tree_courses.grid (row = 0, column = 0, columnspan = 3, sticky = "nsew")
frame_courses.rowconfigure (0, weight = 1); frame_courses.columnconfigure (1, weight = 1)

tree_courses.bind ("<<TreeviewSelect>>", on_course_select)

entry_cname_var = tk.StringVar()
entry_instr_var = tk.StringVar()

ttk.Label (frame_courses, text = "Course").grid (row = 1, column = 0, sticky = "e", pady = (8,2))
ttk.Entry (frame_courses, textvariable = entry_cname_var).grid (row = 1, column = 1, sticky = "ew", pady = (8,2))
ttk.Label (frame_courses, text = "Instructor").grid (row = 2, column = 0, sticky = "e")
ttk.Entry (frame_courses, textvariable = entry_instr_var).grid (row = 2, column = 1, sticky = "ew")

ttk.Button (frame_courses, text = "Add", command = add_course).grid (row = 1, column = 2, padx = 6, sticky = "ew")
ttk.Button (frame_courses, text = "Update", command = update_course).grid (row = 2, column = 2, padx = 6, sticky = "ew")
ttk.Button (frame_courses, text = "Delete", command = delete_course).grid (row = 3, column = 2, padx = 6, sticky = "ew")
ttk.Button (frame_courses, text = "Clear", command = clear_course_fields).grid (row = 3, column = 1, padx = 6, sticky = "e")

#* ---------- Ініціалізація бд ----------.
#Встановлення шляху до бащи даних.
db.set_db_path (DEFAULT_DB)
db.init_db()
db_label_var.set (f"DB: {DEFAULT_DB}")
#Деф оновлення всього при зміні бд.
def refresh_all():
    refresh_courses()
    reload_enroll_courses_combo()
    refresh_course_filter()
    refresh_students()
    reload_enroll_courses_combo()

refresh_all()

#*Посилання на мій репозиторій.
print("https://github.com/JohnIvanov/university-journal")
#*Запуск додатку.
root.mainloop()
