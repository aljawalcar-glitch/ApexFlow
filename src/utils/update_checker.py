import urllib.request
import json
from config.version import VERSION

def check_for_updates():
    """
    Checks for updates from the GitHub repository and returns the status.
    Returns:
        (bool, str): A tuple containing (is_update_available, latest_version)
    """
    try:
        # Use the provided GitHub repository URL
        url = "https://api.github.com/repos/aljawalcar-glitch/ApexFlow/releases/latest"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("tag_name", "v0.0.0").lstrip('v')
            current_version = VERSION.lstrip('v')

            # Compare versions
            latest_v_tuple = tuple(map(int, latest_version.split('.')))
            current_v_tuple = tuple(map(int, current_version.split('.')))

            if latest_v_tuple > current_v_tuple:
                return (True, data.get("tag_name"))
            else:
                return (False, VERSION)

    except Exception as e:
        print(f"Error checking for updates: {e}")
        return (False, None)
