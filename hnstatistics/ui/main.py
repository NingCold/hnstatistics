from copy import deepcopy
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from tkinter import filedialog

from hnstatistics.core.db import init_db
from hnstatistics.core.project import Project
from hnstatistics.core.services.project_service import ProjectService
from hnstatistics.core.errors import HNStatisticsError
from hnstatistics.core.services.statistics_service import StatisticsService
from hnstatistics.core.services.export_service import export_project
from hnstatistics.core.statistics.analyze_options import AnalyzeOptions
from hnstatistics.core.statistics.commit_mode import CommitMode
from hnstatistics.core.statistics.draft import DraftStatistics
from hnstatistics.core.statistics.model import StatisticsModel

# ========== UI State ==========
class UIState:
    def __init__(self):
        self.current_project: Project | None = None
        self.selected_project = None
        self.draft: DraftStatistics = DraftStatistics()
        self.preview_stats: StatisticsModel | None = None
        self.project_list = []
        self.filtered_projects = []
        
        self.sort_column = None
        self.sort_reverse: bool = True
        self.commit_mode: CommitMode = CommitMode.OVERWRITE
        self.last_analyzed_mode: CommitMode = CommitMode.OVERWRITE
        self.analyze_options: AnalyzeOptions = AnalyzeOptions()

ui = {}
state = UIState()
project_service = ProjectService()
statistics_service = StatisticsService()

def refresh_project_list(projects=None):
    tree = ui['project_tree']
    tree.delete(*tree.get_children())

    if projects is None:
        projects = state.project_list = project_service.list_projects()
    
    state.filtered_projects = projects
    
    keyword = ui['project_search'].get().lower()
    
    for project in projects:
        tags = ()
        if keyword and keyword in project.name.lower():
            tags = ("search_match",)
        tree.insert("", "end", text=project.name, tags=tags)
        
def refresh_result_view():
    tree = ui['result_tree']
    tree.delete(*tree.get_children())
    
    stats = state.preview_stats
    
    if not stats:
        return
    
    for k in stats.frequency:
        tree.insert(
            "",
            "end",
            values=(
                k,
                stats.frequency[k],
                f"{stats.probability[k]:.4f}"
            )
        )
    
    if state.sort_column:
        sort_result_tree(state.sort_column)

def set_status(message):
    ui['status_bar'].set(message)

def sort_result_tree(column: str):
    tree = ui['result_tree']
    
    rows = []
    
    for iid in tree.get_children():
        values = tree.item(iid, "values")
        rows.append(values)
    
    if not rows:
        return
    
    if state.sort_column == column:
        state.sort_reverse = not state.sort_reverse
    else:
        state.sort_column = column
        state.sort_reverse = True
    
    col_index = {"item": 0, "freq": 1, "prob": 2}[column]
    
    def sort_key(row):
        value = row[col_index]
        if column == "item":
            return value
        elif column == "freq":
            return int(value)
        elif column == "prob":
            return float(value)
    
    rows.sort(
        key=sort_key,
        reverse=state.sort_reverse
    )
    
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=row)
    
    update_result_tree_headers()
    
    direction = "descending" if state.sort_reverse else "ascending"
    set_status(f"Sorted by {column} ({direction})")

def update_result_tree_headers():
    tree = ui["result_tree"]
    
    col_map = {
        "item": "Item",
        "freq": "Frequency",
        "prob": "Probability"
    }
    
    for col, title in col_map.items():
        arrow = ""
        if state.sort_column == col:
            arrow = " ▲" if not state.sort_reverse else " ▼"
        tree.heading(
            col,
            text=title + arrow,
            command=lambda c=col: sort_result_tree(c)
        )

# ========== command functions ==========
def command_create_project():
    name = simpledialog.askstring("Create Project", "Enter project name:")
    if not name:
        return
    
    try:
        project = project_service.create(name)
        refresh_project_list()
        set_status(f"Created project: {project.name}")
    except HNStatisticsError as e:
        messagebox.showerror("Error", str(e))

def command_open_project():
    index = get_selected_index()
    if index is None:
        return
    
    project = state.filtered_projects[index]
    state.current_project = project_service.load(project.id)
    state.preview_stats = state.current_project.stats
    refresh_result_view()
    set_status(f"Opened project: {state.current_project.name}")

