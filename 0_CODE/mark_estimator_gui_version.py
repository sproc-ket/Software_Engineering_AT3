import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from sklearn.linear_model import LinearRegression
from tkinterdnd2 import DND_FILES, TkinterDnD

class MarkEstimatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Mark Estimator System")
        self.root.geometry("750x660")
        self.root.minsize(700, 580)

        self.df = None
        self.file_path = None
        self.last_exported_file = None
        self.saved_file_path = None
        self.has_unsaved_results = False
        self.id_col = None
        self.assessment_cols = []
        self.missing_records = []

        self.is_dark_mode = True

        self.style = ttk.Style()
        self.style.theme_use("default")

        self._create_widgets()
        self._update_theme_styles()

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def _update_theme_styles(self):
        if self.is_dark_mode:
            self.bg_color = "#1E1E1E"
            self.card_bg = "#2D2D2D"
            self.fg_color = "#E0E0E0"
            self.accent_color = "#007ACC"
            self.btn_bg = "#3E3E3E"
            self.btn_active = "#4E4E4E"
            self.disabled_bg = "#252526"
            self.disabled_fg = "#7C7C7C"
            self.status_text = "#4FC1FF"
            self.theme_btn_text = "Switch to Light Mode"
        else:
            self.bg_color = "#F5F5F5"
            self.card_bg = "#FFFFFF"
            self.fg_color = "#202020"
            self.accent_color = "#005FB8"
            self.btn_bg = "#E1E1E1"
            self.btn_active = "#D0D0D0"
            self.disabled_bg = "#EAEAEA"
            self.disabled_fg = "#A0A0A0"
            self.status_text = "#008000"
            self.theme_btn_text = "Switch to Dark Mode"

        self.root.configure(bg=self.bg_color)

        self.style.configure(".", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLable", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)

        self.style.configure(
            "TLabelframe",
            background=self.bg_color,
            foreground=self.fg_color,
            bordercolor=self.card_bg,
            borderwidth=1,
        )
        self.style.configure(
            "TLabelframe.Label",
            background=self.bg_color,
            foreground=self.accent_color,
            font=("Arial", 10, "bold"),
        )

        self.style.configure(
            "TButton",
            background=self.btn_bg,
            foreground=self.fg_color,
            bordercolor=self.bg_color,
            borderwidth=1,
            focusthickness=0,
            padding=6,
            font=("Arial", 9, "bold"),
        )
        self.style.map(
            "TButton",
            background=[("active", self.btn_active), ("disabled", self.disabled_bg)],
            foreground=[("disabled", self.disabled_fg)],
        )

        self.style.configure(
            "TScrollbar",
            background=self.btn_bg,
            troughcolor=self.bg_color,
            bordercolor=self.bg_color,
            arrowcolor=self.fg_color,
        )

        self.listbox_missing.configure(
            bg=self.card_bg,
            fg=self.fg_color,
            selectbackground=self.accent_color,
            selectforeground=(self.card_bg if not self.is_dark_mode else self.fg_color),
            highlightbackground=self.bg_color,
        )

        self.txt_output.config(state=tk.NORMAL)
        self.txt_output.configure(
            bg=self.card_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            highlightbackground=self.bg_color,
        )
        self.txt_output.config(state=tk.DISABLED)

        self.btn_theme_toggle.config(text=self.theme_btn_text)

        if self.df is not None:
            self.lbl_file_status.config(foreground=self.status_text)
        else:
            self.lbl_file_status.config(foreground=self.disabled_fg)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self._update_theme_styles()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_utility_frame = ttk.Frame(main_frame)
        top_utility_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_theme_toggle = ttk.Button(
            top_utility_frame, text="", command=self.toggle_theme
        )
        self.btn_theme_toggle.pack(side=tk.RIGHT)

        file_frame = ttk.LabelFrame(main_frame, text=" 1. Load Dataset (Browse or Drag & Drop CSV) ", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_browse = ttk.Button(
            file_frame, text="Browse CSV File", command=self.load_csv
        )
        self.btn_browse.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_file_status = ttk.Label(
            file_frame, text="No file loaded.", font=("Arial", 9, "italic")
        )
        self.lbl_file_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        list_frame = ttk.LabelFrame(
            main_frame, text=" 2. Select Missing Mark to Estimate ", padding="10"
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)

        self.listbox_missing = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            selectmode=tk.SINGLE,
            borderwidth=1,
            relief=tk.FLAT,
            highlightthickness=1,
        )
        scrollbar.config(command=self.listbox_missing.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_missing.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        action_frame = ttk.Frame(main_frame, padding="5")
        action_frame.pack(fill=tk.X, pady=10)

        btn_grid = ttk.Frame(action_frame)
        btn_grid.pack(fill=tk.X)

        self.btn_estimate = ttk.Button(
            btn_grid,
            text="Run ML Estimation",
            command=self.process_estimation,
            state=tk.DISABLED,
        )
        self.btn_estimate.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_run_all = ttk.Button(
            btn_grid,
            text="Run All Estimations",
            command=self.process_all_estimations,
            state=tk.DISABLED,
        )
        self.btn_run_all.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_save = ttk.Button(
            btn_grid,
            text="Save Results",
            command=self.save_results,
            state=tk.DISABLED,
        )
        self.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_save_as = ttk.Button(
            btn_grid,
            text="Save As...",
            command=self.save_results_as,
            state=tk.DISABLED,
        )
        self.btn_save_as.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_open_file = ttk.Button(
            btn_grid,
            text="Open in Spreadsheet / Text Editor",
            command=self.open_exported_file,
            state=tk.DISABLED,
        )
        self.btn_open_file.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        result_frame = ttk.LabelFrame(
            main_frame, text=" 3. Estimation Results & Logs ", padding="10"
        )
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.txt_output = tk.Text(
            result_frame,
            height=8,
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            borderwidth=1,
            relief=tk.FLAT,
            highlightthickness=1,
        )
        self.txt_output.pack(fill=tk.BOTH, expand=True)

    def log_message(self, message, clear=False):
        self.txt_output.config(state=tk.NORMAL)
        if clear:
            self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, message + "\n")
        self.txt_output.config(state=tk.DISABLED)

    def load_csv(self):
        selected_file = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if not selected_file:
            return

        self._load_csv_from_path(selected_file)

    def handle_drop(self, event):
        file_path = event.data.strip('{}')

        if not file_path.lower().endswith('.csv'):
            messagebox.showwarning(
                "Invalid File Type",
                "Please drop a CSV file (.csv extension required)."
            )
            return

        self._load_csv_from_path(file_path)

    def _load_csv_from_path(self, selected_file):
        try:
            temp_df = pd.read_csv(selected_file)

            if temp_df.empty:
                messagebox.showerror("Error", "The chosen CSV file is empty.")
                return
            if len(temp_df.columns) < 2:
                messagebox.showerror(
                    "Error",
                    "CSV must contain at least a Student Identifier and one assessment column.",
                )
                return

            self.df = temp_df
            self.file_path = selected_file
            self.id_col = self.df.columns[0]
            self.assessment_cols = list(self.df.columns[1:])

            self.last_exported_file = None
            self.btn_open_file.config(state=tk.DISABLED)

            self.lbl_file_status.config(
                text=os.path.basename(selected_file),
                font=("Arial", 9, "bold"),
            )
            self._update_theme_styles()

            self.log_message(
                f"Success: Loaded file successfully: {os.path.basename(selected_file)}",
                clear=True,
            )

            self.scan_for_missing_data()
            self.saved_file_path = None
            self.last_exported_file = None
            self.has_unsaved_results = False
            self.btn_save.config(state=tk.DISABLED)
            self.btn_save_as.config(state=tk.DISABLED)
            self.btn_open_file.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror(
                "File Read Error", f"Could not open or parse file:\n{str(e)}"
            )

    def scan_for_missing_data(self):
        self.listbox_missing.delete(0, tk.END)
        self.missing_records = []

        missing_mask = self.df[self.assessment_cols].isna().any(axis=1)
        missing_df = self.df[missing_mask]

        if missing_df.empty:
            self.log_message(
                "Success: No missing grades found in this dataset."
            )
            self.btn_estimate.config(state=tk.DISABLED)
            self.btn_run_all.config(state=tk.DISABLED)
            if self.has_unsaved_results:
                self.btn_save.config(state=tk.NORMAL)
                self.btn_save_as.config(state=tk.NORMAL)
            else:
                self.btn_save.config(state=tk.DISABLED)
                self.btn_save_as.config(state=tk.DISABLED)
            self.btn_open_file.config(state=tk.NORMAL if self.last_exported_file else tk.DISABLED)
            return

        for _, row in missing_df.iterrows():
            student_id = row[self.id_col]
            for col in self.assessment_cols:
                if pd.isna(row[col]):
                    display_str = f"Student ID: {str(student_id):<12} | Missing Task: {col}"
                    self.listbox_missing.insert(tk.END, display_str)
                    self.missing_records.append(
                        {"id": student_id, "column": col}
                    )

        self.btn_estimate.config(state=tk.NORMAL)
        self.btn_run_all.config(state=tk.NORMAL)
        if self.has_unsaved_results:
            self.btn_save.config(state=tk.NORMAL)
            self.btn_save_as.config(state=tk.NORMAL)
        else:
            self.btn_save.config(state=tk.DISABLED)
            self.btn_save_as.config(state=tk.DISABLED)
        self.btn_open_file.config(state=tk.NORMAL if self.last_exported_file else tk.DISABLED)
        self.log_message(
            f"Found {len(self.missing_records)} missing item(s). Highlight one above to process, or click 'Run All Estimations'."
        )

    def process_estimation(self):
        selection = self.listbox_missing.curselection()
        if not selection:
            messagebox.showwarning(
                "Selection Required",
                "Please click and select a specific row item from the list box above.",
            )
            return

        selected_index = selection[0]
        target_info = self.missing_records[selected_index]
        target_id = target_info["id"]
        target_col = target_info["column"]

        predicted_mark, metrics = self.predict_mark(target_id, target_col)

        self.log_message("", clear=True)
        self.log_message("=========================================")
        self.log_message("           ESTIMATION OUTPUT             ")
        self.log_message("=========================================")
        self.log_message(f"Student Target ID : {target_id}")
        self.log_message(f"Assessment Column : {target_col}")
        self.log_message(f"Estimated Mark    : {predicted_mark}")
        self.log_message("-----------------------------------------")
        self.log_message("Supporting Context Baseline Calculations:")
        for k, v in metrics.items():
            self.log_message(f" - {k}: {v}")
        self.log_message("=========================================")

        self.btn_save.config(state=tk.NORMAL)
        self.btn_save_as.config(state=tk.NORMAL)
        self.has_unsaved_results = True
        self.btn_open_file.config(state=tk.DISABLED)
        self.saved_file_path = None

    def process_all_estimations(self):
        if not self.missing_records:
            messagebox.showwarning(
                "No Missing Data",
                "There are no missing marks to estimate."
            )
            return

        total_count = len(self.missing_records)

        self.log_message("", clear=True)
        self.log_message("=" * 60)
        self.log_message("           BATCH ESTIMATION - RUN ALL")
        self.log_message("=" * 60)
        self.log_message(f"Processing {total_count} missing mark(s)...\n")

        estimation_results = []

        for idx, target_info in enumerate(self.missing_records, 1):
            target_id = target_info["id"]
            target_col = target_info["column"]

            self.log_message(f"[{idx}/{total_count}] Processing: Student {target_id}, Column {target_col}")

            predicted_mark, metrics = self.predict_mark(target_id, target_col)

            self.df.loc[self.df[self.id_col] == target_id, target_col] = predicted_mark

            estimation_results.append({
                "student_id": target_id,
                "column": target_col,
                "estimated_mark": predicted_mark
            })

            self.log_message(f"    -> Estimated Mark: {predicted_mark}\n")

        self.btn_save.config(state=tk.NORMAL)
        self.btn_save_as.config(state=tk.NORMAL)
        self.has_unsaved_results = True
        self.btn_open_file.config(state=tk.DISABLED)
        self.saved_file_path = None

        self.log_message("=" * 60)
        self.log_message("           BATCH ESTIMATION COMPLETE")
        self.log_message("=" * 60)
        self.log_message(f"Total marks estimated: {total_count}")
        self.log_message("=" * 60)
        self.log_message("Please use Save or Save As to write the results to a CSV file.")
        self.scan_for_missing_data()

    def predict_mark(self, target_id, target_col):
        feature_cols = [c for c in self.assessment_cols if c != target_col]

        if not feature_cols:
            historical_avg = round(self.df[target_col].mean(), 1)
            return historical_avg, {"Fallback Route": "Global Class Column Mean"}

        train_data = self.df.dropna(subset=[target_col] + feature_cols)

        if len(train_data) < 2:
            historical_avg = round(self.df[target_col].mean(), 1)
            return historical_avg, {
                "Fallback Route": "Global Class Mean (Insufficient complete rows for ML)"
            }

        target_row = self.df[self.df[self.id_col] == target_id].iloc[0]

        if target_row[feature_cols].isna().any():
            student_avg = round(target_row[feature_cols].mean(), 1)
            return student_avg, {
                "Fallback Route": "Student Row Mean (Multiple missing marks)"
            }

        X_train = train_data[feature_cols]
        y_train = train_data[target_col]

        X_predict = pd.DataFrame([target_row[feature_cols]])

        model = LinearRegression()
        model.fit(X_train, y_train)

        raw_pred = model.predict(X_predict)

        final_pred = round(max(0.0, min(100.0, raw_pred[0])), 1)

        metrics = {
            f"Class Baseline Mean for {target_col}": round(
                self.df[target_col].mean(), 2
            ),
            "Target Student Mean on other tests": round(
                target_row[feature_cols].mean(), 2
            ),
            "Robust Sample Sizes Used for Training": len(train_data),
        }

        return final_pred, metrics

    def _choose_export_path(self, default_name):
        return filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=default_name,
            title="Save estimated results as...",
        )

    def _project_root(self):
        """Return the repository root based on this source file location.

        Falls back to current working directory if __file__ is unavailable.
        """
        try:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        except Exception:
            return os.getcwd()

    def _save_to_path(self, output_path):
        try:
            self.df.to_csv(output_path, index=False)
            self.last_exported_file = output_path
            self.saved_file_path = output_path
            self.btn_open_file.config(state=tk.NORMAL)
            self.log_message(f"Results saved to: {output_path}")
            messagebox.showinfo(
                "Save Successful",
                f"Estimated results saved to:\n\n{output_path}"
            )
            return True
        except Exception as e:
            messagebox.showerror(
                "Save Failure",
                f"Could not save results:\n{str(e)}"
            )
            return False

    def save_results(self):
        if self.df is None:
            messagebox.showwarning(
                "No Data",
                "Load a CSV and run an estimation before saving."
            )
            return

        if self.saved_file_path:
            if self._save_to_path(self.saved_file_path):
                self.has_unsaved_results = False
            return

        try:
            dir_name, file_name = os.path.split(self.file_path)
            project_root = self._project_root()
            default_name = f"estimated_{file_name}"
            output_path = os.path.join(project_root, default_name)
        except Exception:
            output_path = self._choose_export_path(f"estimated_{os.path.basename(self.file_path) if self.file_path else 'results.csv'}")

        if not output_path:
            self.log_message("Save cancelled by user.")
            return

        if self._save_to_path(output_path):
            self.has_unsaved_results = False

    def save_results_as(self):
        if self.df is None:
            messagebox.showwarning(
                "No Data",
                "Load a CSV and run an estimation before saving."
            )
            return

        dir_name, file_name = os.path.split(self.file_path)
        output_path = self._choose_export_path(f"estimated_{file_name}")
        if not output_path:
            self.log_message("Save As cancelled by user.")
            return
        if self._save_to_path(output_path):
            self.has_unsaved_results = False

    def export_results(self, target_id, target_col, predicted_mark):
        self.df.loc[self.df[self.id_col] == target_id, target_col] = (
            predicted_mark
        )

        dir_name, file_name = os.path.split(self.file_path)
        output_path = self._choose_export_path(f"estimated_{file_name}")
        if not output_path:
            self.log_message("Export cancelled by user.")
            return

        try:
            self.df.to_csv(output_path, index=False)

            self.last_exported_file = output_path
            self.btn_open_file.config(state=tk.NORMAL)

            self.log_message(f"\nDocument updated file exported to:\n -> {output_path}")
            messagebox.showinfo(
                "Export Success",
                f"Successfully calculated results!\nFile written out to:\n\n{output_path}\n\nYou can now open it in your editor below.",
            )

            self.scan_for_missing_data()
        except Exception as e:
            messagebox.showerror(
                "Export Failure Error",
                f"Could not print output onto hard disk storage systems:\n{str(e)}",
            )

    def open_exported_file(self):
        if not self.last_exported_file or not os.path.exists(self.last_exported_file):
            messagebox.showerror("Error", "The estimated file could not be found.")
            return

        try:
            if sys.platform == "win32":
                subprocess.Popen(["notepad.exe", self.last_exported_file])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", "TextEdit", self.last_exported_file])
            else:
                subprocess.Popen(["xdg-open", self.last_exported_file])

            self.log_message(f"Opened file in editor: {os.path.basename(self.last_exported_file)}")
        except Exception as e:
            messagebox.showerror(
                "Open Failed",
                f"Could not open editor automatically:\n{str(e)}\n\nYou can find it at:\n{self.last_exported_file}"
            )

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = MarkEstimatorApp(root)
    root.mainloop()
