import os
import sys
import pandas as pd
from sklearn.linear_model import LinearRegression

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_csv():
    """Prompts user for a CSV file and validates its existence and content."""
    while True:
        file_path = input("Enter the path to the student CSV file (or 'q' to quit): ").strip()
        if file_path.lower() == 'q':
            print("Exiting the program.")
            sys.exit("Application terminated by user.")
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found. Please try again.")
            continue

        try:
            df = pd.read_csv(file_path)
            if df.empty:
                print("Error: The CSV file is empty.")
                continue
            
            if len(df.columns) < 2:
                print("Error: CSV must have an identifier column (e.g., Student_ID) and at least one assessment column.")
                continue
                
            return df, file_path
        except Exception as e:
            print(f"Error reading file: {e}")

def display_missing_data(df):
    """Identifies and displays rows with missing assessment marks."""
    id_col = df.columns[0]
    assessment_cols = df.columns[1:]
    
    missing_mask = df[assessment_cols].isna().any(axis=1)
    missing_df = df[missing_mask]

    if missing_df.empty:
        print("No missing assessment marks found in this dataset!")
        sys.exit(0)
    
    print("\n--- Students with Missing Marks ---")
    print(missing_df[[id_col] + list(assessment_cols)].to_string(index=False))
    return missing_df, id_col, list(assessment_cols)

def select_target_mark(missing_df, assessment_cols):
    """Allows the user to select which specific missing value to estimate."""
    print("\n--- Select Missing Mark to Estimate ---")
    
    # Filter out combinations that actually have missing data
    available_targets = []
    id_col = missing_df.columns[0]
    
    for _, row in missing_df.iterrows():
        for col in assessment_cols:
            if pd.isna(row[col]):
                available_targets.append((row[id_col], col))
    
    for idx, (student_id, col_name) in enumerate(available_targets, 1):
        print(f"{idx}. Student ID: {student_id} | Missing Assessment: {col_name}")
        
    while True:
        try:
            choice = input(f"\nEnter selection number (1-{len(available_targets)}): ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_targets):
                return available_targets[choice_idx]
            print(f"Invalid selection. Please choose a number between 1 and {len(available_targets)}.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def predict_missing_mark(df, target_student_id, target_column, id_col, assessment_cols):
    """Predicts the missing mark using Linear Regression based on other assessments."""
    # Features (X) are all assessment columns except the target column
    feature_cols = [col for col in assessment_cols if col != target_column]

    if not feature_cols:
        # Fallback if there is only 1 assessment column total (ML requires features)
        print("Not enough assessment columns for ML prediction. Falling back to historical column average.")
        historical_avg = df[target_column].mean()
        return round(historical_avg, 1), {"Fallback Method": "Column Mean"}

    # Complete data for training (drop any row that has NaN in our selected features or target)
    train_data = df.dropna(subset=[target_column] + feature_cols)

    if len(train_data) < 2:
        # Fallback if there aren't enough rows to train an ML model
        print("Insufficient complete rows for Machine Learning. Falling back to historical column average.")
        historical_avg = df[target_column].mean()
        return round(historical_avg, 1), {"Fallback Method": "Column Mean"}
    
    X_train = train_data[feature_cols]
    y_train = train_data[target_column]

    # Target row to predict
    target_row = df[df[id_col] == target_student_id]

    if target_row[feature_cols].isna().any().any():
        print(f"Error: Student {target_student_id} has multiple missing marks. Cannot use ML.")
        print("Falling back to the student's available assessment average.")
        student_avg = target_row[feature_cols].mean(axis=1).values[0]
        return round(student_avg, 1), {"Fallback Method": "Student Average"}
    
    X_predict = target_row[feature_cols]
    
    # Train Linear Regression Model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Predict
    predicted_value = model.predict(X_predict)[0]
    # Bound the mark between 0 and 100 assuming standard marking scales
    predicted_value = max(0.0, min(100.0, predicted_value))
    
    # Generate supporting information metrics
    supporting_info = {
        f"Historical Class Average for {target_column}": round(df[target_column].mean(), 2),
        f"Target Student's Average in other tasks": round(X_predict.mean(axis=1).values[0], 2),
        "Training Sample Size (Rows Used)": len(train_data)
    }
    
    return round(predicted_value, 1), supporting_info

def export_updated_csv(df, target_student_id, target_column, id_col, predicted_mark, original_path):
    """Updates the dataframe and exports it to a new file to preserve the original dataset."""
    # Update value in dataframe
    df.loc[df[id_col] == target_student_id, target_column] = predicted_mark
    
    # Generate output path
    dir_name, file_name = os.path.split(original_path)
    new_file_name = "estimated_" + file_name
    export_path = os.path.join(dir_name, new_file_name)
    
    try:
        df.to_csv(export_path, index=False)
        print(f"\nSuccess! Updated dataset exported to: {export_path}")
    except Exception as e:
        print(f"❌ Export failed: {e}")


def main():
    clear_screen()
    print("=========================================")
    print("      STUDENT MARK ESTIMATOR SYSTEM      ")
    print("=========================================\n")
    
    # 1. Read & Validate CSV Input
    df, file_path = load_csv()
    
    # 2. Identify Missing Marks
    missing_df, id_col, assessment_cols = display_missing_data(df)
    
    # 3. User Selects the Target to Estimate
    target_student_id, target_column = select_target_mark(missing_df, assessment_cols)
    
    # 4. Predict the Missing Mark using ML
    predicted_mark, supporting_info = predict_missing_mark(df, target_student_id, target_column, id_col, assessment_cols)

     # 5. Display Supporting Information
    print("\n=========================================")
    print("           ESTIMATION RESULTS            ")
    print("=========================================")
    print(f"Target Student : {target_student_id}")
    print(f"Assessment     : {target_column}")
    print(f"Predicted Mark : {predicted_mark}")
    print("-----------------------------------------")
    print("Supporting Data:")
    for key, value in supporting_info.items():
        print(f" • {key}: {value}")
    print("=========================================")

    # 6. Export to a new CSV file
    export_updated_csv(df, target_student_id, target_column, id_col, predicted_mark, file_path)

if __name__ == "__main__":
    main()