def command_rename_project():
    index = get_selected_index()
    if index is None:
        return
    
    project = state.filtered_projects[index]
    
    new_name = simpledialog.askstring(
        "Rename Project",
        "Enter new project name:",
        initialvalue=project.name
    )
    
    if not new_name:
        return
    
    try:
        project_service.rename(project.id, new_name)
        refresh_project_list()
    except HNStatisticsError as e:
        messagebox.showerror("Error", str(e))

def command_delete_project():
    index = get_selected_index()
    if index is None:
        return
    
    project = state.filtered_projects[index]
    
    confirm = messagebox.askyesno(
        "Delete Project",
        f"Are you sure you want to delete project '{project.name}'?"
    )
    
    if not confirm:
        return
    
    try:
        project_service.delete(project.id)
        refresh_project_list()
    except HNStatisticsError as e:
        messagebox.showerror("Error", str(e))

def command_analyze():
    text = ui["input_text"].get("1.0", tk.END).strip()
    
    if not text and not state.current_project:
        messagebox.showwarning("Warning", "Input text is empty")
        return
    
    try:
        state.draft = statistics_service.create_draft()
        statistics_service.analyze_draft(state.draft, text, state.analyze_options)
        state.preview_stats = deepcopy(state.draft.current)
        if state.current_project:
            if state.commit_mode == CommitMode.MERGE:
                statistics_service.merge_statistics(
                    state.preview_stats,
                    state.current_project.stats
                )
        state.last_analyzed_mode = state.commit_mode
        refresh_result_view()
        set_status("Analysis completed")
    except HNStatisticsError as e:
        messagebox.showerror("Error", str(e))

def command_change_commit_mode():
    if state.commit_mode == CommitMode.OVERWRITE:
        ui["commit_mode_button"].set("Commit Mode: Merge")
        state.commit_mode = CommitMode.MERGE
    else:
        ui["commit_mode_button"].set("Commit Mode: Overwrite")
        state.commit_mode = CommitMode.OVERWRITE
    
    set_status(f"Commit mode changed to: {state.commit_mode.value}")

def command_commit():
    if not state.current_project:
        messagebox.showwarning("Warning", "No project opened")
        return
    
    text = ui["input_text"].get("1.0", tk.END).strip()
    
    if not text:
        messagebox.showwarning("Warning", "Input text is empty")
        return
    
    mode = state.commit_mode
    
    if mode != state.last_analyzed_mode:
        messagebox.showinfo(
            "Info",
            "The commit mode has changed since the last analysis. "
            "Please analyze the text again before committing."
        )
        return
    
    try:
        statistics_service.analyze_draft(state.draft, text, state.analyze_options)
        statistics_service.commit(state.current_project, state.draft.current, mode)
        state.preview_stats = deepcopy(state.current_project.stats)
        refresh_result_view()
        set_status(
            f"Commited {mode.value} changes to project: {state.current_project.name}"
        )
    except HNStatisticsError as e:
        messagebox.showerror("Error", str(e))

def command_undo():
    if not state.draft:
        messagebox.showwarning("Warning", "No project opened")
        return
    
    state.draft.undo()
    refresh_result_view()

def command_redo():
    if not state.draft:
        messagebox.showwarning("Warning", "No project opened")
        return
    
    state.draft.redo()
    refresh_result_view()

# ========== UI builders ==========
def build_menu_bar(parent):
    menubar = tk.Menu(parent)
    parent.config(menu=menubar)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    
    file_menu.add_command(label="Create Project", command=command_create_project)
    file_menu.add_command(label="Open Project", command=command_open_project)
    file_menu.add_command(label="Export...", command=on_export_project)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=parent.quit)
    
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    
    edit_menu.add_command(label="Undo", command=command_undo)
    edit_menu.add_command(label="Redo", command=command_redo)
    
    analyze_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Analyze", menu=analyze_menu)
    analyze_menu.add_command(label="Analyze Text", command=command_analyze)

