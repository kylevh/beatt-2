import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from components.sidebar import Sidebar
from pages.home import HomePage
from pages.reports import ReportsPage
from pages.settings import SettingsPage
from utils.snapshot_manager import SnapshotManager

import os

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("BEATT Dashboard")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")
        
        # Create custom styles
        self.style = ttk.Style()
        self.style.configure("Card.TFrame", background="#ffffff", relief="flat")
        self.style.configure("Sidebar.TFrame", background="#2c3e50")
        
        # Initialize snapshot manager and selected project
        self.snapshot_manager = SnapshotManager()
        self.selected_project = None
        
        # Set default snapshots directory
        default_snapshots_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "SOAP2", "snapshots")
        if os.path.exists(default_snapshots_path):
            self.snapshot_manager.set_snapshot_dir(default_snapshots_path)
        
        # Initialize pages dictionary and current page tracker
        self.pages = {}
        self.current_page = None
        
        # Create sidebar with page switching capability
        self.sidebar = Sidebar(self.root, self.show_page, self.snapshot_manager, self.on_project_selected)
        self.create_menu()
        
        # Create and setup pages
        self.setup_pages()
        self.show_page("Home")
    
    def on_project_selected(self, project_name):
        """Handle project selection"""
        self.selected_project = project_name
        self.refresh_ui()

    def setup_pages(self):
        # Create container for pages
        self.pages_frame = ttk.Frame(self.root, style="Card.TFrame")
        self.pages_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Create pages
        self.pages = {
            "Home": HomePage(self.pages_frame, self.snapshot_manager),
            "Reports": ReportsPage(self.pages_frame),
            "Settings": SettingsPage(self.pages_frame),
}

    def show_page(self, page_name):
        if self.current_page is not None:
            self.current_page.pack_forget()
        
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)
        
    def create_menu(self):
        """Creates the menu bar with File options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Create File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Snapshots Folder", command=self.select_snapshot_folder)
        
    def select_snapshot_folder(self):
        """Opens a dialog to select the snapshots folder"""
        directory = filedialog.askdirectory(
            title="Select Snapshots Folder",
            mustexist=True
        )
        if directory:  # Only update if a folder was selected
            self.snapshot_manager.set_snapshot_dir(directory)
            # Optionally refresh your UI here
            self.refresh_ui()
            
    def refresh_ui(self):
        """Refresh the UI after changing the snapshots directory or selected project"""
        self.sidebar.refresh_projects()
        for page in self.pages.values():
            if hasattr(page, 'refresh'):
                page.refresh(self.selected_project)

if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()