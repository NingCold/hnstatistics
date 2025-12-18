from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from hnstatistics.core.config.app_config import AppConfig
from hnstatistics.core.path import ensure_dir

class ConfigDialog(tk.Toplevel):
    def __init__(self, parent, config: AppConfig, on_save):
        super().__init__(parent)
        self.title("Preferences")
        self.resizable(False, False)
        self.config = config
        self.on_save = on_save
        
        self.var_font_family = tk.StringVar(value=self.config.font_family)
        self.var_font_size = tk.IntVar(value=self.config.font_size)
        self.var_font_weight = tk.StringVar(value=self.config.font_weight)
        self.var_default_save_dir = tk.StringVar(value=self.config.default_save_dir or ".")
        
        self._build()
    
    def _build(self):
        frame = ttk.Frame(self, padding="12")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Font Family:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.var_font_family).grid(row=0, column=1, sticky="ew")
        
        ttk.Label(frame, text="Font Size:").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(frame, from_=8, to=72, textvariable=self.var_font_size).grid(row=1, column=1, sticky="ew")
        
        ttk.Label(frame, text="Font Weight:").grid(row=2, column=0, sticky="w")
        ttk.Combobox(frame, textvariable=self.var_font_weight, values=["normal", "bold"]).grid(row=2, column=1, sticky="ew")
        
        ttk.Label(frame, text="Default Save Directory:").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.var_default_save_dir).grid(row=3, column=1, sticky="ew")
        ttk.Button(frame, text="Browse...", command=self._browse_directory).grid(row=3, column=2, sticky="ew")
        
        btns = ttk.Frame(frame)
        btns.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        ttk.Button(btns, text="Save", command=self._save).pack(side="right", padx=(0, 5))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")
        
        frame.columnconfigure(1, weight=1)
    
    def _browse_directory(self):
        path = filedialog.askdirectory(
            title="Select Default Save Directory",
            initialdir=ensure_dir(Path(self.var_default_save_dir.get()))
        )
        if path:
            self.var_default_save_dir.set(path)
    
    def _save(self):
        self.config.font_family = self.var_font_family.get()
        self.config.font_size = self.var_font_size.get()
        self.config.font_weight = self.var_font_weight.get()
        
        dir_value = self.var_default_save_dir.get().strip()
        self.config.default_save_dir = dir_value if dir_value else None
        
        self.on_save()
        self.destroy()