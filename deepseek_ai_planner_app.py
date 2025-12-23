import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import json
import random
from collections import defaultdict
import numpy as np
from PIL import Image, ImageTk
import threading

class AIStudyPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Study Planner")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f4f8')
        
        # Initialize data structures
        self.courses = []
        self.assignments = []
        self.study_sessions = []
        self.user_preferences = {
            'focus_hours': 2,
            'break_minutes': 15,
            'daily_study_hours': 4,
            'preferred_times': ['Morning', 'Afternoon', 'Evening']
        }
        
        # Load sample data
        self.load_sample_data()
        
        # Setup GUI
        self.setup_gui()
        
        # Initialize with default schedule
        self.generate_schedule()
    
    def setup_gui(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'), background='#f0f4f8')
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'), background='#f0f4f8')
        style.configure('Card.TFrame', background='white', relief='raised', borderwidth=2)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f4f8')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg='#4a6fa5')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="AI Study Planner", 
                               font=('Helvetica', 24, 'bold'), 
                               bg='#4a6fa5', fg='white', pady=10)
        title_label.pack()
        
        # Main content area
        content_frame = tk.Frame(main_container, bg='#f0f4f8')
        content_frame.pack(fill='both', expand=True)
        
        # Left panel - Input and controls
        left_panel = tk.Frame(content_frame, bg='#f0f4f8', width=400)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        
        # Right panel - Schedule display
        right_panel = tk.Frame(content_frame, bg='#f0f4f8')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Left Panel Contents
        self.create_input_section(left_panel)
        self.create_courses_section(left_panel)
        self.create_preferences_section(left_panel)
        
        # Right Panel Contents
        self.create_schedule_section(right_panel)
        self.create_stats_section(right_panel)
    
    def create_input_section(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Add New Task", style='Card.TFrame')
        input_frame.pack(fill='x', pady=(0, 15))
        
        # Course name
        tk.Label(input_frame, text="Course:", bg='white').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.course_var = tk.StringVar()
        course_entry = ttk.Entry(input_frame, textvariable=self.course_var, width=25)
        course_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Task name
        tk.Label(input_frame, text="Task:", bg='white').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.task_var = tk.StringVar()
        task_entry = ttk.Entry(input_frame, textvariable=self.task_var, width=25)
        task_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Due date
        tk.Label(input_frame, text="Due Date:", bg='white').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.due_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        due_date_entry = ttk.Entry(input_frame, textvariable=self.due_date_var, width=25)
        due_date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Priority
        tk.Label(input_frame, text="Priority:", bg='white').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var, 
                                     values=["Low", "Medium", "High"], width=23)
        priority_combo.grid(row=3, column=1, padx=5, pady=5)
        
        # Estimated hours
        tk.Label(input_frame, text="Est. Hours:", bg='white').grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.hours_var = tk.StringVar(value="2")
        hours_spinbox = ttk.Spinbox(input_frame, from_=1, to=20, textvariable=self.hours_var, width=23)
        hours_spinbox.grid(row=4, column=1, padx=5, pady=5)
        
        # Add button
        add_button = ttk.Button(input_frame, text="Add Task", command=self.add_task, width=20)
        add_button.grid(row=5, column=0, columnspan=2, pady=10)
    
    def create_courses_section(self, parent):
        courses_frame = ttk.LabelFrame(parent, text="Current Courses & Tasks", style='Card.TFrame')
        courses_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Treeview for courses and assignments
        columns = ('Course', 'Task', 'Due Date', 'Priority', 'Hours')
        self.tasks_tree = ttk.Treeview(courses_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.tasks_tree.heading(col, text=col)
            self.tasks_tree.column(col, width=100)
        
        self.tasks_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(courses_frame, orient='vertical', command=self.tasks_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate with existing tasks
        self.update_tasks_tree()
        
        # Delete button
        delete_button = ttk.Button(courses_frame, text="Delete Selected", command=self.delete_task)
        delete_button.pack(pady=5)
    
    def create_preferences_section(self, parent):
        pref_frame = ttk.LabelFrame(parent, text="Study Preferences", style='Card.TFrame')
        pref_frame.pack(fill='x')
        
        # Daily study hours
        tk.Label(pref_frame, text="Daily Study Hours:", bg='white').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.study_hours_var = tk.StringVar(value=str(self.user_preferences['daily_study_hours']))
        study_hours_spinbox = ttk.Spinbox(pref_frame, from_=1, to=12, 
                                          textvariable=self.study_hours_var, width=15)
        study_hours_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        # Focus session length
        tk.Label(pref_frame, text="Focus Session (hrs):", bg='white').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.focus_hours_var = tk.StringVar(value=str(self.user_preferences['focus_hours']))
        focus_hours_spinbox = ttk.Spinbox(pref_frame, from_=0.5, to=4, increment=0.5,
                                         textvariable=self.focus_hours_var, width=15)
        focus_hours_spinbox.grid(row=1, column=1, padx=5, pady=5)
        
        # Break length
        tk.Label(pref_frame, text="Break (minutes):", bg='white').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.break_minutes_var = tk.StringVar(value=str(self.user_preferences['break_minutes']))
        break_minutes_spinbox = ttk.Spinbox(pref_frame, from_=5, to=60, increment=5,
                                           textvariable=self.break_minutes_var, width=15)
        break_minutes_spinbox.grid(row=2, column=1, padx=5, pady=5)
        
        # Update preferences button
        update_button = ttk.Button(pref_frame, text="Update Preferences", 
                                  command=self.update_preferences, width=20)
        update_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Generate schedule button
        generate_button = ttk.Button(pref_frame, text="Generate New Schedule", 
                                    command=self.generate_schedule, width=20)
        generate_button.grid(row=4, column=0, columnspan=2, pady=(0, 10))
    
    def create_schedule_section(self, parent):
        schedule_frame = ttk.LabelFrame(parent, text="Study Schedule", style='Card.TFrame')
        schedule_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Text area for schedule display
        self.schedule_text = scrolledtext.ScrolledText(schedule_frame, wrap=tk.WORD, 
                                                       width=80, height=15,
                                                       font=('Consolas', 10))
        self.schedule_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Export button
        export_button = ttk.Button(schedule_frame, text="Export Schedule", 
                                  command=self.export_schedule)
        export_button.pack(side='right', padx=10, pady=(0, 10))
    
    def create_stats_section(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="Study Statistics", style='Card.TFrame')
        stats_frame.pack(fill='x')
        
        # Stats display
        self.stats_text = tk.Text(stats_frame, height=6, width=80, 
                                 font=('Helvetica', 10), bg='white')
        self.stats_text.pack(fill='x', padx=10, pady=10)
        
        # Update stats
        self.update_stats()
    
    def load_sample_data(self):
        # Sample courses
        self.courses = [
            {"name": "Mathematics", "code": "MATH101", "difficulty": 3},
            {"name": "Computer Science", "code": "CS201", "difficulty": 4},
            {"name": "Physics", "code": "PHYS101", "difficulty": 4},
            {"name": "Literature", "code": "LIT201", "difficulty": 2}
        ]
        
        # Sample assignments
        today = datetime.now()
        self.assignments = [
            {"course": "Mathematics", "task": "Complete calculus exercises", 
             "due_date": (today + timedelta(days=2)).strftime('%Y-%m-%d'), 
             "priority": "High", "hours": 3},
            {"course": "Computer Science", "task": "AI project implementation", 
             "due_date": (today + timedelta(days=5)).strftime('%Y-%m-%d'), 
             "priority": "High", "hours": 8},
            {"course": "Physics", "task": "Lab report on optics", 
             "due_date": (today + timedelta(days=7)).strftime('%Y-%m-%d'), 
             "priority": "Medium", "hours": 4},
            {"course": "Literature", "task": "Read chapters 5-7", 
             "due_date": (today + timedelta(days=10)).strftime('%Y-%m-%d'), 
             "priority": "Low", "hours": 2}
        ]
    
    def add_task(self):
        course = self.course_var.get().strip()
        task = self.task_var.get().strip()
        due_date = self.due_date_var.get().strip()
        priority = self.priority_var.get()
        hours = self.hours_var.get()
        
        if not course or not task or not due_date:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        try:
            hours = float(hours)
            if hours <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number of hours.")
            return
        
        # Add to assignments list
        self.assignments.append({
            "course": course,
            "task": task,
            "due_date": due_date,
            "priority": priority,
            "hours": hours
        })
        
        # Update UI
        self.update_tasks_tree()
        self.clear_input_fields()
        messagebox.showinfo("Success", "Task added successfully!")
    
    def clear_input_fields(self):
        self.course_var.set("")
        self.task_var.set("")
        self.due_date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.priority_var.set("Medium")
        self.hours_var.set("2")
    
    def update_tasks_tree(self):
        # Clear existing items
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        
        # Add assignments to treeview
        for i, assignment in enumerate(self.assignments):
            self.tasks_tree.insert('', 'end', iid=i, values=(
                assignment['course'],
                assignment['task'],
                assignment['due_date'],
                assignment['priority'],
                assignment['hours']
            ))
    
    def delete_task(self):
        selected = self.tasks_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")
            return
        
        # Get index of selected item
        index = int(selected[0])
        
        # Remove from assignments list
        if 0 <= index < len(self.assignments):
            del self.assignments[index]
        
        # Update UI
        self.update_tasks_tree()
    
    def update_preferences(self):
        try:
            self.user_preferences['daily_study_hours'] = float(self.study_hours_var.get())
            self.user_preferences['focus_hours'] = float(self.focus_hours_var.get())
            self.user_preferences['break_minutes'] = int(self.break_minutes_var.get())
            messagebox.showinfo("Success", "Preferences updated successfully!")
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter valid numbers.")
    
    def generate_schedule(self):
        # Clear previous schedule
        self.study_sessions = []
        
        if not self.assignments:
            self.schedule_text.delete(1.0, tk.END)
            self.schedule_text.insert(tk.END, "No tasks to schedule. Add tasks first.")
            return
        
        # Sort assignments by priority and due date
        priority_values = {"High": 3, "Medium": 2, "Low": 1}
        sorted_assignments = sorted(self.assignments, 
                                   key=lambda x: (priority_values[x['priority']], 
                                                 datetime.strptime(x['due_date'], '%Y-%m-%d')))
        
        # Generate schedule using AI-like algorithm
        today = datetime.now()
        current_date = today
        daily_hours_remaining = self.user_preferences['daily_study_hours']
        session_count = 0
        
        self.schedule_text.delete(1.0, tk.END)
        schedule_output = "AI-GENERATED STUDY SCHEDULE\n"
        schedule_output += "=" * 50 + "\n\n"
        
        for assignment in sorted_assignments:
            due_date = datetime.strptime(assignment['due_date'], '%Y-%m-%d')
            days_until_due = (due_date - today).days
            
            if days_until_due < 0:
                schedule_output += f"⚠️ OVERDUE: {assignment['task']} (was due {assignment['due_date']})\n"
                continue
            
            # Calculate hours per day needed
            hours_needed = assignment['hours']
            days_available = max(1, days_until_due)
            hours_per_day = min(hours_needed / days_available, 
                              self.user_preferences['daily_study_hours'] / 2)
            
            schedule_output += f"\n📚 {assignment['course']}: {assignment['task']}\n"
            schedule_output += f"   Due: {assignment['due_date']} | Priority: {assignment['priority']}\n"
            schedule_output += f"   Recommended: {hours_per_day:.1f} hours per day\n"
            
            # Generate sessions for this assignment
            hours_allocated = 0
            current_date = today
            
            while hours_allocated < hours_needed and current_date <= due_date:
                if current_date.weekday() >= 5:  # Skip weekends
                    current_date += timedelta(days=1)
                    continue
                
                # Calculate session hours for this day
                session_hours = min(hours_per_day, hours_needed - hours_allocated, 
                                  self.user_preferences['focus_hours'])
                
                if session_hours > 0:
                    # Create session
                    session = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'course': assignment['course'],
                        'task': assignment['task'],
                        'hours': session_hours,
                        'priority': assignment['priority']
                    }
                    self.study_sessions.append(session)
                    
                    schedule_output += f"   • {current_date.strftime('%A, %b %d')}: "
                    schedule_output += f"{session_hours:.1f} hours\n"
                    
                    hours_allocated += session_hours
                    session_count += 1
                
                current_date += timedelta(days=1)
        
        # Add study tips
        schedule_output += "\n" + "=" * 50 + "\n"
        schedule_output += "📝 AI STUDY TIPS:\n"
        tips = [
            "Use the Pomodoro technique: 25 min focus, 5 min break",
            "Review material within 24 hours to improve retention by up to 60%",
            "Study hardest subjects when you're most alert",
            "Teach what you've learned to reinforce understanding",
            "Take regular breaks to maintain focus and prevent burnout"
        ]
        
        for tip in tips:
            schedule_output += f"• {tip}\n"
        
        # Display schedule
        self.schedule_text.insert(tk.END, schedule_output)
        
        # Update statistics
        self.update_stats()
    
    def update_stats(self):
        total_hours = sum(assignment['hours'] for assignment in self.assignments)
        high_priority = sum(1 for a in self.assignments if a['priority'] == 'High')
        medium_priority = sum(1 for a in self.assignments if a['priority'] == 'Medium')
        low_priority = sum(1 for a in self.assignments if a['priority'] == 'Low')
        
        stats_text = f"""
        Study Statistics:
        • Total tasks: {len(self.assignments)}
        • Total study hours needed: {total_hours}
        • High priority tasks: {high_priority}
        • Medium priority tasks: {medium_priority}
        • Low priority tasks: {low_priority}
        • Recommended daily study: {self.user_preferences['daily_study_hours']} hours
        """
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
    
    def export_schedule(self):
        try:
            filename = f"study_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(self.schedule_text.get(1.0, tk.END))
            messagebox.showinfo("Export Successful", f"Schedule exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export schedule: {str(e)}")

def main():
    root = tk.Tk()
    app = AIStudyPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()