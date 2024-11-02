import tkinter as tk
from tkinter import ttk

class SettingsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Settings Page", font=("Helvetica", 24, "bold"),
                bg="white").pack(pady=20)