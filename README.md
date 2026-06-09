This is my Software Engineering Year 12 Assessment Task 3, all relevant files are attached.

STUDENT MARK ESTIMATOR - INSTALLATION & USAGE INSTRUCTIONS
===========================================================

THERE ARE 2 OPTIONS FOR RUNNING THIS PROGRAM, READ THIS
========================================================

OPTION 1: run MarkEstimatorApp.exe directly from \dist\MarkEstimatorApp\MarkEstimatorApp.exe which will load it without any other action on your part

OR

OPTION 2: run the app through an IDE such as Visual Studio Code. Instructions for manual installation are below:

-------------------------------------------------------------------------------------------------

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

OR install them one by one:

    pip install pandas
    pip install scikit-learn
    pip install tkinterdnd2


RUNNING THE APPLICATION:
------------------------
Once dependencies are installed, run:
    mark_estimator_experimental.py


FEATURES:
---------
- Dark/Light theme toggle
- Browse for CSV files OR drag & drop CSV files directly onto the window
- Automatically detects missing student marks
- Run individual estimations by selecting from the list
- Run ALL estimations at once with the "Run All Estimations" button
- Machine Learning predictions using Linear Regression
- Exports results to a new CSV file (prefixed with "estimated_")
- Open exported files directly in Notepad/TextEdit


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


HOW IT WORKS
------------
Supporting metrics:
- Class Baseline Mean - Average score for that assessment across all students
- Target Student Mean - The student's average on OTHER tests
- Training Sample Size - How many complete student records were used to train the model


Fallback Strategies (When ML Won't Work)
----------------------------------------
The program has 3 fallback routes for edge cases:

- Fallback 1: Only One Assessment Column
  If there's only 1 column total (e.g., just "FinalExam"), you can't use other marks to predict.

  Solution: Returns the class average for that column.


- Fallback 2: Not Enough Training Data
  If fewer than 2 students have complete data, Linear Regression can't train.

  Solution: Returns the class average for that column.


- Fallback 3: Student Missing Multiple Marks
  If the student is missing marks in OTHER columns too (e.g., missing both Test2 AND Test3), you can't use their Test2 score to predict Test3.

Solution: Returns the student's personal average from their available marks.




In Simple Terms:
The program asks: "Based on how other students performed across ALL their tests, and knowing THIS student's pattern on their other tests, what would we expect them to score on the missing test?"

It's like saying: "Student A scored 80-85 on everything else, and students who score in that range typically get around 82 on Test3, so let's predict 82 for Student A's missing Test3 mark."