import os
import pandas as pd

def load_csv(folder_name, file_name):
    """
    Reads a CSV file from a specified folder and returns a DataFrame.

    Parameters:
        folder_name (str): Name of the folder containing the CSV file.
        file_name (str): Name of the CSV file, must end with .csv extension.

    Returns:
        pd.DataFrame: A DataFrame containing the contents of the CSV file.

    Raises:
        ValueError: If file_name does not end with .csv extension.
        FileNotFoundError: If folder does not exist or file does not exist in the specified folder.
    """
    try:
        if not file_name.endswith('.csv'):
            raise ValueError("File name must end with '.csv' extension")
        
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        folder_path = os.path.join(parent_dir, folder_name)
        file_path = os.path.join(folder_path, file_name)

        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder '{folder_name}' does not exists")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File '{file_name}' not found in folder '{folder_name}'")

        df = pd.read_csv(file_path)
        return df
    
    except (FileNotFoundError, ValueError) as e:
        print(e)
        return pd.DataFrame()
    
def load_parquet(folder_name, file_name):
    """
    Reads a Parquet file from a specified folder and returns a DataFrame.

    Parameters:
        folder_name (str): Name of the folder containing the Parquet file.
        file_name (str): Name of the Parquet file, must end with .parquet extension.

    Returns:
        pd.DataFrame: A DataFrame containing the contents of the Parquet file.

    Raises:
        ValueError: If file_name does not end with .parquet extension.
        FileNotFoundError: If folder does not exist or file does not exist in the specified folder.
    """
    try:
        if not file_name.endswith('.parquet'):
            raise ValueError("File name must end with '.parquet' extension")
        
        current_dir = os.getcwd()   #gets the current working directory.
        parent_dir = os.path.dirname(current_dir)  #gets its parent directory.
        folder_path = os.path.join(parent_dir, folder_name)  #constructs the path to your target folder (inside parent directory).
        file_path = os.path.join(folder_path, file_name) #constructs the full path to your parquet file.

        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder '{folder_name}' does not exists")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File '{file_name}' not found in folder '{folder_name}'")

        df = pd.read_parquet(file_path, engine='pyarrow')
        return df
    
    except (FileNotFoundError, ValueError) as e:
        print(e)
        return pd.DataFrame()