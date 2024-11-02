import os
import json
from datetime import datetime
from collections import defaultdict

class SnapshotManager:
    def __init__(self):
        self.snapshot_dir = None
        self.project_data = defaultdict(lambda: defaultdict(list))
        self.projects_list = set()

    def set_snapshot_dir(self, directory):
        self.snapshot_dir = directory
        self.scan_snapshots()

    def scan_snapshots(self):
        """Scans the snapshot directory and builds the data structure"""
        self.project_data.clear()
        self.projects_list.clear()

        if not self.snapshot_dir or not os.path.exists(self.snapshot_dir):
            return

        # Walk through the directory structure
        for date_folder in os.listdir(self.snapshot_dir):
            date_path = os.path.join(self.snapshot_dir, date_folder)
            if not os.path.isdir(date_path):
                continue

            # Process each project folder within the date folder
            for project_name in os.listdir(date_path):
                project_path = os.path.join(date_path, project_name)
                if not os.path.isdir(project_path):
                    continue

                self.projects_list.add(project_name)

                # Process each JSON file in the project folder
                for json_file in os.listdir(project_path):
                    if not json_file.endswith('.json'):
                        continue

                    file_path = os.path.join(project_path, json_file)
                    timestamp = self._parse_timestamp(json_file)
                    
                    # Store the file path and timestamp
                    self.project_data[project_name][date_folder].append({
                        'timestamp': timestamp,
                        'file_path': file_path
                    })

    def _parse_timestamp(self, filename):
        """Parse timestamp from filename (e.g., '2024-11-01_22-44-27.json')"""
        datetime_str = filename.split('.')[0]  # Remove .json
        return datetime.strptime(datetime_str, '%Y-%m-%d_%H-%M-%S')

    def get_all_projects(self):
        """Returns a sorted list of all unique project names"""
        return sorted(list(self.projects_list))

    def get_project_dates(self, project_name):
        """Returns all dates available for a specific project"""
        return sorted(self.project_data[project_name].keys())

    def get_project_snapshots(self, project_name, date=None):
        """Returns all snapshots for a project, optionally filtered by date"""
        if date:
            return sorted(self.project_data[project_name][date], 
                        key=lambda x: x['timestamp'])
        
        # If no date specified, return all snapshots across all dates
        all_snapshots = []
        for date_snapshots in self.project_data[project_name].values():
            all_snapshots.extend(date_snapshots)
        return sorted(all_snapshots, key=lambda x: x['timestamp'])

    def load_snapshot_data(self, file_path):
        """Loads and returns the JSON data from a specific snapshot file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading snapshot: {e}")
            return None