from PySide6.QtWidgets import QFileDialog

def browse_folder_simple(parent=None, title="Select Folder"):
    """
    A simple function to browse for a folder.
    """
    folder_path = QFileDialog.getExistingDirectory(
        parent,
        title,
    )
    return folder_path