def build_project_panel(parent):
    frame = ttk.Frame(parent, width=220)
    
    ttk.Label(
        frame,
        text = "Projects",
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w", padx=8, pady=(8, 4))
    
    search_var = tk.StringVar()
    search = ttk.Entry(frame, textvariable=search_var)
    search.pack(fill="x", padx=8, pady=4)
    search.bind("<Escape>", on_search_escape)
    
    ui['project_search'] = search_var
    
    search_var.trace_add("write", on_project_search_change)
    
    tree = ttk.Treeview(frame, show="tree")
    tree.pack(fill="both", expand=True, padx=8, pady=4)
    tree.tag_configure(
        "search_match",
        background="#FFF4CC"
    )
    
    tree.bind("<<TreeviewSelect>>", on_project_single_click)
    tree.bind("<Double-Button-1>", on_project_double_click)
    tree.bind("<Button-3>", on_project_right_click)
    tree.bind("<Return>", on_project_enter)
    
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", padx=8, pady=4)
    
    ttk.Button(btn_frame, text="Create", command=command_create_project).pack(fill="x", pady=2)
    ttk.Button(btn_frame, text="Rename", command=command_rename_project).pack(fill="x", pady=2)
    ttk.Button(btn_frame, text="Delete", command=command_delete_project).pack(fill="x", pady=2)
    ttk.Button(btn_frame, text="Export...", command=on_export_project).pack(fill="x", pady=2)

    ui['project_tree'] = tree
    return frame

def build_project_context_menu(parent):
    menu = tk.Menu(parent, tearoff=0)
    
    menu.add_command(label="Open", command=command_open_project)
    menu.add_command(label="Create", command=command_create_project)
    menu.add_separator()
    menu.add_command(label="Rename", command=command_rename_project)
    menu.add_command(label="Delete", command=command_delete_project)
    menu.add_command(label="Export", command=on_export_project)

    ui["project_menu"] = menu

def build_editor_panel(parent):
    frame = ttk.Frame(parent)
    
    ttk.Label(
        frame,
        text="Input Text",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", padx=8, pady=4)
    
    text = tk.Text(frame, height=8)
    text.pack(fill="both", expand=True, padx=8, pady=4)
    
    ui["input_text"] = text
    
    star_var = tk.BooleanVar(value=False)
    
    ttk.Checkbutton(
        frame,
        text="Support  ' * '  operation (e.g., '1 * 3' means '1 1 1')",
        variable=star_var,
        command=on_star_option_change
    ).pack(anchor="w", padx=8, pady=4)
    
    ui['star_option_var'] = star_var
    
    btn_bar = ttk.Frame(frame)
    btn_bar.pack(fill="x", padx=8, pady=4)
    
    ttk.Button(btn_bar, text="Analyze", command=command_analyze).pack(side="right", padx=4)
    ui["commit_mode_button"] = tk.StringVar(value="Commit Mode: Overwrite")
    ttk.Button(btn_bar, textvariable=ui["commit_mode_button"], command=command_change_commit_mode).pack(side="right", padx=4)
    ttk.Button(btn_bar, text="Commit", command=command_commit).pack(side="right", padx=4)
    
    return frame

def build_result_panel(parent):
    frame = ttk.Frame(parent)
    
    ttk.Label(
        frame,
        text="Results",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", padx=8, pady=4)
    tree = ttk.Treeview(
        frame,
        columns=("item", "freq", "prob"),
        show="headings"
    )
    
    tree.heading("item", text="Item", command=lambda: sort_result_tree("item"))
    tree.heading("freq", text="Frequency", command=lambda: sort_result_tree("freq"))
    tree.heading("prob", text="Probability", command=lambda: sort_result_tree("prob"))
    
    tree.pack(fill="both", expand=True, padx=8, pady=4)
    
    ui["result_tree"] = tree
    update_result_tree_headers()
    return frame

def build_status_bar(parent):
    ui['status_bar'] = tk.StringVar(value="HNStatistics - Ready")
    status = ttk.Label(
        parent,
        textvariable=ui['status_bar'],
        relief="sunken",
        anchor="w"
    )
    status.pack(fill="x", side="bottom")

# ========== event handlers ==========
def on_project_enter(event):
    if state.selected_project:
        command_open_project()
    else:
        set_status("No project selected")
        
def on_project_single_click(event):
    tree = ui['project_tree']
    selection = tree.selection()
    
    if not selection:
        state.selected_project = None
        set_status("No project selected")
        return
    
    index = tree.index(selection[0])
    state.selected_project = state.project_list[index]
    set_status(f"Selected project: {state.selected_project.name}")

def on_project_right_click(event):
    tree = ui['project_tree']
    menu = ui["project_menu"]
    
    selection = tree.identify_row(event.y)
    
    if selection:
        tree.selection_set(selection)
        index = tree.index(selection)
        state.selected_project = state.project_list[index]
    else:
        tree.selection_remove(tree.selection())
        state.selected_project = None
    
    has_project = bool(selection)
    menu.entryconfig("Open", state="normal" if has_project else "disabled")
    menu.entryconfig("Rename", state="normal" if has_project else "disabled")
    menu.entryconfig("Delete", state="normal" if has_project else "disabled")
    menu.entryconfig("Export", state="normal" if has_project else "disabled")
    
    menu.post(event.x_root, event.y_root)

def on_project_double_click(event):
    if state.selected_project:
        command_open_project()
    else:
        set_status("No project selected")

def on_project_search_change(*args):
    keyword = ui['project_search'].get().lower()
    
    if not keyword:
        refresh_project_list(state.project_list)
        state.selected_project = None
        set_status("Showing all projects")
        return
    
    filtered = [
        project for project in state.project_list
        if keyword in project.name.lower()
    ]
    
    refresh_project_list(filtered)
    
    if state.selected_project and state.selected_project not in filtered:
        state.selected_project = None
        tree = ui['project_tree']
        tree.selection_remove(tree.selection())
    
    set_status(f"Filtering projects by keyword: '{keyword}'")

def on_search_escape(event):
    var = ui['project_search']
    if not var.get():
        return "break"
    
    var.set("")
    
    tree = ui['project_tree']
    tree.selection_remove(tree.selection())
    state.selected_project = None
    
    tree.focus_set()
    
    set_status("Search cleared")
    return "break"

def on_export_project():
    project = state.current_project
    if project is None:
        messagebox.showwarning("Warning", "Please select a project first.")
        return
    
    file_path = filedialog.asksaveasfilename(
        title="Export Project",
        initialfile=f"{project.name}",
        defaultextension=".xlsx",
        filetypes=[
            ("Excel Files", "*.xlsx"),
            ("CSV Files", "*.csv"),
            ("JSON Files", "*.json"),
            ("All Files", "*.*")
        ]
    )
    
    if not file_path:
        return
    
    try:
        ext = file_path.split('.')[-1].lower()
        export_project(project, file_path, ext)
        messagebox.showinfo("Success", f"Project exported to {file_path}")
        set_status(f"Project exported to {file_path}")
    except HNStatisticsError as e:
        messagebox.showerror("Error", str(e))
        set_status("Export failed")

def on_star_option_change():
    star_var = ui["star_option_var"]
    state.analyze_options.enable_star = star_var.get()
    set_status(f"'*' operation support set to: {state.analyze_options.enable_star}")

def get_selected_index():
    tree = ui['project_tree']
    selection = tree.selection()
    
    if not selection:
        messagebox.showwarning("Warning", "No project selected")
        return None
    
    return tree.index(selection[0])

# ========== app entry ==========
def main():
    init_db()
    
    root = tk.Tk()
    root.title("HNStatistics")
    root.geometry("900x600")
    
    build_menu_bar(root)
    
    h_paned = ttk.PanedWindow(root, orient="horizontal")
    h_paned.pack(fill="both", expand=True)
    
    project_panel = build_project_panel(h_paned)
    h_paned.add(project_panel, weight=1)
    
    v_paned = ttk.PanedWindow(h_paned, orient="vertical")
    h_paned.add(v_paned, weight=4)
    
    editor_panel = build_editor_panel(v_paned)
    result_panel = build_result_panel(v_paned)
    
    v_paned.add(editor_panel, weight=2)
    v_paned.add(result_panel, weight=3)
    
    build_project_context_menu(root)
    build_status_bar(root)
    
    refresh_project_list()
    
    root.mainloop()

if __name__ == "__main__":
    main()