import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv
from datetime import datetime

class HomePage(ttk.Frame):
    def __init__(self, parent, snapshot_manager):
        super().__init__(parent)
        self.snapshot_manager = snapshot_manager
        self.create_content()

    def create_content(self):
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 20))
        
        self.header_label = tk.Label(header, text="Select a Project", 
                                   font=("Helvetica", 24, "bold"),
                                   bg="white")
        self.header_label.pack(side="left")

        # Add Export Button
        self.export_button = ttk.Button(
            header,
            text="Export to CSV",
            command=self.export_to_csv
        )
        self.export_button.pack(side="right", padx=10)
        self.export_button.state(['disabled'])  # Initially disabled

        # Project info container
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(fill="both", expand=True, padx=20)

    def refresh(self, selected_project=None):
        """Update the view based on selected project"""
        if selected_project:
            self.header_label.config(text=f"Project: {selected_project}")
            # Get project dates
            dates = self.snapshot_manager.get_project_dates(selected_project)
            # Get all snapshots
            snapshots = self.snapshot_manager.get_project_snapshots(selected_project)
            # Update UI with project information
            self.update_project_info(dates, snapshots)
            # Enable export button
            self.export_button.state(['!disabled'])
            # Store current project and snapshots for export
            self.current_project = selected_project
            self.current_snapshots = snapshots
        else:
            self.header_label.config(text="Select a Project")
            self.export_button.state(['disabled'])
            self.current_project = None
            self.current_snapshots = None

    def export_to_csv(self):
        """Export current project data to CSV"""
        if not self.current_project or not self.current_snapshots:
            return

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.current_project}_report_{timestamp}.csv"

        # Prepare data for export
        rows = []
        
        # Add header row
        headers = ['Timestamp', 'Test Suite', 'Test Case', 'Status', 'Duration (ms)', 'API Path', 'Method']
        rows.append(headers)

        # Process each snapshot
        for snapshot in self.current_snapshots:
            # Load the snapshot data
            data = self.snapshot_manager.load_snapshot_data(snapshot['file_path'])
            if not data:
                continue

            # Process test suites
            for suite in data.get('testSuites', []):
                suite_name = suite.get('testSuiteName', '')
                
                # Process test cases
                for test_case in suite.get('testCases', []):
                    case_name = test_case.get('testCaseName', '')
                    
                    # Process test steps
                    for step in test_case.get('testSteps', []):
                        if not step:
                            continue

                        # Create row for each test step
                        row = [
                            snapshot['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                            suite_name,
                            case_name,
                            step.get('statusCode', ''),
                            step.get('duration', ''),
                            step.get('resource', ''),
                            step.get('method', '')
                        ]
                        rows.append(row)

        # Write to CSV file
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)
            tk.messagebox.showinfo("Success", f"Report exported successfully to {filename}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to export report: {str(e)}")
            
    def update_project_info(self, dates, snapshots):
        """Update the project information display"""
        # Clear existing widgets
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        if not dates or not snapshots:
            ttk.Label(self.info_frame, text="No data available").pack()
            return

        # Create a frame for statistics
        stats_frame = ttk.Frame(self.info_frame)
        stats_frame.pack(fill="x", pady=(0, 20))

        # Display basic statistics
        ttk.Label(stats_frame, text=f"Total Snapshots: {len(snapshots)}").pack(side="left", padx=10)
        ttk.Label(stats_frame, text=f"Date Range: {min(dates)} to {max(dates)}").pack(side="left", padx=10)

        # Create a treeview for snapshots
        tree = ttk.Treeview(self.info_frame, columns=("Date", "Time", "Path"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Time", text="Time")
        tree.heading("Path", text="File Path")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate treeview with snapshot data
        for snapshot in sorted(snapshots, key=lambda x: x['timestamp']):
            date_str = snapshot['timestamp'].strftime("%Y-%m-%d")
            time_str = snapshot['timestamp'].strftime("%H:%M:%S")
            tree.insert("", "end", values=(date_str, time_str, snapshot['file_path']))