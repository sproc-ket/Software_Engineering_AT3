import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from sklearn.linear_model import LinearRegression


class MarkEstimatorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Student Mark Estimator System")
        self.root.geometry("750x750")
        self.root.minsize(750, 750)

        # Application State
        self.df = None
        self.file_path = None
        self.last_exported_file = None  # Tracks the most recently saved file path
        self.id_col = None
        self.assessment_cols = []
        self.missing_records = []

        self._setup_dark_theme()
        self._create_widgets()
    
    def _setup_dark_theme(self):
        """Defines and applies a cohesive dark-palette configuration across all UI objects."""
        # Color Palette Variables
        self.bg_color = "#1E1E1E"        # Dark Gray background
        self.card_bg = "#2D2D2D"         # Slightly lighter gray for sections
        self.fg_color = "#E0E0E0"        # Crisp light text
        self.accent_color = "#007ACC"    # Blue accents for selections and boundaries
        self.btn_bg = "#3E3E3E"          # Button base surface color
        self.btn_active = "#4E4E4E"      # Button hover state surface color
        self.green_text = "#4FC1FF"      # Electric blue/green variant for success indicators

        # Apply global container window background configurations
        self.root.configure(bg=self.bg_color)

        # Configure TTK Styles Matrix mappings
        self.style = ttk.Style()
        self.style.theme_use("default")

        # Global Frame Configurations
        self.style.configure(".", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TFrame", background=self.bg_color)

        # LabelFrame Section Box Containers
        self.style.configure("TLable", background=self.bg_color, foreground=self.fg_color)
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

        # Labels Matrix mapping
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)

        # Custom Button System Implementations
        self.style.configure(
            "TButton",
            background=self.btn_bg,
            foreground=self.fg_color,
            bordercolor=self.bg_color,
            borderwidth=1,
            focusthickness=0,
            focuscolor=self.accent_color,
            padding=6,
            font=("Arial", 9, "bold"),
        )
        self.style.map(
            "TButton",
            background=[("active", self.btn_active), ("disabled", "#252526")],
            foreground=[("disabled", "#7C7C7C")],
        )

        # Scrollbars tracking configuration elements
        self.style.configure(
            "TScrollbar",
            gripcount=0,
            background=self.btn_bg,
            troughcolor=self.bg_color,
            bordercolor=self.bg_color,
            lightcolor=self.bg_color,
            darkcolor=self.bg_color,
            arrowcolor=self.fg_color,
        )

    def _create_widgets(self):
        """Builds the layout structures using Tkinter frames and themes."""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- File Selection ---
        file_frame = ttk.LabelFrame(main_frame, text=" 1. Load Dataset ", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_browse = ttk.Button(
            file_frame, text="Browse CSV File", command=self.load_csv
        )
        self.btn_browse.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_file_status = ttk.Label(
            file_frame,
            text="No file loaded.",
            font=("Arial", 9, "italic"),
            foreground="gray",
        )
        self.lbl_file_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Missing Data Selection ---
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
        )
        scrollbar.config(command=self.listbox_missing.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_missing.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Actions ---
        action_frame = ttk.Frame(main_frame, padding="5")
        action_frame.pack(fill=tk.X, pady=10)

        # Horizontal sub-layout for buttons
        btn_grid = ttk.Frame(action_frame)
        btn_grid.pack(fill=tk.X)

        self.btn_estimate = ttk.Button(
            btn_grid,
            text="Run ML Estimation",
            command=self.process_estimation,
            state=tk.DISABLED,
        )
        self.btn_estimate.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # NEW: Open file button (initially hidden/disabled until an export happens)
        self.btn_open_file = ttk.Button(
            btn_grid,
            text="Open Estimated File",
            command=self.open_exported_file,
            state=tk.DISABLED,
        )
        self.btn_open_file.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # --- Output Log ---
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
        )
        self.txt_output.pack(fill=tk.BOTH, expand=True)

    def log_message(self, message, clear=False):
        """Inserts system status feedback messages into the console Text Box."""
        self.txt_output.config(state=tk.NORMAL)
        if clear:
            self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, message + "\n")
        self.txt_output.config(state=tk.DISABLED)

    def load_csv(self):
        """Opens file dialog window, handles validation checks, and screens input file."""
        selected_file = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if not selected_file:
            return

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

            # Reset file tracker state when loading a completely new original file
            self.last_exported_file = None
            self.btn_open_file.config(state=tk.DISABLED)

            self.lbl_file_status.config(
                text=os.path.basename(selected_file),
                foreground="green",
                font=("Arial", 9, "bold"),
            )
            self.log_message(
                f"Loaded file successfully: {os.path.basename(selected_file)}",
                clear=True,
            )

            self.scan_for_missing_data()

        except Exception as e:
            messagebox.showerror(
                "File Read Error", f"Could not open or parse file:\n{str(e)}"
            )

    def scan_for_missing_data(self):
        """Scans loaded matrix structures tracking rows containing missing empty cells."""
        self.listbox_missing.delete(0, tk.END)
        self.missing_records = []

        missing_mask = self.df[self.assessment_cols].isna().any(axis=1)
        missing_df = self.df[missing_mask]

        if missing_df.empty:
            self.log_message(
                "No missing grades found in this dataset."
            )
            self.btn_estimate.config(state=tk.DISABLED)
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
        self.log_message(
            f"Found {len(self.missing_records)} missing item(s). Highlight one above to process."
        )

    def process_estimation(self):
        """Triggers ML core modeling logic, formats execution feedback prints, saves files."""
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
            self.log_message(f" • {k}: {v}")
        self.log_message("=========================================")

        self.export_results(target_id, target_col, predicted_mark)

    def predict_mark(self, target_id, target_col):
        """Core ML execution framework mapping data subsets and training regressions models."""
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

        target_row = self.df[self.df[self.id_col] == target_id]

        if target_row[feature_cols].isna().any().any():
            student_avg = round(target_row[feature_cols].mean(axis=1).values[0], 1)
            return student_avg, {
                "Fallback Route": "Student Row Mean (Multiple missing marks)"
            }

        X_train = train_data[feature_cols]
        y_train = train_data[target_col]
        X_predict = target_row[feature_cols]

        model = LinearRegression()
        model.fit(X_train, y_train)

        raw_pred = model.predict(X_predict)[0]
        final_pred = round(max(0.0, min(100.0, raw_pred)), 1)

        metrics = {
            f"Class Baseline Mean for {target_col}": round(
                self.df[target_col].mean(), 2
            ),
            "Target Student Mean on other tests": round(
                X_predict.mean(axis=1).values[0], 2
            ),
            "Robust Sample Sizes Used for Training": len(train_data),
        }

        return final_pred, metrics

    def export_results(self, target_id, target_col, predicted_mark):
        """Saves values into memory frames, and generates new external document exports safely."""
        self.df.loc[self.df[self.id_col] == target_id, target_col] = (
            predicted_mark
        )

        dir_name, file_name = os.path.split(self.file_path)
        output_path = os.path.join(dir_name, f"estimated_{file_name}")

        try:
            self.df.to_csv(output_path, index=False)
            
            # Save reference and enable the open file button widget
            self.last_exported_file = output_path
            self.btn_open_file.config(state=tk.NORMAL)
            
            self.log_message(f"\nDocument updated file exported to:\n -> {output_path}")
            messagebox.showinfo(
                "Export Success",
                f"Successfully calculated results!\nFile written out to:\n\n{output_path}\n\nYou can now open it using the button below.",
            )

            self.scan_for_missing_data()
        except Exception as e:
            messagebox.showerror(
                "Export Failure Error",
                f"Could not print output onto hard disk storage systems:\n{str(e)}",
            )

    def open_exported_file(self):
        """NEW FEATURE: Cross-platform utility that natively opens the generated file."""
        if not self.last_exported_file or not os.path.exists(self.last_exported_file):
            messagebox.showerror("Error", "The estimated file could not be found.")
            return

        try:
            # Handles opening files natively across Windows, MacOS, and Linux environments
            if sys.platform == "win32":
                subprocess.Popen(["notepad.exe", self.last_exported_file])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.last_exported_file])
            else:
                subprocess.Popen(["xdg-open", self.last_exported_file])
                
            self.log_message(f"Triggered native OS request to open: {os.path.basename(self.last_exported_file)}")
        except Exception as e:
            messagebox.showerror(
                "Open Failed", 
                f"Your OS could not open this file automatically:\n{str(e)}\n\nYou can find it at:\n{self.last_exported_file}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkEstimatorApp(root)
    root.mainloop()
