This is my Software Engineering Year 12 Assessment Task 3, all relevant files are attached.

File naming scheme:
[D] = DATA
[C] = CODE
[S] = SUPPORTING FILES

STUDENT MARK ESTIMATOR - INSTALLATION & USAGE INSTRUCTIONS
=============================================================

REQUIRED DEPENDENCIES:
----------------------
Before running the application, you need to install the following Python packages:

1. pandas - For CSV file handling and data manipulation
2. scikit-learn - For machine learning (Linear Regression)
3. tkinterdnd2 - For drag and drop functionality

INSTALLATION:
-------------
Run the following command in your terminal/command prompt:

    pip install pandas scikit-learn tkinterdnd2

Or install them one by one:

    pip install pandas
    pip install scikit-learn
    pip install tkinterdnd2


RUNNING THE APPLICATION:
------------------------
Once dependencies are installed, run:

    python mark-estimator-app.py


FEATURES:
---------
✓ Dark/Light theme toggle
✓ Browse for CSV files OR drag & drop CSV files directly onto the window
✓ Automatically detects missing student marks
✓ Run individual estimations by selecting from the list
✓ Run ALL estimations at once with the "Run All Estimations" button
✓ Machine Learning predictions using Linear Regression
✓ Exports results to a new CSV file (prefixed with "estimated_")
✓ Open exported files directly in Notepad/TextEdit


HOW TO USE:
-----------
1. Load a CSV file by either:
   - Clicking "Browse CSV File" button, OR
   - Dragging and dropping a CSV file onto the window

2. The application will automatically scan for missing marks

3. Choose to either:
   - Select a specific missing mark from the list and click "Run ML Estimation"
   - Click "Run All Estimations" to process all missing marks at once

4. View results in the log panel at the bottom

5. Click "Open in Notepad / Text Editor" to view the exported file


CSV FILE FORMAT:
----------------
Your CSV should have:
- First column: Student ID (or any unique identifier)
- Remaining columns: Assessment/test scores

Example:
StudentID, Test1, Test2, Test3, FinalExam
12345,    85,    90,    ,       88
12346,    78,    ,      82,
12347,    92,    88,    91,     95

Missing values will be automatically detected and can be estimated.


TROUBLESHOOTING:
----------------
- If you get "module not found" errors, make sure all dependencies are installed
- If drag & drop doesn't work, ensure tkinterdnd2 is properly installed
- CSV files must have at least 2 columns (ID + at least one assessment)
- For ML to work, you need at least 2 complete rows of data


SUPPORT:
--------
For issues or questions, check that:
1. Python 3.x is installed
2. All dependencies are up to date
3. Your CSV file follows the correct format
