import tkinter as tk
from tkinter import ttk

class Sidebar(ttk.Frame):
    def __init__(self, parent, page_switcher, snapshot_manager, project_callback):
        super().__init__(parent, style="Sidebar.TFrame", width=200)
        self.pack(side="left", fill="y")
        self.pack_propagate(False)
        
        self.snapshot_manager = snapshot_manager
        self.project_callback = project_callback

        # Logo/Title
        title = tk.Label(self, text="Dashboard", font=("Helvetica", 20, "bold"),
                        bg="#2c3e50", fg="white")
        title.pack(pady=20)

        # Project Selection
        project_frame = ttk.Frame(self, style="Sidebar.TFrame")
        project_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        project_label = tk.Label(project_frame, text="Select Project:",
                               font=("Helvetica", 10), bg="#2c3e50", fg="white")
        project_label.pack(anchor="w")
        
        self.project_var = tk.StringVar()
        self.project_dropdown = ttk.Combobox(project_frame, 
                                           textvariable=self.project_var,
                                           state="readonly")
        self.project_dropdown.pack(fill="x", pady=(5, 0))
        self.project_dropdown.bind('<<ComboboxSelected>>', self.on_project_selected)

        # Menu Buttons
        menu_items = ["Home", "Reports", "Settings"]
        for item in menu_items:
            btn = tk.Button(self, text=item, font=("Helvetica", 12),
                          bg="#2c3e50", fg="white", bd=0, pady=10,
                          activebackground="#34495e", activeforeground="white",
                          width=20, command=lambda i=item: page_switcher(i))
            btn.pack(pady=5)

    def refresh_projects(self):
        """Update the projects dropdown"""
        projects = self.snapshot_manager.get_all_projects()
        self.project_dropdown['values'] = projects
        if projects and not self.project_var.get():
            self.project_dropdown.set(projects[0])
            self.on_project_selected(None)

    def on_project_selected(self, event):
        """Handle project selection"""
        selected = self.project_var.get()
        if selected:
            self.project_callback(selected)