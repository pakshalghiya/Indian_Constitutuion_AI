"""Script to download the Indian Constitution source files."""
import os
import sys
import requests
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to the path so we can import our app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()

# GitHub repository information
GITHUB_REPO = "prince-mishra/the-constitution-of-india"
GITHUB_RAW_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/master"

# List of parts and schedules to download
PARTS = [f"PART{i:02d}" for i in range(1, 23)]
# Special parts with 'A' suffix
SPECIAL_PARTS = ["PART04A", "PART09A", "PART09B", "PART14A"]
# Add special parts to the list of parts
PARTS.extend(SPECIAL_PARTS)

# List of schedules
SCHEDULES = [f"SCHEDULE{i:02d}" for i in range(1, 13)]

# Other files
OTHER_FILES = ["Preamble"]

def download_file(file_name, destination_path):
    """
    Download a file from the GitHub repository.
    
    Args:
        file_name (str): The name of the file to download
        destination_path (str): The path to download the file to
    
    Returns:
        bool: True if the download was successful, False otherwise
    """
    url = f"{GITHUB_RAW_BASE_URL}/{file_name}.txt"
    file_path = os.path.join(destination_path, f"{file_name}.txt")
    
    logger.info(f"Downloading {file_name}.txt to {file_path}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise an error if the download fails
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the file
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        logger.debug(f"Successfully downloaded {file_name}.txt")
        return True
    
    except Exception as e:
        logger.error(f"Error downloading {file_name}.txt: {e}")
        return False

def download_constitution(force=False):
    """
    Download the Indian Constitution source files.
    
    Args:
        force (bool): Whether to force download and overwrite existing files
    
    Returns:
        int: The number of files downloaded successfully
    """
    logger.info("Starting download of Indian Constitution source files...")
    
    # Get the destination path from settings
    destination_path = settings.CONSTITUTION_SOURCE_PATH
    
    # Create the destination directory if it doesn't exist
    os.makedirs(destination_path, exist_ok=True)
    
    # Check if the Preamble file already exists and skip download if it does
    if not force and os.path.exists(os.path.join(destination_path, "Preamble.txt")):
        logger.info("Constitution files already exist. Use force=True to redownload.")
        return 0
    
    # Create a list of all files to download
    all_files = PARTS + SCHEDULES + OTHER_FILES
    
    # Download the files using a thread pool
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(
            lambda file_name: download_file(file_name, destination_path),
            all_files
        ))
    
    # Count successful downloads
    successful_downloads = sum(results)
    logger.info(f"Successfully downloaded {successful_downloads} out of {len(all_files)} files")
    
    return successful_downloads

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Indian Constitution source files")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force download and overwrite existing files"
    )
    
    args = parser.parse_args()
    
    download_constitution(force=args.force) 