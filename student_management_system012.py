import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class SimpleStudentSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Result System")
        self.root.geometry("900x650")
        self.connect_database()
        self.create_interface()

    def connect_database(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="your_password_here",  # ← Replace this with "<your-password>" or leave blank
                database="your_database_name"
                )
            self.cursor = self.db.cursor()
            self.create_tables()
        except mysql.connector.Error:
            try:
                temp_db = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password=""
                )
                temp_cursor = temp_db.cursor()
                temp_cursor.execute("CREATE DATABASE school_db")
                temp_db.commit()
                temp_cursor.close()
                temp_db.close()
                self.db = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="your_password_here",
                    database="your_database_name"
                )
                self.cursor = self.db.cursor()
                self.create_tables()
            except Exception as e:
                messagebox.showerror("Error", f"Database connection failed: {e}")
                self.root.destroy()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                class VARCHAR(20),
                roll_no VARCHAR(20) UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                subject VARCHAR(50),
                marks INT,
                skill VARCHAR(50),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)
        self.db.commit()

    def create_interface(self):
        title = tk.Label(self.root, text="Student Result Management System",
                         font=("Arial", 20, "bold"), bg="lightblue")
        title.pack(fill=tk.X, pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_add_student_tab()
        self.create_add_marks_tab()
        self.create_view_results_tab()
        self.create_search_tab()

    def create_add_student_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Add Student")

        tk.Label(frame, text="Add New Student", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(frame, text="Student Name:", font=("Arial", 12)).pack()
        self.name_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.name_entry.pack(pady=5)

        tk.Label(frame, text="Class:", font=("Arial", 12)).pack()
        self.class_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.class_entry.pack(pady=5)

        tk.Label(frame, text="Roll Number:", font=("Arial", 12)).pack()
        self.roll_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.roll_entry.pack(pady=5)

        tk.Button(frame, text="Add Student", command=self.add_student,
                  font=("Arial", 12, "bold"), bg="green", fg="white").pack(pady=10)

        tk.Button(frame, text="Update Selected Student", command=self.update_student,
                  font=("Arial", 10), bg="orange", fg="white").pack(pady=(5, 2))

        tk.Button(frame, text="Delete Selected Student", command=self.delete_student,
                  font=("Arial", 10), bg="red", fg="white").pack(pady=(2, 10))

        tk.Label(frame, text="All Students:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        self.students_listbox = tk.Listbox(frame, height=10, font=("Arial", 10))
        self.students_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.refresh_students_list()

    def add_student(self):
        name = self.name_entry.get().strip()
        class_name = self.class_entry.get().strip()
        roll_no = self.roll_entry.get().strip()

        if not name or not class_name or not roll_no:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        try:
            query = "INSERT INTO students (name, class, roll_no) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (name, class_name, roll_no))
            self.db.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.name_entry.delete(0, tk.END)
            self.class_entry.delete(0, tk.END)
            self.roll_entry.delete(0, tk.END)
            self.refresh_students_list()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Roll number already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")

    def update_student(self):
        selected = self.students_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to update.")
            return

        selected_text = self.students_listbox.get(selected[0])
        student_id = int(selected_text.split("ID: ")[1].split(" |")[0])

        name = self.name_entry.get().strip()
        class_name = self.class_entry.get().strip()
        roll_no = self.roll_entry.get().strip()

        if not name or not class_name or not roll_no:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        try:
            query = "UPDATE students SET name = %s, class = %s, roll_no = %s WHERE id = %s"
            self.cursor.execute(query, (name, class_name, roll_no, student_id))
            self.db.commit()
            messagebox.showinfo("Success", "Student updated successfully!")
            self.refresh_students_list()
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")

    def delete_student(self):
        selected = self.students_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this student and all their marks?")
        if not confirm:
            return

        selected_text = self.students_listbox.get(selected[0])
        student_id = int(selected_text.split("ID: ")[1].split(" |")[0])

        try:
            query = "DELETE FROM students WHERE id = %s"
            self.cursor.execute(query, (student_id,))
            self.db.commit()
            messagebox.showinfo("Success", "Student and their marks deleted!")
            self.refresh_students_list()
        except Exception as e:
            messagebox.showerror("Error", f"Deletion failed: {e}")
    def refresh_students_list(self):
        self.students_listbox.delete(0, tk.END)
        try:
            self.cursor.execute("SELECT id, name, class, roll_no FROM students")
            students = self.cursor.fetchall()
            for student in students:
                student_info = f"ID: {student[0]} | {student[1]} | Class: {student[2]} | Roll: {student[3]}"
                self.students_listbox.insert(tk.END, student_info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")

    def create_add_marks_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Add Marks")

        tk.Label(frame, text="Add / Update Student Marks", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(frame, text="Select Student:", font=("Arial", 12)).pack()
        self.student_combo = ttk.Combobox(frame, font=("Arial", 12), width=40, state="readonly")
        self.student_combo.pack(pady=5)
        self.load_students_combo()

        self.subjects_listbox = tk.Listbox(frame, height=5, font=("Arial", 10))
        self.subjects_listbox.pack(pady=5)
        self.subjects_listbox.bind("<<ListboxSelect>>", self.load_selected_subject_data)

        tk.Button(frame, text="Load Subjects", command=self.load_student_subjects).pack(pady=2)

        tk.Label(frame, text="Subject:", font=("Arial", 12)).pack()
        self.subject_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.subject_entry.pack(pady=5)

        tk.Label(frame, text="Marks (out of 100):", font=("Arial", 12)).pack()
        self.marks_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.marks_entry.pack(pady=5)

        tk.Label(frame, text="Skill (e.g., Python, Java):", font=("Arial", 12)).pack()
        self.skill_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.skill_entry.pack(pady=5)

        tk.Button(frame, text="Add Marks", command=self.add_marks,
                  font=("Arial", 12, "bold"), bg="blue", fg="white").pack(pady=5)

        tk.Button(frame, text="Update Selected Marks", command=self.update_marks,
                  font=("Arial", 10), bg="orange", fg="white").pack(pady=2)

        tk.Button(frame, text="Delete Selected Marks", command=self.delete_marks,
                  font=("Arial", 10), bg="red", fg="white").pack(pady=2)

    def load_students_combo(self):
        try:
            self.cursor.execute("SELECT id, name, roll_no FROM students")
            students = self.cursor.fetchall()
            student_list = [f"{s[1]} (Roll: {s[2]}) - ID: {s[0]}" for s in students]
            self.student_combo['values'] = student_list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")

    def load_student_subjects(self):
        self.subjects_listbox.delete(0, tk.END)
        if not self.student_combo.get():
            return

        try:
            student_id = int(self.student_combo.get().split("ID: ")[1])
            self.cursor.execute("SELECT subject FROM marks WHERE student_id = %s", (student_id,))
            subjects = self.cursor.fetchall()
            for subject in subjects:
                self.subjects_listbox.insert(tk.END, subject[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load subjects: {e}")

    def load_selected_subject_data(self, event):
        try:
            subject_name = self.subjects_listbox.get(self.subjects_listbox.curselection())
            student_id = int(self.student_combo.get().split("ID: ")[1])
            self.cursor.execute("SELECT subject, marks, skill FROM marks WHERE student_id = %s AND subject = %s",
                                (student_id, subject_name))
            data = self.cursor.fetchone()
            if data:
                self.subject_entry.delete(0, tk.END)
                self.marks_entry.delete(0, tk.END)
                self.skill_entry.delete(0, tk.END)

                self.subject_entry.insert(0, data[0])
                self.marks_entry.insert(0, data[1])
                self.skill_entry.insert(0, data[2])
        except:
            pass

    def add_marks(self):
        if not self.student_combo.get():
            messagebox.showerror("Error", "Please select a student!")
            return

        subject = self.subject_entry.get().strip()
        marks_text = self.marks_entry.get().strip()
        skill = self.skill_entry.get().strip()

        if not subject or not marks_text or not skill:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        try:
            marks = int(marks_text)
            if marks < 0 or marks > 100:
                messagebox.showerror("Error", "Marks must be between 0 and 100!")
                return

            selected_text = self.student_combo.get()
            student_id = int(selected_text.split("ID: ")[1])

            query = "INSERT INTO marks (student_id, subject, marks, skill) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (student_id, subject, marks, skill))
            self.db.commit()
            messagebox.showinfo("Success", f"Marks added for {subject}!")
            self.subject_entry.delete(0, tk.END)
            self.marks_entry.delete(0, tk.END)
            self.skill_entry.delete(0, tk.END)
            self.load_student_subjects()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Duplicate entry!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add marks: {e}")

    def update_marks(self):
        try:
            student_id = int(self.student_combo.get().split("ID: ")[1])
            selected_subject = self.subjects_listbox.get(self.subjects_listbox.curselection())
            new_subject = self.subject_entry.get().strip()
            new_marks = int(self.marks_entry.get().strip())
            new_skill = self.skill_entry.get().strip()

            if not new_subject or not new_skill:
                messagebox.showerror("Error", "All fields required!")
                return

            query = "UPDATE marks SET subject=%s, marks=%s, skill=%s WHERE student_id=%s AND subject=%s"
            self.cursor.execute(query, (new_subject, new_marks, new_skill, student_id, selected_subject))
            self.db.commit()
            messagebox.showinfo("Success", "Marks updated!")
            self.load_student_subjects()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update: {e}")

    def delete_marks(self):
        try:
            subject = self.subjects_listbox.get(self.subjects_listbox.curselection())
            student_id = int(self.student_combo.get().split("ID: ")[1])
            self.cursor.execute("DELETE FROM marks WHERE student_id = %s AND subject = %s", (student_id, subject))
            self.db.commit()
            messagebox.showinfo("Deleted", "Marks deleted.")
            self.load_student_subjects()
            self.subject_entry.delete(0, tk.END)
            self.marks_entry.delete(0, tk.END)
            self.skill_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")
    def create_view_results_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="View Results")

        tk.Label(frame, text="View Student Results", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(frame, text="Select Student:", font=("Arial", 12)).pack()
        self.result_combo = ttk.Combobox(frame, font=("Arial", 12), width=40, state="readonly")
        self.result_combo.pack(pady=5)
        self.load_result_combo()

        tk.Button(frame, text="View Result", command=self.view_result,
                  font=("Arial", 12, "bold"), bg="orange", fg="white").pack(pady=10)

        self.result_text = tk.Text(frame, height=20, width=75, font=("Arial", 11))
        self.result_text.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    def load_result_combo(self):
        try:
            self.cursor.execute("SELECT id, name, roll_no FROM students")
            students = self.cursor.fetchall()
            student_list = [f"{s[1]} (Roll: {s[2]}) - ID: {s[0]}" for s in students]
            self.result_combo['values'] = student_list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")

    def view_result(self):
        if not self.result_combo.get():
            messagebox.showerror("Error", "Please select a student!")
            return

        try:
            student_id = int(self.result_combo.get().split("ID: ")[1])

            self.cursor.execute("SELECT name, class, roll_no FROM students WHERE id = %s", (student_id,))
            student = self.cursor.fetchone()

            self.cursor.execute("SELECT subject, marks, skill FROM marks WHERE student_id = %s", (student_id,))
            marks = self.cursor.fetchall()

            self.result_text.delete(1.0, tk.END)

            if not marks:
                self.result_text.insert(tk.END, "No marks found for this student!")
                return

            result_text = f"STUDENT RESULT CARD\n{'='*50}\n\n"
            result_text += f"Name: {student[0]}\nClass: {student[1]}\nRoll No: {student[2]}\n\n"
            result_text += f"MARKS & SKILLS:\n{'-'*40}\n"

            total_marks = 0
            total_subjects = len(marks)

            for subject, mark, skill in marks:
                result_text += f"{subject}: {mark}/100 | Skill: {skill}\n"
                total_marks += mark

            percentage = (total_marks / (total_subjects * 100)) * 100

            if percentage >= 90:
                grade = "A+"
            elif percentage >= 80:
                grade = "A"
            elif percentage >= 70:
                grade = "B"
            elif percentage >= 60:
                grade = "C"
            elif percentage >= 50:
                grade = "D"
            else:
                grade = "F"

            if percentage >= 75:
                strength = "Strong in academics"
            elif percentage >= 50:
                strength = "Average in academics"
            else:
                strength = "Needs improvement"

            result_text += f"\n{'-'*40}\n"
            result_text += f"Total Marks: {total_marks}/{total_subjects * 100}\n"
            result_text += f"Percentage: {percentage:.2f}%\n"
            result_text += f"Grade: {grade}\n"
            result_text += f"Academic Performance: {strength}\n"

            self.result_text.insert(tk.END, result_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch results: {e}")

    def create_search_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Search")

        tk.Label(frame, text="Search Students", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(frame, text="Enter student name or roll number:", font=("Arial", 12)).pack()
        self.search_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.search_entry.pack(pady=10)

        tk.Button(frame, text="Search", command=self.search_student,
                  font=("Arial", 12, "bold"), bg="purple", fg="white").pack(pady=10)

        tk.Label(frame, text="Search Results:", font=("Arial", 12, "bold")).pack(pady=(20, 10))
        self.search_listbox = tk.Listbox(frame, height=15, font=("Arial", 10))
        self.search_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def search_student(self):
        search_term = self.search_entry.get().strip()

        if not search_term:
            messagebox.showerror("Error", "Please enter search term!")
            return

        try:
            query = "SELECT id, name, class, roll_no FROM students WHERE name LIKE %s OR roll_no LIKE %s"
            search_pattern = f"%{search_term}%"
            self.cursor.execute(query, (search_pattern, search_pattern))
            results = self.cursor.fetchall()

            self.search_listbox.delete(0, tk.END)

            if not results:
                self.search_listbox.insert(tk.END, "No students found!")
            else:
                for student in results:
                    student_info = f"ID: {student[0]} | {student[1]} | Class: {student[2]} | Roll: {student[3]}"
                    self.search_listbox.insert(tk.END, student_info)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = SimpleStudentSystem()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")


