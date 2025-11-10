import os

def create_path(folder_name, file_name):
    """
    Returns the full path of a specified file from a given folder.

    Parameters:
        folder_name (str): Name of the folder containing the file.
        file_name (str): Name of the file to load from the folder.

    Returns:
        str: Full path to the file from a given folder,
             Create a folder with same name, if not exist.

    Example:
        >>> create_path('images', 'logo.png')
        '/path/to/current/directory/images/logo.png'
    """
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    folder_path = os.path.join(parent_dir, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, file_name)

    return file_path